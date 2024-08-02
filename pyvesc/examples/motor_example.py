from pyvesc.firmware import Firmware
from pyvesc.VESC import VESC
from pyvesc.params import confgenerator
import time
import logging
import argparse
import json

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%m-%y %H:%M:%S', level=logging.INFO)
console = logging.StreamHandler()
logger.addHandler(console)


# a function to show how to use the class with a with-statement
def run_motor_using_with(serial_port):
    with VESC(serial_port=serial_port) as motor:
        print("Firmware: ", motor.get_firmware_version())
        motor.set_duty_cycle(.02)

        # run motor and print out rpm for ~2 seconds
        for i in range(30):
            time.sleep(0.1)
            print(motor.get_measurements().rpm)
        motor.set_rpm(0)


# a function to show how to use the class as a static object.
def run_motor_as_object(serial_port):
    motor = VESC(serial_port=serial_port)
    print("Firmware: ", motor.get_firmware_version())

    # sweep servo through full range
    for i in range(100):
        time.sleep(0.01)
        motor.set_servo(i / 100)

    # IMPORTANT: YOU MUST STOP THE HEARTBEAT IF IT IS RUNNING BEFORE IT GOES OUT OF SCOPE. Otherwise, it will not
    #            clean-up properly.
    motor.stop_heartbeat()


def time_get_values(serial_port):
    with VESC(serial_port=serial_port) as motor:
        start = time.time()
        motor.get_measurements()
        stop = time.time()
        print("Getting values takes ", stop - start, "seconds.")


def commands_example(port, firmware, compressed):
    """
    Example of using the terminal commands with some additional commands defined here which allow erase and firmware updates
    """

    with VESC(serial_port=port) as motor:
        print(motor.send_terminal_cmd("hw_status"))

        print("\nAll VESC commands are supported, plus the following:")
        print("fw\t\t- update firmware")
        print("erase\t\t- erase firmware ")
        print("\n\nEntering Terminal:\n====================\n")
        print("\n\n")

        while True:
            # terminal console that reads in text on a newline, assigns it to the user_in string
            user_in = input("")
            if user_in == "fw":
                if firmware is None:
                    print("No firmware file specified")
                    continue
                fw = Firmware(firmware, lzss=compressed)
                motor.update_firmware(fw)
                logging.info("This script will exit as it doesn't handle serial ports reconnecting yet.")
                break

            if user_in == "erase":
                print("sending erase")
                erase_res = motor.fw_erase_new_app(fw.size)
                print("Erase status:", erase_res.erase_new_app_result)
                break

            print(motor.send_terminal_cmd(user_in))


def save_parameters(serial_port, save_file):
    with VESC(serial_port=serial_port) as motor:
        motor_config_bytes = motor.get_motor_configuration()
        app_config_bytes = motor.get_app_configuration()
        mcconfig = confgenerator.confgenerator_deserialise_mcconf(bytearray(motor_config_bytes), None)
        appconfig = confgenerator.confgenerator_deserialise_appconf(bytearray(app_config_bytes), None)

        # convert to dictionary
        # TODO: add datatype to the dictionary
        mcconfig_dict = [{param.name: param.value} for param in mcconfig]
        appconfig_dict = [{param.name: param.value} for param in appconfig]

        output = {"mcconfig": mcconfig_dict, "appconfig": appconfig_dict}

        # convert to json
        config_json = json.dumps(output, indent=4)
        print(config_json)

        # save the parameters to a file
        with open(save_file, 'wb') as f:
            f.write(config_json.encode('utf-8'))


def load_parameters(serial_port, load_file):
    with VESC(serial_port=serial_port) as motor:
        with open(load_file, 'rb') as f:
            config_json = f.read()

        config = json.loads(config_json)

        mcconfig = []
        for param in config['mcconfig']:
            name, value = list(param.items())[0]
            mcconfig.append(confgenerator.confgenerator_param_from_dict(name, value))

        appconfig = []
        for param in config['appconfig']:
            name, value = list(param.items())[0]
            appconfig.append(confgenerator.confgenerator_param_from_dict(name, value))

        mcconfig_bytes = confgenerator.confgenerator_serialise_mcconf(mcconfig)
        appconfig_bytes = confgenerator.confgenerator_serialise_appconf(appconfig)

        motor.set_motor_configuration(mcconfig_bytes)
        motor.set_app_configuration(appconfig_bytes)


if __name__ == '__main__':
    # arguments
    parser = argparse.ArgumentParser(description='VESC Motor Example')
    parser.add_argument('-p', '--port', type=str, help='Serial port', default='')
    parser.add_argument('-f', '--firmware', type=str, help='Firmware file', default=None)
    parser.add_argument('-c', '--compressed', action='store_true', help='Compressed firmware', default=True)
    parser.add_argument('-s', '--save', type=str, help='Save parameters to file', default=None)
    parser.add_argument('-l', '--load', type=str, help='Load parameters from file', default=None)
    args = parser.parse_args()

    if args.save:
        save_parameters(serial_port=args.port, save_file=args.save)

    if args.load:
        load_parameters(serial_port=args.port, load_file=args.load)

    # run_motor_using_with(args.port)
    # run_motor_as_object(args.port)
    # time_get_values(args.port)
    commands_example(args.port, args.firmware, args.compressed)
