from .base import VESCMessage


class SetDuty(metaclass=VESCMessage):
    id = 5
    fields = [
        ('duty', 'f')
    ]