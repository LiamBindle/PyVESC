from pyvesc.messages.base import VESCMessage

class GetValues(metaclass=VESCMessage):
    """ Gets internal sensor data
    """
    id = 4

    fields = [
            ('temp_mos1', 'h', 10),
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
            ('mc_fault_code', 'c')
    ]

    class GetMcConf(metaclass=VESCMessage):
        """ Gets the configuration of the motor"""
        id = 12

        fields = [
                ('pwm_mode', 'B'),
                ('comm_mode', 'B'),
                ('motor_type', 'B'),
                ('sensor_mode', 'B'),
                ('l_current_max', 'i', 1000),
                ('l_current_min', 'i', 1000),
                ('l_in_current_max', 'i', 1000),
                ('l_in_current_min', 'i', 1000),
                ('l_abs_current_max', 'i', 1000),
                ('l_min_erpm', 'i', 1000),
                ('l_max_erpm', 'i', 1000),
                ('l_max_erpm_fbrake', 'i', 1000),
                ('l_max_erpm_fbrake_cc', 'i', 1000),
                ('l_min_vin', 'i', 1000),
                ('l_max_vin', 'i', 1000),
                ('l_battery_cut_start', 'i', 1000),
                ('l_battery_cut_end', 'i', 1000),
                ('l_slow_abs_currrent', 'B'),
                ('l_rpm_lim_neg_torque', 'B'),
                ('l_temp_fet_start', 'i', 1000),
                ('l_temp_fet_end', 'i', 1000),
                ('l_temp_motor_start', 'i', 1000),
                ('l_min_duty', 'i', 1000000),
                ('l_max_duty', 'i', 1000000),
                ('sl_min_erom', 'i', 1000),
                ('sl_min_rpm_cycle_int_limit', 'i', 1000),
                ('sl_max_fullbreak_current_dir_change', 'i', 1000),
                ('sl_cycle_int_limit', 'i', 1000),
                ('sl_phase_advance_at_br', 'i', 1000),
                ('sl_cycle_int_rpm_br', 'i', 1000),
                ('sl_bemf_coupling_k', 'i', 1000),
                ('hall_table0', 'B'),
                ('hall_table1', 'B'),
                ('hall_table2', 'B'),
                ('hall_table3', 'B'),
                ('hall_table4', 'B'),
                ('hall_table5', 'B'),
                ('hall_table6', 'B'),
                ('hall_table7', 'B'),
                ('hall_sl_erpm', 'i', 1000),
                ('foc_current_kp', 'f', 1e5),
                ('foc_current_ki', 'f', 1e5),
                ('foc_f_sw', 'f', 1e3),
                ('foc_dt_us', 'f', 1e6),
                ('foc_encoder_inverted', 'B'),
                ('foc_encoder_offset', 'f', 1e3),
                ('foc_encoder_ratio', 'f', 1e3),
                ('foc_sensor_mode', 'B'),
                ('foc_pll_kp', 'f', 1e3),
                ('foc_pll_ki', 'f', 1e3),
                ('foc_motor_l', 'f', 1e8),
                ('foc_motor_r', 'f', 1e5),
                ('foc_motor_flux_linkage', 'f', 1e5),
                ('foc_observer_gain', 'f', 1e0),
                ('foc_duty_dowmramp_kp', 'f', 1e3),
                ('foc_duty_ki', 'f', 1e3),
                ('foc_openloop_rpm', 'f', 1e3),
                ('foc_sl_openloop_hyst', 'f', 1e3),
                ('foc_sl_openloop_time', 'f', 1e3),
                ('foc_sl_d_current_duty', 'f', 1e6),
                ('foc_sl_d_current_factor', 'f', 1e6),
                ('foc_hall_table0', 'B'),
                ('foc_hall_table1', 'B'),
                ('foc_hall_table2', 'B'),
                ('foc_hall_table3', 'B'),
                ('foc_hall_table4', 'B'),
                ('foc_hall_table5', 'B'),
                ('foc_hall_table6', 'B'),
                ('foc_hall_table7', 'B'),
                ('foc_sl_erpm', 'i', 1000),
                ('s_pid_kp', 'i', 1000000),
                ('s_pid_ki', 'i', 1000000),
                ('s_pid_kd', 'i', 1000000),
                ('s_pid_min_erpm', 'i', 1000),
                ('p_pid_kp', 'i', 1000000),
                ('p_pid_ki', 'i', 1000000),
                ('p_pid_kd', 'i', 1000000),
                ('p_pid_ang_div', 'f', 1e5),
                ('cc_startup_boost_duty', 'i', 1000000),
                ('cc_min_current', 'i', 1000),
                ('cc_gain', 'i', 1000000),
                ('cc_ramp_step_max', 'i', 1000000),
                ('m_fault_stop_time_ms', 'i'),
                ('m_duty_ramp_step', 'f', 1000000),
                ('m_duty_ramp_step_rpm_lim', 'f', 1000000),
                ('m_current_backoff_gain', 'f', 1000000),
                ('m_encoder_counts', 'I'),
                ('m_sensor_port_mode', 'B')
                ]


class GetRotorPosition(metaclass=VESCMessage):
    """ Gets rotor position data

    Must be set to DISP_POS_MODE_ENCODER or DISP_POS_MODE_PID_POS (Mode 3 or
    Mode 4). This is set by SetRotorPositionMode (id=21).
    """
    id = 21

    fields = [
            ('rotor_pos', 'i', 100000)
    ]
