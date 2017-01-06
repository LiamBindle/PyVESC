
class VESCException(ValueError):
    pass


class InvalidPayload(VESCException):
    pass


class CorruptPacket(VESCException):
    pass