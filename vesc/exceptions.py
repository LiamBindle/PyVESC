
class VESCException(ValueError):
    pass


class DuplicateMessageID(Exception):
    pass

class NoMessageID(Exception):
    pass

class InvalidPayload(VESCException):
    pass


class CorruptPacket(VESCException):
    pass