from pyvesc.messages.base import VESCMessage

class GetValues(metaclass=VESCMessage):
    """ Gets internal sensor data
    """
    id = 4
    # When sending the request for this info, a blank ID must be sent
    #    fields = []
    fields = [
            ('temp_mos1', 'e'),
            ('temp_mos2', 'e'),
            ('temp_mos3', 'e'),
            ('temp_mos4', 'e'),
            ('temp_mos5', 'e'),
            ('temp_mos6', 'e'),
            ('temp_pcb',  'e'),
            ('current_motor', 'f'),
            ('current_in',  'f'),
            ('duty_now',    'e'),
            ('rpm',         'f'),
            ('v_in',        'e'),
            ('amp_hours',   'f'),
            ('amp_hours_charged', 'f'),
            ('watt_hours',  'f'),
            ('watt_hours_charged', 'f'),
            ('tachometer', 'l'),
            ('tachometer_abs', 'l'),
            ('mc_fault_code', 'c')
    ]
