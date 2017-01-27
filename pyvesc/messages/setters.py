from .base import VESCMessage


class SetDutyCycle(metaclass=VESCMessage):
    id = 5
    fields = [
        ('duty_cycle', 'f')
    ]


class SetRPM(metaclass=VESCMessage):
    id = 8
    fields = [
        ('rpm', 'i')
    ]


class SetCurrent(metaclass=VESCMessage):
    id = 6
    fields = [
        ('current', 'f')
    ]


class SetCurrentBrake(metaclass=VESCMessage):
    id = 7
    fields = [
        ('current_brake', 'f')
    ]
