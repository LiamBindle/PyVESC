#!/usr/bin/env python
# coding: utf-8

from pyvesc.VESC import MultiVESC
import pygame
import time
import numpy as np


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


def cycle_from_joystick(joystick):
    factor = 1.0
    cycle_max_t = 0.2*factor
    cycle_max_r = 0.1*factor
    print(joystick.get_axis(1))
    y = -joystick.get_axis(1) * cycle_max_t
    x = joystick.get_axis(0) * cycle_max_t
    rot = -joystick.get_axis(3) * cycle_max_r

    cycle_back = x + rot
    cycle_right = (x*np.cos(120*np.pi/180)) + (y*np.sin(120*np.pi/180)) + rot
    cycle_left = (x*np.cos(240*np.pi/180)) + (y*np.sin(240*np.pi/180)) + rot

    #print(cycle_back, cycle_left, cycle_right)

    return (cycle_back), (cycle_right), (cycle_left)


omnibase = MobileBase()

pygame.init()
pygame.joystick.init()

J = pygame.joystick.Joystick(0)

while True:
    for event in pygame.event.get():
        pass

    time.sleep(0.1)
    omnibase.back_wheel.set_duty_cycle(cycle_from_joystick(J)[0])
    omnibase.left_wheel.set_duty_cycle(cycle_from_joystick(J)[2])
    omnibase.right_wheel.set_duty_cycle(cycle_from_joystick(J)[1])
