#!/usr/bin/env python
# coding: utf-8



from pyvesc.VESC import MultiVESC
import time
import numpy as np




class MobileBase:
    def __init__(
        self, 
        serial_port='/dev/ttyACM0',
        left_wheel_id=102,
        right_wheel_id=127,
        back_wheel_id=None, 
        ) -> None:

        params = [
            {'can_id': left_wheel_id, 'has_sensor': True, 'start_heartbeat': True},
            {'can_id': right_wheel_id, 'has_sensor': True, 'start_heartbeat': True},
            {'can_id': back_wheel_id, 'has_sensor': True, 'start_heartbeat': True},
        ]
        self._multi_vesc = MultiVESC(serial_port=serial_port, vescs_params=params)

        self.left_wheel, self.right_wheel, self.back_wheel = self._multi_vesc.controllers




omnibase = MobileBase()

time.sleep(0.1)
t = time.time()
print("go")
omnibase.left_wheel.set_duty_cycle(0.2)
omnibase.back_wheel.set_duty_cycle(0.2)
omnibase.right_wheel.set_duty_cycle(0.2)


while((time.time() - t) < 2.0):
    # omnibase.back_wheel.set_duty_cycle(0.2)
    # omnibase.left_wheel.set_duty_cycle(0.2)
    pass

omnibase.left_wheel.set_duty_cycle(-0.2)
omnibase.back_wheel.set_duty_cycle(-0.2)
omnibase.right_wheel.set_duty_cycle(-0.2)
time.sleep(2.0)
print("stop")
omnibase.back_wheel.set_duty_cycle(0.0)
omnibase.left_wheel.set_duty_cycle(0.0)
omnibase.right_wheel.set_duty_cycle(0.0)


# omnibase.right_wheel.set_duty_cycle(cycle_from_joystick(J)[1])

