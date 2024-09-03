#!/usr/bin/env python
# coding: utf-8
from typing import List
from pyvesc.VESC import MultiVESC
import pygame
import time
import numpy as np
import traceback
import math
import sys


class MobileBase:
    """Mobile base representation and the interface with low level controllers"""

    def __init__(
        self,
        serial_port: str = "/dev/vesc_wheels",
        left_wheel_id: int = 24,
        right_wheel_id: int = 72,
        back_wheel_id: int = 116,
    ) -> None:
        params = [
            {"can_id": left_wheel_id, "has_sensor": True, "start_heartbeat": True},
            {"can_id": right_wheel_id, "has_sensor": True, "start_heartbeat": True},
            {"can_id": back_wheel_id, "has_sensor": True, "start_heartbeat": True},
        ]
        self._multi_vesc = MultiVESC(serial_port=serial_port, vescs_params=params)

        (
            self.left_wheel,
            self.right_wheel,
            self.back_wheel,
        ) = self._multi_vesc.controllers

        (
            self.left_wheel_measurements,
            self.right_wheel_measurements,
            self.back_wheel_measurements,
        ) = (None, None, None)

        self.max_duty_cyle = 0.4
        self.wheel_radius = 0.21 / 2.0
        self.wheel_to_center = 0.19588  # 0.188
        self.half_poles = 15.0
        self.lin_speed_ratio = 0.5
        self.rot_speed_ratio = 2.0
        # The joyticks dont come back at a perfect 0 position when released.
        # Any abs(value) below min_joy_position will be assumed to be 0
        self.min_joy_position = 0.03

        # Joy init
        pygame.init()
        pygame.display.init()
        pygame.joystick.init()

        self.nb_joy = pygame.joystick.get_count()
        if self.nb_joy < 1:
            print("No controller detected.")
            sys.exit()
        print("nb joysticks: {}".format(self.nb_joy))
        self.j = pygame.joystick.Joystick(0)

    def read_all_measurements(self) -> None:
        """Reads all the measurements for the left, right and back wheels"""
        self.left_wheel_measurements = self.left_wheel.get_measurements()
        self.right_wheel_measurements = self.right_wheel.get_measurements()
        self.back_wheel_measurements = self.back_wheel.get_measurements()

    def format_measurements(self, measurements) -> str:
        """Text formatting for the low level controller measurements"""
        if measurements is None:
            return "None"
        to_print = ""
        to_print += "temp_fet:{}\n".format(measurements.temp_fet)
        to_print += "temp_motor:{}\n".format(measurements.temp_motor)
        to_print += "avg_motor_current:{}\n".format(measurements.avg_motor_current)
        to_print += "avg_input_current:{}\n".format(measurements.avg_input_current)
        to_print += "avg_id:{}\n".format(measurements.avg_id)
        to_print += "avg_iq:{}\n".format(measurements.avg_iq)
        to_print += "duty_cycle_now:{}\n".format(measurements.duty_cycle_now)
        to_print += "rpm:{}\n".format(measurements.rpm)
        to_print += "v_in:{}\n".format(measurements.v_in)
        to_print += "amp_hours:{}\n".format(measurements.amp_hours)
        to_print += "amp_hours_charged:{}\n".format(measurements.amp_hours_charged)
        to_print += "watt_hours:{}\n".format(measurements.watt_hours)
        to_print += "watt_hours_charged:{}\n".format(measurements.watt_hours_charged)
        to_print += "tachometer:{}\n".format(measurements.tachometer)
        to_print += "tachometer_abs:{}\n".format(measurements.tachometer_abs)
        to_print += "mc_fault_code:{}\n".format(measurements.mc_fault_code)
        to_print += "pid_pos_now:{}\n".format(measurements.pid_pos_now)
        to_print += "app_controller_id:{}\n".format(measurements.app_controller_id)
        to_print += "time_ms:{}\n".format(measurements.time_ms)
        return to_print

    def print_all_measurements(self) -> None:
        """Prints the low level measurements from the 3 wheel controllers"""
        to_print = "\n*** back_wheel measurements:\n"
        to_print += self.format_measurements(self.back_wheel_measurements)
        to_print += "\n\n*** left_wheel:\n"
        to_print += self.format_measurements(self.left_wheel_measurements)
        to_print += "\n\n*** right_wheel:\n"
        to_print += self.format_measurements(self.right_wheel_measurements)

        print("{}".format(to_print))

    def ik_vel(self, x_vel: float, y_vel: float, rot_vel: float) -> List[float]:
        """Takes 2 linear speeds and 1 rot speed (robot's egocentric frame) and outputs the rotational speed (rad/s)
        of each of the 3 motors in an omni setup

        Args:
            x (float): x speed (m/s). Positive "in front" of the robot.
            y (float): y speed (m/s). Positive "to the left" of the robot.
            rot (float): rotational speed (rad/s). Positive counter-clock wise.
        """

        wheel_rot_speed_back = (1 / self.wheel_radius) * (self.wheel_to_center * rot_vel - y_vel)
        wheel_rot_speed_right = (1 / self.wheel_radius) * (
            self.wheel_to_center * rot_vel + y_vel / 2.0 + math.sin(math.pi / 3) * x_vel
        )
        wheel_rot_speed_left = (1 / self.wheel_radius) * (
            self.wheel_to_center * rot_vel + math.sin(math.pi / 3) * y_vel / 2 - math.sin(math.pi / 3) * x_vel
        )

        return [wheel_rot_speed_back, wheel_rot_speed_right, wheel_rot_speed_left]

    def wheel_rot_speed_to_pwm(self, rot: float) -> float:
        """Uses a simple affine model to map the expected rotational speed of the wheel to a constant PWM
        (based on measures made on a full Reachy Mobile)
        """
        # Creating an arteficial null zone to avoid undesired behaviours for very small rot speeds
        epsilon = 0.02
        if rot > epsilon:
            pwm = 0.0418 * rot + 0.0126
        elif rot < -epsilon:
            pwm = 0.0418 * rot - 0.0126
        else:
            pwm = 0.0

        return pwm

    def limit_duty_cycles(self, duty_cycles: List[float]) -> List[float]:
        """Limits the duty cycles to stay in +-max_duty_cyle"""
        for i in range(len(duty_cycles)):
            if duty_cycles[i] < 0:
                duty_cycles[i] = max(-self.max_duty_cyle, duty_cycles[i])
            else:
                duty_cycles[i] = min(self.max_duty_cyle, duty_cycles[i])
        return duty_cycles

    def speeds_from_joystick(self):
        cycle_max_t = self.lin_speed_ratio  # 0.2*factor
        cycle_max_r = self.rot_speed_ratio  # 0.1*factor
        print(
            "x = {:.2f}, y = {:.2f}, rot={:.2f}".format(
                -self.j.get_axis(1) * cycle_max_t, -self.j.get_axis(0) * cycle_max_t, -self.j.get_axis(3) * cycle_max_r
            )
        )

        if abs(self.j.get_axis(1)) < self.min_joy_position:
            x = 0.0
        else:
            x = -self.j.get_axis(1) * cycle_max_t

        if abs(self.j.get_axis(0)) < self.min_joy_position:
            y = 0.0
        else:
            y = -self.j.get_axis(0) * cycle_max_t

        if abs(self.j.get_axis(3)) < self.min_joy_position:
            rot = 0.0
        else:
            rot = -self.j.get_axis(3) * cycle_max_r

        return x, y, rot

    def send_wheel_commands(self, wheel_speeds: List[float]) -> None:
        duty_cycles = [self.wheel_rot_speed_to_pwm(wheel_speed) for wheel_speed in wheel_speeds]
        duty_cycles = self.limit_duty_cycles(duty_cycles)
        self.back_wheel.set_duty_cycle(duty_cycles[0])
        self.left_wheel.set_duty_cycle(duty_cycles[2])
        self.right_wheel.set_duty_cycle(duty_cycles[1])


# def cycle_from_joystick(joystick):
#     factor = 1.0
#     cycle_max_t = 0.2 * factor
#     cycle_max_r = 0.1 * factor
#     print(joystick.get_axis(1))
#     y = -joystick.get_axis(1) * cycle_max_t
#     x = joystick.get_axis(0) * cycle_max_t
#     rot = -joystick.get_axis(3) * cycle_max_r

#     cycle_back = x + rot
#     cycle_right = (x * np.cos(120 * np.pi / 180)) + (y * np.sin(120 * np.pi / 180)) + rot
#     cycle_left = (x * np.cos(240 * np.pi / 180)) + (y * np.sin(240 * np.pi / 180)) + rot

#     # print(cycle_back, cycle_left, cycle_right)

#     return (cycle_back), (cycle_right), (cycle_left)


# add args parse for serial port and wheel ids
if __name__ == "__main__":
    try:
        import argparse

        parser = argparse.ArgumentParser(
            description="Example of usage: python3 test_omnibase.py --serial_port /dev/vesc_wheels --right_wheel_id 72 --back_wheel_id 116"
        )
        parser.add_argument("--serial_port", type=str, default="/dev/vesc_wheels", help="serial port")
        parser.add_argument("--left_wheel_id", type=int, default=None, help="left wheel id")
        parser.add_argument("--right_wheel_id", type=int, default=None, help="right wheel id")
        parser.add_argument("--back_wheel_id", type=int, default=None, help="back wheel id")
        args = parser.parse_args()

        # local is 72 on reachy V2!!!!...

        # Attention! The VESC connected to the USB HAS to be declared as None here or wierd stuff happens...
        print("Make sure you plugged a controller!")
        print("Creating MobileBase instance...")
        mobile_base = MobileBase(
            serial_port=args.serial_port,
            left_wheel_id=args.left_wheel_id,
            right_wheel_id=args.right_wheel_id,
            back_wheel_id=args.back_wheel_id,
        )
        print("MobileBase instance created.")
        # self.omnibase = MobileBase(left_wheel_id=None, right_wheel_id=72, back_wheel_id=116)

        # pygame.init()
        # pygame.joystick.init()
        # nb_joy = pygame.joystick.get_count()
        # print("nb joysticks: {}".format(nb_joy))

        # J = pygame.joystick.Joystick(0)

        while True:
            for event in pygame.event.get():
                pass
            # mobile_base.back_wheel.set_duty_cycle(cycle_from_joystick(J)[0])
            # mobile_base.left_wheel.set_duty_cycle(cycle_from_joystick(J)[2])
            # mobile_base.right_wheel.set_duty_cycle(cycle_from_joystick(J)[1])

            x, y, theta = mobile_base.speeds_from_joystick()

            wheel_speeds = mobile_base.ik_vel(x, y, theta)
            mobile_base.send_wheel_commands(wheel_speeds)

            # mobile_base.read_all_measurements()
            # mobile_base.print_all_measurements()
            time.sleep(0.01)
    except Exception as e:
        traceback.print_exc()
    finally:
        print("reached finally block")
        mobile_base.back_wheel.set_duty_cycle(0.0)
        mobile_base.left_wheel.set_duty_cycle(0.0)
        mobile_base.right_wheel.set_duty_cycle(0.0)
        mobile_base.j.quit()
