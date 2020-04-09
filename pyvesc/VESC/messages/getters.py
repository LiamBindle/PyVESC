from pyvesc.protocol.base import VESCMessage
from pyvesc.VESC.messages import VedderCmd


pre_v3_33_fields = [('temp_mos1', 'h', 10),
                    ('temp_mos2', 'h', 10),
                    ('temp_mos3', 'h', 10),
                    ('temp_mos4', 'h', 10),
                    ('temp_mos5', 'h', 10),
                    ('temp_mos6', 'h', 10),
                    ('temp_pcb',  'h', 10),
                    ('current_motor', 'i', 100),
                    ('current_in',  'i', 100),
                    ('duty_now',    'h', 1000),
                    ('rpm',         'i', 1),
                    ('v_in',        'h', 10),
                    ('amp_hours',   'i', 10000),
                    ('amp_hours_charged', 'i', 10000),
                    ('watt_hours',  'i', 10000),
                    ('watt_hours_charged', 'i', 10000),
                    ('tachometer', 'i', 1),
                    ('tachometer_abs', 'i', 1),
                    ('mc_fault_code', 'c', 0)]


class GetVersion(metaclass=VESCMessage):
    """ Gets version fields
    """
    id = VedderCmd.COMM_FW_VERSION

    fields = [
            ('comm_fw_version', 'b', 0),
            ('fw_version_major', 'b', 0),
            ('fw_version_minor', 'b', 0)
    ]

    def __str__(self):
        return f"{self.comm_fw_version}.{self.fw_version_major}.{self.fw_version_minor}"


class GetValues(metaclass=VESCMessage):
    """ Gets internal sensor data
    """
    id = VedderCmd.COMM_GET_VALUES

    fields = [
        ('temp_fet', 'h', 10),
        ('temp_motor', 'h', 10),
        ('avg_motor_current', 'i', 100),
        ('avg_input_current', 'i', 100),
        ('avg_id', 'i', 100),
        ('avg_iq', 'i', 100),
        ('duty_cycle_now', 'h', 1000),
        ('rpm', 'i', 1),
        ('v_in', 'h', 10),
        ('amp_hours', 'i', 10000),
        ('amp_hours_charged', 'i', 10000),
        ('watt_hours', 'i', 10000),
        ('watt_hours_charged', 'i', 10000),
        ('tachometer', 'i', 1),
        ('tachometer_abs', 'i', 1),
        ('mc_fault_code', 'c', 0),
        ('pid_pos_now', 'i', 1000000),
        ('app_controller_id', 'c', 0),
        ('time_ms', 'i', 1),
    ]


class GetRotorPosition(metaclass=VESCMessage):
    """ Gets rotor position data
    
    Must be set to DISP_POS_MODE_ENCODER or DISP_POS_MODE_PID_POS (Mode 3 or 
    Mode 4). This is set by SetRotorPositionMode (id=21).
    """
    id = VedderCmd.COMM_ROTOR_POSITION

    fields = [
            ('rotor_pos', 'i', 100000)
    ]