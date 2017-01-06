"""
This file declares all message id's and formats. Most of these are simply hand copied from bldc_interface.
"""
import enum
import struct
import collections

@enum.unique
class msg_id(enum.Enum):
    fw_version                     = 0
    jump_to_bootloader             = 1
    erase_new_app                  = 2
    write_new_app_data             = 3
    get_values                     = 4
    set_duty                       = 5
    set_current                    = 6
    set_current_brake              = 7
    set_rpm                        = 8
    set_pos                        = 9
    set_detect                     = 10
    set_servo_pos                  = 11
    set_mcconf                     = 12
    get_mcconf                     = 13
    get_mcconf_default             = 14
    set_appconf                    = 15
    get_appconf                    = 16
    get_appconf_default            = 17
    sample_print                   = 18
    terminal_cmd                   = 19
    print                          = 20
    rotor_position                 = 21
    experiment_sample              = 22
    detect_motor_param             = 23
    detect_motor_r_l               = 24
    detect_motor_flux_linkage      = 25
    detect_encoder                 = 26
    detect_hall_foc                = 27
    reboot                         = 28
    alive                          = 29
    get_decoded_ppm                = 30
    get_decoded_adc                = 31
    get_decoded_chuk               = 32
    forward_can                    = 33
    set_chuck_data                 = 34
    custom_app_data                = 35

msg_fmt = {
    # Setters
    msg_id.terminal_cmd : '',
    msg_id.set_duty : '',
    msg_id.set_current : '',
    msg_id.set_current_brake : '',
    msg_id.set_rpm : 'i',
    msg_id.set_pos : '',
    msg_id.set_servo_pos : '',
    msg_id.set_mcconf : '',
    msg_id.set_appconf : '',

    # Getters
    msg_id.fw_version : '',
    msg_id.get_values : '',
    msg_id.get_mcconf : '',
    msg_id.get_appconf : '',
    msg_id.get_decoded_ppm : '',
    msg_id.get_decoded_adc : '',
    msg_id.get_decoded_chuk : '',

    # Other functions
    msg_id.detect_motor_param : '',
    msg_id.reboot : '',
    msg_id.alive : '',
}


msg = collections.namedtuple('msg', 'id vargs_tuple')


def generate_payload(message):
    """
    Converts a message to a byte string.
    :param message: The message to be written.
    :return: byte string
    """
    return struct.pack('<B' + msg_fmt[message.id], message.id, *message.vargs_tuple)


