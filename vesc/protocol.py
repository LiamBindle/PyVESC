import asyncio
import logging
from .packet import Footer
from .codec import encode
from .codec import decode


class Protocol(asyncio.Protocol):
    def __init__(self, callback):
        self.callback = callback

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
            payload, consumed = decode(self.buffer)
            self.buffer = self.buffer[consumed:]
            if payload:
                self.callback(payload)
