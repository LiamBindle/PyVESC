#!/usr/bin/env python
# coding: utf-8

from pyvesc.VESC import MultiVESC
import pygame
import time
import numpy as np


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

        self.get_logger().info("{}".format(to_print))


def cycle_from_joystick(joystick):
    factor = 1.0
    cycle_max_t = 0.2 * factor
    cycle_max_r = 0.1 * factor
    print(joystick.get_axis(1))
    y = -joystick.get_axis(1) * cycle_max_t
    x = joystick.get_axis(0) * cycle_max_t
    rot = -joystick.get_axis(3) * cycle_max_r

    cycle_back = x + rot
    cycle_right = (
        (x * np.cos(120 * np.pi / 180)) + (y * np.sin(120 * np.pi / 180)) + rot
    )
    cycle_left = (x * np.cos(240 * np.pi / 180)) + (y * np.sin(240 * np.pi / 180)) + rot

    # print(cycle_back, cycle_left, cycle_right)

    return (cycle_back), (cycle_right), (cycle_left)


# add args parse for serial port and wheel ids
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Example of usage: python3 test_omnibase.py --serial_port /dev/vesc_wheels --left_wheel_id 24 --right_wheel_id 72 --back_wheel_id 116"
    )
    parser.add_argument(
        "--serial_port", type=str, default="/dev/vesc_wheels", help="serial port"
    )
    parser.add_argument("--left_wheel_id", type=int, default=24, help="left wheel id")
    parser.add_argument("--right_wheel_id", type=int, default=72, help="right wheel id")
    parser.add_argument("--back_wheel_id", type=int, default=116, help="back wheel id")
    args = parser.parse_args()

    mobile_base = MobileBase(
        serial_port=args.serial_port,
        left_wheel_id=args.left_wheel_id,
        right_wheel_id=args.right_wheel_id,
        back_wheel_id=args.back_wheel_id,
    )

    pygame.init()
    pygame.joystick.init()

    J = pygame.joystick.Joystick(0)

    while True:
        for event in pygame.event.get():
            pass
        mobile_base.back_wheel.set_duty_cycle(cycle_from_joystick(J)[0])
        mobile_base.left_wheel.set_duty_cycle(cycle_from_joystick(J)[2])
        mobile_base.right_wheel.set_duty_cycle(cycle_from_joystick(J)[1])

        mobile_base.read_all_measurements()
        mobile_base.print_all_measurements()
        time.sleep(0.1)
