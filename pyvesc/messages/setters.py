from pyvesc.messages.base import VESCMessage

class SetDutyCycle(metaclass=VESCMessage):
    """ Set the duty cycle.

    :ivar duty_cycle: Value of duty cycle to be set.
    """
    id = 5
    fields = [
        ('duty_cycle', 'f')
    ]


class SetRPM(metaclass=VESCMessage):
    """ Set the RPM.

    :ivar rpm: Value to set the RPM to.
    """
    id = 8
    fields = [
        ('rpm', 'i')
    ]


class SetCurrent(metaclass=VESCMessage):
    """ Set the current to the motor.

    :ivar current: Value to set the current to.
    """
    id = 6
    fields = [
        ('current', 'f')
    ]


class SetCurrentBrake(metaclass=VESCMessage):
    """ Set the current brake.

    :ivar current_brake: Value to set the current brake to.
    """
    id = 7
    fields = [
        ('current_brake', 'f')
    ]
