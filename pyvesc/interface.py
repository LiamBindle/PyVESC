import pyvesc.packet.codec
import pyvesc.messages.base

def decode(buffer):
    """
    Decodes the next valid VESC message in a buffer.

    :param buffer: The buffer to attempt to parse from.
    :type buffer: bytes

    :return: PyVESC message, number of bytes consumed in the buffer. If nothing
             was parsed returns (None, 0).
    :rtype: `tuple`: (PyVESC message, int)
    """
    msg_payload, consumed = pyvesc.packet.codec.unframe(buffer)
    if msg_payload:
        return pyvesc.messages.base.VESCMessage.unpack(msg_payload), consumed
    else:
        return None, consumed


def encode(msg):
    """
    Encodes a PyVESC message to a packet. This packet is a valid VESC packet and
    can be sent to a VESC via your serial port.

    :param msg: PyVESC message to be encoded. All fields must be initialized.
    :return: The packet.
    :rtype: bytes
    """
    msg_payload = pyvesc.messages.base.VESCMessage.pack(msg)
    packet = pyvesc.packet.codec.frame(msg_payload)
    return packet
