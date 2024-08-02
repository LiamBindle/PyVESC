from .protocol.interface import encode_request, encode, decode
from .messages.getters import GetVersion, GetMotorConfig, GetAppConfig, GetValues
from .messages.setters import (
    SetMotorConfig, SetAppConfig, SetRPM, SetCurrent, SetDutyCycle,
    SetServoPosition, EraseNewApp, WriteNewAppData, WriteNewAppDataLZO,
    JumpToBootloader, TerminalCmd, SetRotorPositionMode, Reboot, alive_msg
)
import time
import threading
import logging


logger = logging.getLogger(__name__)

# because people may want to use this library for their own messaging, do not make this a required package
try:
    import serial
except ImportError:
    serial = None

read_lock = threading.Lock()


class VESC(object):
    def __init__(self, serial_port, has_sensor=False, start_heartbeat=True, baudrate=115200, timeout=0.05):
        """
        :param serial_port: Serial device to use for communication (i.e. "COM3" or "/dev/tty.usbmodem0")
        :param has_sensor: Whether or not the bldc motor is using a hall effect sensor
        :param start_heartbeat: Whether or not to automatically start the heartbeat thread that will keep commands
                                alive.
        :param baudrate: baudrate for the serial communication. Shouldn't need to change this.
        :param timeout: timeout for the serial communication
        """

        if serial is None:
            raise ImportError("Need to install pyserial in order to use the VESCMotor class.")

        self.serial_port = serial.Serial(port=serial_port, baudrate=baudrate, timeout=timeout)
        if has_sensor:
            self.serial_port.write(encode(SetRotorPositionMode(SetRotorPositionMode.DISP_POS_OFF)))

        self.heart_beat_thread = threading.Thread(target=self._heartbeat_cmd_func)
        self._stop_heartbeat = threading.Event()

        if start_heartbeat:
            self.start_heartbeat()

        self._message_monitor_thread = threading.Thread(target=self._message_monitor)

        # thread to monitor messages to receive unscheuled prints from ESC for debugging,
        # currently disabled as it was interfering sometimes and is not needed
        self._stop_message_monitor = threading.Event()
        # self._message_monitor_thread.start()

        # store message info for getting values so it doesn't need to calculate it every time
        msg = GetValues()
        self._get_values_msg = encode_request(msg)
        self._get_values_msg_expected_length = msg._recv_full_msg_size

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_heartbeat()
        try:
            if self.serial_port.is_open:
                self.serial_port.flush()
                self.serial_port.close()
        except Exception as e:
            logging.error("Error closing serial port: ", e)
            logging.error("This is likely due to the motor being disconnected before the connection could be closed.")

    def _message_monitor(self):
        """
        A function that continuously reads the serial port for messages and decodes them.
        """
        while not self._stop_message_monitor.isSet():
            ret = self.read(1, expect_string=True, expect_anything=False)
            if ret is not None:
                print(ret)
            time.sleep(0.01)

    def _heartbeat_cmd_func(self):
        """
        Continuous function calling that keeps the motor alive
        """
        while not self._stop_heartbeat.isSet():
            time.sleep(0.1)
            self.write(alive_msg, is_heartbeat=True)

    def start_heartbeat(self):
        """
        Starts a repetitive calling of the last set cmd to keep the motor alive.
        """
        self.heart_beat_thread.start()

    def stop_heartbeat(self):
        """
        Stops the heartbeat thread and resets the last cmd function. THIS MUST BE CALLED BEFORE THE OBJECT GOES OUT OF
        SCOPE UNLESS WRAPPING IN A WITH STATEMENT (Assuming the heartbeat was started).
        """
        if self.heart_beat_thread.is_alive():
            try:
                self._stop_heartbeat.set()
                self.heart_beat_thread.join()
            except Exception as e:
                logger.error("Error stopping heartbeat: {}".format(e))

    def write(self, data, num_read_bytes=None, is_heartbeat=False, expect_string=False):
        """
        A write wrapper function implemented like this to try and make it easier to incorporate other communication
        methods than UART in the future.
        :param data: the byte string to be sent
        :param num_read_bytes: number of bytes to read for decoding response
        :param is_heartbeat: whether or not this is a heartbeat message, can be used for filtering debug prints
        :param expect_string: whether or not to expect a string response
        :param expect_anything: whether or not to expect any response
        :return: decoded response from buffer
        """
        try:
            self.serial_port.write(data)
        except Exception as e:
            logging.error("Error writing to serial port: ", e)
        if not is_heartbeat:
            logging.debug("Data sent: {}".format(data))
        if num_read_bytes is not None:
            return self.read(num_read_bytes, expect_string=expect_string)

    def read(self, num_read_bytes, timeout=0.01, expect_string=False, expect_anything=True):
        response = None
        payload = b''
        last_payload_len = 0
        t_start = None

        # allow more time for parsing string of unknown length
        if expect_string:
            timeout = 0.1

        with read_lock:
            while True:
                time.sleep(0.01)

                # first data received
                if len(payload) > 0 and last_payload_len == 0 or len(payload) > 0 and t_start is None:
                    t_start = time.time()

                # if data stops for a long time
                if last_payload_len == len(payload):
                    if t_start is not None:
                        if time.time() - t_start > timeout:
                            break

                # read in data gradually to ensure buffer doesn't fill
                payload += self.serial_port.read(self.serial_port.in_waiting)

                last_payload_len = len(payload)

                # if we are just probing the serial line, exit early as we are not waiting for a response
                if len(payload) == 0 and not expect_anything:
                    return None

        response, consumed, msg_payload = decode(payload, recv=True)
        logging.debug("Data response: {}".format(msg_payload))
        return response

    def update_firmware(self, firmware, progress_callback=None):

        logging.info("Erasing")

        erase_res = self.fw_erase_new_app(firmware.size)
        if erase_res.erase_new_app_result != 1:
            logging.error("Erase failed")
            progress_callback("Erase Failed")
            return False

        logging.info("Sending firmware")

        offset = 0
        time_since_last_progress_update = time.time()

        while firmware.size > 0:
            fw_chunk = firmware.get_next_chunk()

            # check if the chunk is empty, don't send
            has_data = False
            for i in fw_chunk:
                if i != 0xff:
                    has_data = True
                    break

            if has_data:
                fw_result = self.fw_write_new_app_data(offset, fw_chunk)

                if fw_result.write_new_app_result != 1 or fw_result.write_new_app_result is None:
                    logging.error("Write failed")
                    logging.error(fw_result)
                    progress_callback("Flashing Failed")
                    return False

            offset += firmware.chunk_size

            UPDATE_INTERVAL_SECS = 10
            if time.time() - time_since_last_progress_update > UPDATE_INTERVAL_SECS:
                time_since_last_progress_update = time.time()
                logging.info(
                    "Progress: {:.2f}%, Size: {}/{}kB".format(firmware.get_progress(offset), offset, firmware.original_size))
                if progress_callback is not None:
                    progress_callback(int(firmware.get_progress(offset)))

            # stream updates quickly to stdout
            print("\rProgress: {:.2f}%, Size: {}kB, to be written to {}".format(
                firmware.get_progress(offset), offset, offset + firmware.chunk_size), end='\r')
            firmware.clear_chunk()

        logging.info("Firmware upload complete, jumping to bootloader.")
        try:
            self.fw_jump_to_bootloader()
        except Exception as e:
            logging.error(
                "Error jumping to bootloader, this is likely the motor rebooting before a connection could be closed: {}".format(e))

        return True

    def set_rpm(self, new_rpm):
        """
        Set the electronic RPM value (a.k.a. the RPM value of the stator)
        :param new_rpm: new rpm value
        """
        self.write(encode(SetRPM(new_rpm)))

    def set_current(self, new_current):
        """
        :param new_current: new current in milli-amps for the motor
        """
        self.write(encode(SetCurrent(new_current)))

    def set_duty_cycle(self, new_duty_cycle):
        """
        :param new_duty_cycle: Value of duty cycle to be set (range [-1e5, 1e5]).
        """
        self.write(encode(SetDutyCycle(new_duty_cycle)))

    def set_servo(self, new_servo_pos):
        """
        :param new_servo_pos: New servo position. valid range [0, 1]
        """
        self.write(encode(SetServoPosition(new_servo_pos)))

    def get_measurements(self):
        """
        :return: A msg object with attributes containing the measurement values
        """
        return self.write(self._get_values_msg, num_read_bytes=self._get_values_msg_expected_length)

    def get_firmware_version(self):
        msg = GetVersion()
        return self.write(encode_request(msg), num_read_bytes=msg._recv_full_msg_size)

    def get_rpm(self):
        """
        :return: Current motor rpm
        """
        return self.get_measurements().rpm

    def get_duty_cycle(self):
        """
        :return: Current applied duty-cycle
        """
        return self.get_measurements().duty_now

    def get_v_in(self):
        """
        :return: Current input voltage
        """
        return self.get_measurements().v_in

    def get_motor_current(self):
        """
        :return: Current motor current
        """
        return self.get_measurements().current_motor

    def get_incoming_current(self):
        """
        :return: Current incoming current
        """
        return self.get_measurements().current_in

    def fw_erase_new_app(self, fw_size):
        """
        Erase app data
        """
        # TODO: Revert this to actual fw size
        msg = EraseNewApp(fw_size)
        return self.write(encode(msg), num_read_bytes=msg._recv_full_msg_size)

    def reboot(self):
        """
        Reboot VESC
        """
        msg = Reboot()
        return str(self.write(encode_request(msg), num_read_bytes=msg._recv_full_msg_size))

    def fw_write_new_app_data(self, offset, data):
        """
        Write new app data
        """
        msg = WriteNewAppData(offset, data)
        return self.write(encode(msg), num_read_bytes=msg._recv_full_msg_size)

    def fw_write_new_app_data_lzo(self, offset, data):
        """
        Write new app data
        """
        msg = WriteNewAppDataLZO(offset, data)
        return self.write(encode(msg), num_read_bytes=msg._recv_full_msg_size)

    def fw_jump_to_bootloader(self):
        """
        Jump to bootloader
        set number of read bytes to None as we don't expect a response
        """
        msg = JumpToBootloader()
        # stop heartbeat, as we are about to reset the device
        self.stop_heartbeat()

        return self.write(encode_request(msg), num_read_bytes=None)

    def send_terminal_cmd(self, cmd):
        """
        Send terminal command
        """
        msg = TerminalCmd(cmd)
        return self.write(encode(msg), num_read_bytes=msg._recv_full_msg_size, expect_string=True)

    def get_motor_configuration(self):
        """
        Get the motor configuration parameters
        """
        msg = GetMotorConfig()
        res = self.write(encode(msg), num_read_bytes=msg._recv_full_msg_size, expect_string=True)
        return res

    def set_motor_configuration(self, data):
        """
        Set the motor configuration parameters
        """
        msg = SetMotorConfig(data)
        res = self.write(encode(msg), num_read_bytes=msg._recv_full_msg_size, expect_string=True)
        return res

    def get_app_configuration(self):
        """
        Get the app configuration parameters
        """
        msg = GetAppConfig()
        res = self.write(encode(msg), num_read_bytes=msg._recv_full_msg_size, expect_string=True)
        return res

    def set_app_configuration(self, data):
        """
        Set the app configuration parameters
        """
        msg = SetAppConfig(data)
        res = self.write(encode(msg), num_read_bytes=msg._recv_full_msg_size, expect_string=True)
        return res
