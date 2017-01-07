from .packet import Stateless
from .msg import Msg
import codecs


def encode(vesc_msg, errors='ignore'):
    """
    Encodes a VESC message.
    :param vesc_message: messages.msg object for the desired message.
    :param errors: Error handling scheme. See codec error handling schemes.
    :return: data packet as a byte string
    """
    return Stateless.pack(vesc_msg.pack(), errors)


def decode(buffer, errors='ignore'):
    """
    Decodes a VESC message from a buffer.
    :param buffer: Buffer object.
    :param errors: Error handling scheme. See codec error handling schemes.
    :return: The VESC message
    """
    payload, consumed = Stateless.unpack(buffer, errors)
    return Msg.unpack(payload), consumed

vesc_codec = codecs.CodecInfo(encode, decode, None, None, None, None, 'vesc-msg')

def vesc_search_function(name_lower):
    if name_lower is 'vesc-msg':
        return vesc_codec
    else:
        return None

codecs.register(vesc_search_function)
