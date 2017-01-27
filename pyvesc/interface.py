import pyvesc.packet.codec
import pyvesc.messages.base

def decode(buffer):
    msg_payload, consumed = pyvesc.packet.codec.unframe(buffer)
    if msg_payload:
        return pyvesc.messages.base.VESCMessage.unpack(msg_payload), consumed
    else:
        return None, consumed


def encode(msg):
    msg_payload = pyvesc.messages.base.VESCMessage.pack(msg)
    packet = pyvesc.packet.codec.frame(msg_payload)
    return packet
