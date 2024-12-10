from . import base
from .packet import codec


def decode(buffer, recv=True):
    """
    Decodes the next valid VESC message in a buffer.

    :param buffer: The buffer to attempt to parse from.
    :type buffer: bytes

    :return: PyVESC message, number of bytes consumed in the buffer. If nothing
             was parsed returns (None, 0).
    :rtype: `tuple`: (PyVESC message, int)
    """

    messages = []

    # return values
    unpacked_messages = []
    consumed_total = 0
    msg_payload_total = b''

    # multi-frame messages, loop until buffer is empty
    while len(buffer) > 0:
        msg_payload, consumed = codec.unframe(buffer)
        messages.append((msg_payload, consumed))
        buffer = buffer[consumed:]
        consumed_total += consumed
        msg_payload_total += msg_payload

    if len(messages) > 0:
        for msg_payload, consumed in messages:
            if msg_payload is not None:
                unpacked_messages.append((base.VESCMessage.unpack(msg_payload)))
            else:
                raise ValueError("Invalid message payload")
        # combine unpacked messages into one string if there is a string field
        # we use the first message to determine if there is a string field, they will all have the
        # same field data as they are just repeated messages
        string_field_name = None
        string_field_scalar = None

        if recv:
            field = 'recv_fields'
        else:
            field = 'send_fields'
        if hasattr(unpacked_messages[0], field):
            field_list = getattr(unpacked_messages[0], field)
            for i, f in enumerate(field_list):
                if 's' in f[1]:  # f1 is the formats (there is a '[send/recv]_field_formats attr, but cbf getting it)
                    # there is a string, get the field name
                    string_field_name = f[0]
                    # if there is a scalar field
                    if len(f) > 2:
                        string_field_scalar = field_list[i][2]

        if string_field_name is not None:
            # check if string is an ascii or bytes by looking at the string scalar. -1 is bytestring, None is ascii
            if string_field_scalar is None:
                message_res = "".join([getattr(unpacked_message, string_field_name) + "\n" for unpacked_message in unpacked_messages])
            elif string_field_scalar == -1:
                message_res = b"".join([getattr(unpacked_message, string_field_name) for unpacked_message in unpacked_messages])

        else:
            if len(unpacked_messages) == 1:
                message_res = unpacked_messages[0]
            else:
                raise ValueError("Don't currently support multiple message results from one field that aren't strings")

        return message_res, consumed_total, msg_payload_total
    else:
        return None, consumed_total, msg_payload_total


def encode(msg):
    """
    Encodes a PyVESC message to a packet. This packet is a valid VESC packet and
    can be sent to a VESC via your serial port.

    :param msg: Message to be encoded. All fields must be initialized.
    :type msg: PyVESC message

    :return: The packet.
    :rtype: bytes
    """
    msg_payload = base.VESCMessage.pack(msg)
    packet = codec.frame(msg_payload)
    return packet


def encode_request(msg_cls):
    """
    Encodes a PyVESC message for requesting a getter message. This function
    should be called when you want to request a VESC to return a getter
    message.

    :param msg_cls: The message type which you are requesting.
    :type msg_cls: pyvesc.messages.getters.[requested getter]

    :return: The encoded PyVESC message which can be sent.
    :rtype: bytes
    """
    msg_payload = base.VESCMessage.pack(msg_cls, header_only=True)
    packet = codec.frame(msg_payload)
    return packet
