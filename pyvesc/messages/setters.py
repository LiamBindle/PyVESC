from ..protocol.base import VESCMessage
from ..protocol.interface import encode
from .Vedder_BLDC_Commands import VedderCmd


class SetDutyCycle(metaclass=VESCMessage):
    """ Set the duty cycle.

    :ivar duty_cycle: Value of duty cycle to be set (range [-1e5, 1e5]).
    """
    id = VedderCmd.COMM_SET_DUTY
    send_fields = [
        ('duty_cycle', 'i', 100000)
    ]


class SetMotorConfig(metaclass=VESCMessage):
    """
    Set the motor configuration values

    Sends a bytestring, so scalar is set to -1 to represent this
    """
    id = VedderCmd.COMM_SET_MCCONF

    send_fields = [
        ('mcconf', 's', -1)
    ]


class SetAppConfig(metaclass=VESCMessage):
    """
    Set the app configuration values

    Sends a bytestring, so scalar is set to -1 to represent this
    """
    id = VedderCmd.COMM_SET_APPCONF

    send_fields = [
        ('appconf', 's', -1)
    ]


class SetRPM(metaclass=VESCMessage):
    """ Set the RPM.

    :ivar rpm: Value to set the RPM to.
    """
    id = VedderCmd.COMM_SET_RPM
    send_fields = [
        ('rpm', 'i')
    ]


class SetCurrent(metaclass=VESCMessage):
    """ Set the current (in milliamps) to the motor.

    :ivar current: Value to set the current to (in milliamps).
    """
    id = VedderCmd.COMM_SET_CURRENT
    send_fields = [
        ('current', 'i', 1000)
    ]


class SetCurrentBrake(metaclass=VESCMessage):
    """ Set the current brake (in milliamps).

    :ivar current_brake: Value to set the current brake to (in milliamps).
    """
    id = VedderCmd.COMM_SET_CURRENT_BRAKE
    send_fields = [
        ('current_brake', 'i', 1000)
    ]


class SetPosition(metaclass=VESCMessage):
    """Set the rotor angle based off of an encoder or sensor

    :ivar pos: Value to set the current position or angle to.
    """
    id = VedderCmd.COMM_SET_POS
    send_fields = [
        ('pos', 'i', 1000000)
    ]


class SetRotorPositionMode(metaclass=VESCMessage):
    """ Sets the rotor position feedback mode.
    It is reccomended to use the defined modes as below:
        * DISP_POS_OFF
        * DISP_POS_MODE_ENCODER
        * DISP_POS_MODE_PID_POS
        * DISP_POS_MODE_PID_POS_ERROR

    :ivar pos_mode: Value of the mode
    """

    DISP_POS_OFF = 0
    DISP_POS_MODE_ENCODER = 3
    DISP_POS_MODE_PID_POS = 4
    DISP_POS_MODE_PID_POS_ERROR = 5

    id = VedderCmd.COMM_SET_DETECT
    send_fields = [
        ('pos_mode', 'b')
    ]


class SetServoPosition(metaclass=VESCMessage):
    """Sets the position of s servo connected to the VESC.

    :ivar servo_pos: Value of position (range [0, 1])
    """

    id = VedderCmd.COMM_SET_SERVO_POS
    send_fields = [
        ('servo_pos', 'h', 1000)
    ]


class Reboot(metaclass=VESCMessage):
    """Reboot the VESC"""
    id = VedderCmd.COMM_REBOOT
    send_fields = []


class Alive(metaclass=VESCMessage):
    """Heartbeat signal to keep VESC alive"""
    id = VedderCmd.COMM_ALIVE
    send_fields = []


class EraseNewApp(metaclass=VESCMessage):
    """Erase the flash area on the VESC which stores the new APP, get response"""
    id = VedderCmd.COMM_ERASE_NEW_APP
    send_fields = [
        ('data', 'I')
    ]
    recv_fields = [
        ('erase_new_app_result', 'b', 0)
    ]


class WriteNewAppData(metaclass=VESCMessage):
    """Write the new APP data to the VESC, get response
       write_new_app_data_result = 0 if failed, 1 if successful
    """
    id = VedderCmd.COMM_WRITE_NEW_APP_DATA
    send_fields = [
        ('offset', 'I'),
        ('data', f'{384}s')
    ]
    recv_fields = [
        ('write_new_app_result', '?', 0),
        ('new_app_offset', 'I', 0)
    ]


class WriteNewAppDataLZO(metaclass=VESCMessage):
    """Write the new APP data to the VESC, get response
       write_new_app_data_result = 0 if failed, 1 if successful

       This is a clone of WriteNewAppData, but with a different id to indicate that the data is compressed with LZO
       and the VESC is required to decompress
    """
    id = VedderCmd.COMM_WRITE_NEW_APP_DATA_LZO
    send_fields = [
        ('offset', 'I'),
        ('data', f'{384}s')
    ]
    recv_fields = [
        ('write_new_app_result', '?', 0),
        ('new_app_offset', 'I', 0)
    ]


class JumpToBootloader(metaclass=VESCMessage):
    """Jump to the bootloader, get response
       jump_to_bootloader_result = 0 if failed, 1 if successful
    """
    id = VedderCmd.COMM_JUMP_TO_BOOTLOADER
    send_fields = []
    recv_fields = []


class TerminalCmd(metaclass=VESCMessage):
    """Send a terminal command to the VESC, get response"""
    id = VedderCmd.COMM_TERMINAL_CMD
    send_fields = [
        ('cmd', 's')
    ]
    recv_fields = [
        ('terminal_cmd_result', 's')
    ]


class TerminalPrint(metaclass=VESCMessage):
    """Print a message to the terminal"""
    id = VedderCmd.COMM_PRINT
    recv_fields = [
        ('msg', 's')
    ]


# statically save this message because it does not need to be recalculated
alive_msg = encode(Alive())
