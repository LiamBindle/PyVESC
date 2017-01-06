import asyncio

class Protocol(asyncio.BaseProtocol):
    def connection_made(self, transport):
        raise NotImplementedError

    def connection_lost(self, exc):
        raise NotImplementedError

    def data_received(self, data):
        raise NotImplementedError

    def eof_received(self):
        raise NotImplementedError

    def pause_writing(self):
        raise NotImplementedError

    def resume_writing(self):
        raise NotImplementedError
