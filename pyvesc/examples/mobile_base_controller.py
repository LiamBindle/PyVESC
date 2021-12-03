from pyvesc.VESC import MultiVESC


class MobileBase:
    def __init__(
        self, 
        serial_port='/dev/ttyACM0',
        left_wheel_id=None,
        right_wheel_id=72,
        back_wheel_id=None,
        ) -> None:

        params = [
            {'can_id': left_wheel_id, 'has_sensor': True, 'start_heartbeat': True},
            {'can_id': right_wheel_id, 'has_sensor': True, 'start_heartbeat': True},
            {'can_id': back_wheel_id, 'has_sensor': True, 'start_heartbeat': True},
        ]
        self._multi_vesc = MultiVESC(serial_port=serial_port, vescs_params=params)

        self.left_wheel, self.right_wheel, self.back_wheel = self._multi_vesc.controllers
