#!/usr/bin/env python
# coding: utf-8

from pyvesc.VESC import MultiVESC
import pygame
import time
import numpy as np

# infos : https://vesc-project.com/node/336


class MobileBase:
    def __init__(
        self,
        serial_port='/dev/ttyACM0',
        left_wheel_id=24,
        right_wheel_id=72,
        back_wheel_id=None,
    ) -> None:

        params = [
            {'can_id': left_wheel_id, 'has_sensor': True, 'start_heartbeat': True},
            {'can_id': right_wheel_id, 'has_sensor': True, 'start_heartbeat': True},
            {'can_id': back_wheel_id, 'has_sensor': True, 'start_heartbeat': True},
        ]
        self._multi_vesc = MultiVESC(
            serial_port=serial_port, vescs_params=params)

        self.left_wheel, self.right_wheel, self.back_wheel = self._multi_vesc.controllers


omnibase = MobileBase()

# omnibase.back_wheel.set_duty_cycle(0.1)
# omnibase.left_wheel.set_duty_cycle(0.1)
# omnibase.right_wheel.set_duty_cycle(0.1)

# time.sleep(0.5)

print("Breaking with duty_cycle=0")
omnibase.back_wheel.set_duty_cycle(0.0)
omnibase.left_wheel.set_duty_cycle(0.0)
omnibase.right_wheel.set_duty_cycle(0.0)
time.sleep(3.0)

print("Breaking with rpm=0")
omnibase.back_wheel.set_rpm(0)
omnibase.left_wheel.set_rpm(0)
omnibase.right_wheel.set_rpm(0)
time.sleep(3.0)


print("Releasing")
omnibase.back_wheel.set_current(0)
omnibase.left_wheel.set_current(0)
omnibase.right_wheel.set_current(0)
# t = time.time()
# while (time.time()-t) < 3.0:
#     # omnibase.back_wheel.set_rpm(0)
#     # omnibase.left_wheel.set_rpm(0)
#     # omnibase.right_wheel.set_rpm(0)
#     omnibase.back_wheel.set_current(0)
#     omnibase.left_wheel.set_current(0)
#     omnibase.right_wheel.set_current(0)

time.sleep(2)
# t = time.time()
# while (time.time()-t) < 3.0:
#     omnibase.back_wheel.set_duty_cycle(0)
#     omnibase.left_wheel.set_duty_cycle(0)
#     omnibase.right_wheel.set_duty_cycle(0)
print("End")
