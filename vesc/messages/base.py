import struct


class VESCMessage(type):
    """ Metaclass for VESC messages.
    """
    _msg_registry = {}
    _endian_fmt = '<'
    _id_fmt = 'B'
    _entry_msg_registry = None

    def __init__(cls, name, bases, clsdict):
        msg_id = clsdict['id']
        # make sure that message classes are final
        for klass in bases:
            if isinstance(klass, VESCMessage):
                raise TypeError("VESC messages cannot be inherited.")
        # check for duplicate id
        if msg_id in VESCMessage._msg_registry:
            raise TypeError("ID conflict with %s" % str(VESCMessage._msg_registry[msg_id]))
        else:
            VESCMessage._msg_registry[msg_id] = cls
        # initialize cls static variables
        cls._fmt_fields = ''
        cls._field_names = []
        for field in cls.fields:
            cls._field_names.append(field[0])
            cls._fmt_fields += field[1]
        super(VESCMessage, cls).__init__(name, bases, clsdict)

    def __call__(cls, *args, **kwargs):
        instance = super(VESCMessage, cls).__call__()
        if args:
            if len(args) != len(cls.fields):
                raise AttributeError("Expected %u arguments, received %u" % (len(cls.fields), len(args)))
            for name, value in zip(cls._field_names, args):
                setattr(instance, name, value)
        return instance

    @staticmethod
    def msg_type(id):
        return VESCMessage._msg_registry[id]

    @staticmethod
    def decode(msg_bytes):
        msg_id = struct.unpack_from(VESCMessage._endian_fmt + VESCMessage._id_fmt, msg_bytes, 0)
        msg_type = VESCMessage.msg_type(*msg_id)
        data = struct.unpack_from(VESCMessage._endian_fmt + msg_type._fmt_fields, msg_bytes, 1)
        msg = msg_type(*data)
        return msg

    @staticmethod
    def encode(instance):
        field_values = []
        for field_name in instance._field_names:
            field_values.append(getattr(instance, field_name))
        return struct.pack(VESCMessage._endian_fmt + VESCMessage._id_fmt + instance._fmt_fields, *((instance.id,) + tuple(field_values)))

