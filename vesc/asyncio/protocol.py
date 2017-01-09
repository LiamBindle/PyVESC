import asyncio
import logging
from ..packet.codec import encode as encode_packet
from ..packet.codec import decode as decode_packet
from ..packet.codec import Footer
from ..messages.base import VESCMessage


class VESCProtocol(asyncio.Protocol):
    def __init__(self, recv_callback):
        self.recv_callback = recv_callback
        self.buffer = None
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        self.buffer = bytearray()
        logging.info('Port opened: ', self.transport)

    def connection_lost(self, exc):
        logging.info('Port closed: ', self.transport)
        self.transport = None
        self.buffer = None

    def data_received(self, data):
        self.buffer.extend(data)
        # if the terminator is in data, attempt to parse the packet
        if Footer.TERMINATOR in data:
            msg_bytes, consumed = decode_packet(self.buffer)
            self.buffer = self.buffer[consumed:]
            if msg_bytes:
                self.recv_callback(self, VESCMessage.decode(msg_bytes))

    def write(self, msg):
        payload_bytes = VESCMessage.encode(msg)
        packet = encode_packet(payload_bytes)
        self.transport.write(packet)
