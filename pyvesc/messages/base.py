import struct


class VESCMessage(type):
    """ Metaclass for VESC messages.

    This is the metaclass for any VESC message classes. A VESC message class must then declare 2 static attributes:
    id: unsigned integer which is the identification number for messages of this class
    fields: list of tuples. tuples are of size 2, first element is the field name, second element is the fields type
            the third optional element is a scalar that will be applied to the data upon unpack
    format character. For more info on struct format characters see: https://docs.python.org/2/library/struct.html
    """
    _msg_registry = {}
    _endian_fmt = '>'
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
        cls._string_field = None
        cls._fmt_fields = ''
        cls._field_names = []
        cls._field_scalars = []
        for field, idx in zip(cls.fields, range(0, len(cls.fields))):
            cls._field_names.append(field[0])
            if len(field) >= 3:
                cls._field_scalars.append(field[2])
            if field[1] is 's':
                # string field, add % so we can vary the length
                cls._fmt_fields += '%u'
                cls._string_field = idx
            cls._fmt_fields += field[1]
        # check that at most 1 field is a string
        string_field_count = cls._fmt_fields.count('s')
        if string_field_count > 1:
            raise TypeError("Max number of string fields is 1.")
        if 'p' in cls._fmt_fields:
            raise TypeError("Field with format character 'p' detected. For string field use 's'.")
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
    def unpack(msg_bytes):
        msg_id = struct.unpack_from(VESCMessage._endian_fmt + VESCMessage._id_fmt, msg_bytes, 0)
        msg_type = VESCMessage.msg_type(*msg_id)
        data = None
        if not (msg_type._string_field is None):
            # string field
            fmt_wo_string = msg_type._fmt_fields.replace('%u', '')
            fmt_wo_string = fmt_wo_string.replace('s', '')
            len_string = len(msg_bytes) - struct.calcsize(VESCMessage._endian_fmt + fmt_wo_string) - 1
            fmt_w_string = msg_type._fmt_fields % (len_string)
            data = struct.unpack_from(VESCMessage._endian_fmt + fmt_w_string, msg_bytes, 1)
        else:
            data = list(struct.unpack_from(VESCMessage._endian_fmt + msg_type._fmt_fields, msg_bytes, 1))
            for k, field in enumerate(data):
                try:
                    data[k] = data[k]/msg_type._field_scalars[k]
                except (TypeError, IndexError) as e:
                    pass
        msg = msg_type(*data)
        if not (msg_type._string_field is None):
            string_field_name = msg_type._field_names[msg_type._string_field]
            setattr(msg,
                    string_field_name,
                    getattr(msg, string_field_name).decode('ascii'))
        return msg

    @staticmethod
    def pack(instance, header_only = None):
        if header_only:
            return struct.pack(VESCMessage._endian_fmt + VESCMessage._id_fmt, instance.id)

        field_values = []
        if not instance._field_scalars:
            for field_name in instance._field_names:
                field_values.append(getattr(instance, field_name))
        else:
            for field_name, field_scalar in zip(instance._field_names, instance._field_scalars):
                field_values.append(int(getattr(instance, field_name) * field_scalar))
        if not (instance._string_field is None):
            # string field
            string_field_name = instance._field_names[instance._string_field]
            string_length = len(getattr(instance, string_field_name))
            fmt = VESCMessage._endian_fmt + VESCMessage._id_fmt + (instance._fmt_fields  % (string_length))
            field_values[instance._string_field] = field_values[instance._string_field].encode('ascii')
            values = ((instance.id,) + tuple(field_values))
            return struct.pack(fmt, *values)
        else:
            return struct.pack(VESCMessage._endian_fmt + VESCMessage._id_fmt + instance._fmt_fields, *((instance.id,) + tuple(field_values)))
