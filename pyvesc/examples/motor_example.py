from pyvesc import VESCMotor
import time

# serial port that VESC is connected to. Something like "COM3" for windows and as below for linux/mac
serial_port = '/dev/tty.usbmodem301'


# a function to show how to use the class with a with-statement
def run_motor_using_with():
    with VESCMotor(serial_port=serial_port) as motor:
        print("Firmware: ", motor.get_firmware_version())
        motor.set_rpm(5000)

        # run motor and print out rpm for ~2 seconds
        for i in range(20):
            time.sleep(0.1)
            print(motor.get_measurements().rpm)
        motor.set_rpm(0)


# a function to show how to use the class as a static object.
def run_motor_as_object():
    motor = VESCMotor(serial_port=serial_port)
    print("Firmware: ", motor.get_firmware_version())
    motor.set_rpm(5000)

    # run motor and print out rpm for ~2 seconds
    for _ in range(20):
        time.sleep(0.1)
        print(motor.get_measurements().rpm)
    motor.set_rpm(0)

    # IMPORTANT: YOU MUST STOP THE HEARTBEAT IF IT IS RUNNING BEFORE IT GOES OUT OF SCOPE. Otherwise, it will not
    #            clean-up properly.
    motor.stop_heartbeat()


def time_get_values():
    with VESCMotor(serial_port=serial_port) as motor:
        start = time.time()
        motor.get_measurements()
        stop = time.time()
        print("Getting values takes ", stop-start, "seconds.")


if __name__ == '__main__':
    run_motor_using_with()
    run_motor_as_object()
    time_get_values()

