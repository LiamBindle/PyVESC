import struct

STRING_MAX_LEN = 5000


class VESCMessage(type):
    """ Metaclass for VESC messages.

    This is the metaclass for any VESC message classes. A VESC message class must then declare 2 static attributes:
    id: unsigned integer which is the identification number for messages of this class
    fields: list of tuples. tuples are of size 2, first element is the field name, second element is the fields type
            the third optional element is a scalar that will be applied to the data upon unpack
    format character. For more info on struct format characters see: https://docs.python.org/2/library/struct.html
    """
    _msg_registry = {}
    _endian_fmt = '!'
    _id_fmt = 'B'
    _can_id_fmt = 'BB'
    _comm_forward_can = 33
    _entry_msg_registry = None

    def __init__(cls, name, bases, clsdict):
        cls.can_id = None
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
        cls._send_string_field = None
        cls._send_field_formats = []
        cls._send_field_names = []
        cls._send_field_scalars = []
        # receive fields can be different from send fields
        cls._recv_string_field = None
        cls._recv_field_formats = []
        cls._recv_field_names = []
        cls._recv_field_scalars = []

        # check that there are any fields defined
        if not hasattr(cls, 'send_fields') and not hasattr(cls, 'recv_fields'):
            raise AttributeError("No fields defined for ", VESCMessage._msg_registry[msg_id])

        # format the fields to send
        if hasattr(cls, 'send_fields'):
            for field, idx in zip(cls.send_fields, range(0, len(cls.send_fields))):
                cls._send_field_names.append(field[0])

                # apply scalar if defined
                if len(field) >= 3:
                    cls._send_field_scalars.append(field[2])
                if field[1] == 's':
                    # string field, add % so we can vary the length
                    # edit: we will use a fixed length for now
                    cls._send_field_formats.append('%us')
                    cls._send_string_field = idx
                else:
                    cls._send_field_formats.append(field[1])

            # calc size, iterating through each format to eliminate padding
            msg_size = 0
            for fmt in cls._recv_field_formats:
                msg_size += struct.calcsize(fmt)
            cls._recv_full_msg_size = msg_size

            # check that at most 1 field is a string
            string_field_count = cls._send_field_formats.count('s') + cls._send_field_formats.count('%us')
            if string_field_count > 1:
                raise TypeError("Max number of string fields is 1.")
            if 'p' in cls._send_field_formats:
                raise TypeError("Field with format character 'p' detected. For string field use 's'.")

        # format the fields to receive, if we didn't define any - don't make any
        # TODO: this is duplicated code, should be refactored
        if hasattr(cls, 'recv_fields'):
            for field, idx in zip(cls.recv_fields, range(0, len(cls.recv_fields))):
                cls._recv_field_names.append(field[0])

                # apply scalar if defined
                if len(field) >= 3:
                    cls._recv_field_scalars.append(field[2])
                if field[1] == 's':
                    # for now, maximum string size is 1000
                    cls._recv_field_formats.append('%us')
                    cls._recv_string_field = idx
                else:
                    cls._recv_field_formats.append(field[1])

            # calc size, iterating through each format to eliminate padding
            msg_size = 0
            for fmt in cls._recv_field_formats:
                if '%us' in fmt:
                    msg_size += STRING_MAX_LEN
                else:
                    msg_size += struct.calcsize(fmt)
            cls._recv_full_msg_size = msg_size

            # check that at most 1 field is a string
            string_field_count = cls._recv_field_formats.count('s')
            if string_field_count > 1:
                raise TypeError("Max number of string fields is 1.")
            if 'p' in cls._recv_field_formats:
                raise TypeError("Field with format character 'p' detected. For string field use 's'.")

        super(VESCMessage, cls).__init__(name, bases, clsdict)

    def __call__(cls, *args, **kwargs):
        instance = super(VESCMessage, cls).__call__()
        if 'can_id' in kwargs:
            instance.can_id = kwargs['can_id']
        else:
            instance.can_id = None

        # Select whether we want to unpack the send or receive fields
        # If there are only one defined, we will unpack that one
        # If both are defined, we will refer to the unpack_send_fields flag
        available_fields = {'send_fields': hasattr(cls, 'send_fields'), 'recv_fields': hasattr(cls, 'recv_fields')}
        field_to_unpack = None
        if available_fields['send_fields'] and not available_fields['recv_fields']:
            field_to_unpack = 'send_fields'
        elif not available_fields['send_fields'] and available_fields['recv_fields']:
            field_to_unpack = 'recv_fields'
        elif available_fields['send_fields'] and available_fields['recv_fields']:
            if 'unpack_send_fields' in kwargs and kwargs['unpack_send_fields'] is False:
                field_to_unpack = 'recv_fields'
            else:
                field_to_unpack = 'send_fields'

        if field_to_unpack == 'send_fields':
            fields = cls.send_fields
            field_names = cls._send_field_names
        else:
            fields = cls.recv_fields
            field_names = cls._recv_field_names

        if args:
            if len(args) != len(fields):
                raise AttributeError("Expected %u arguments, received %u" % (len(fields), len(args)))
            for name, value in zip(field_names, args):
                setattr(instance, name, value)
        return instance

    @staticmethod
    def msg_type(id):
        return VESCMessage._msg_registry[id]

    @staticmethod
    def unpack(msg_bytes, unpack_send_fields=False):
        msg_id = struct.unpack_from(VESCMessage._endian_fmt + VESCMessage._id_fmt, msg_bytes, 0)
        msg_type = VESCMessage.msg_type(*msg_id)
        data = None

        # Select whether we want to unpack the send or receive fields
        # We will unpack the send fields if there are none received
        if unpack_send_fields or not hasattr(msg_type, 'recv_fields'):
            fields = msg_type.send_fields
            string_field = msg_type._send_string_field
            field_names = msg_type._send_field_names
            field_formats = "".join([char for tup in msg_type._send_field_formats for char in tup])
            field_scalars = msg_type._send_field_scalars
        else:
            fields = msg_type.recv_fields
            string_field = msg_type._recv_string_field
            field_names = msg_type._recv_field_names
            field_formats = "".join([char for tup in msg_type._recv_field_formats for char in tup])  # stringify formats
            field_scalars = msg_type._recv_field_scalars

        if not (string_field is None):
            # remove the %u and s from the format string
            if '%u' or 's' in field_formats:
                fmt_wo_string = field_formats.replace('%u', '')
                fmt_wo_string = fmt_wo_string.replace('s', '')
            len_string = len(msg_bytes) - struct.calcsize(VESCMessage._endian_fmt + fmt_wo_string) - 1
            fmt_w_string = field_formats % (len_string)
            data = struct.unpack_from(VESCMessage._endian_fmt + fmt_w_string, msg_bytes, 1)
        else:
            data = list(struct.unpack_from(VESCMessage._endian_fmt + field_formats, msg_bytes, 1))
            for k, field in enumerate(data):
                try:
                    if field_scalars[k] != 0:
                        data[k] = data[k] / field_scalars[k]
                except (TypeError, IndexError) as e:
                    print("Error encountered on field " + fields[k][0])
                    print(e)

        msg = msg_type(*data, unpack_send_fields=unpack_send_fields)
        if not (string_field is None):
            string_field_name = field_names[string_field]

            # if scalar is -1, we do not interpret the string as ascii, instead as a bytestring
            if len(field_scalars) > 0 and field_scalars[string_field] == -1:
                setattr(msg,
                        string_field_name,
                        getattr(msg, string_field_name))
            else:
                setattr(msg,
                        string_field_name,
                        getattr(msg, string_field_name).decode('ascii'))

        return msg

    @staticmethod
    def pack(instance, header_only=None, pack_send_fields=True):
        if header_only:
            if instance.can_id is not None:
                fmt = VESCMessage._endian_fmt + VESCMessage._can_id_fmt + VESCMessage._id_fmt
                values = (VESCMessage._comm_forward_can, instance.can_id, instance.id)
            else:
                fmt = VESCMessage._endian_fmt + VESCMessage._id_fmt
                values = (instance.id,)
            return struct.pack(fmt, *values)

        # Select whether we want to unpack the send or receive fields
        # we may only ever unpack the receive fields, but the send fields
        # are used for unit testing at least
        if pack_send_fields:
            string_field = instance._send_string_field
            field_names = instance._send_field_names
            field_formats = "".join([char for tup in instance._send_field_formats for char in tup])  # stringify formats
            field_scalars = instance._send_field_scalars
        else:
            string_field = instance._recv_string_field
            field_names = instance._recv_field_names
            field_formats = "".join([char for tup in instance._recv_field_formats for char in tup])  # stringify formats
            field_scalars = instance._recv_field_scalars

        field_values = []
        if not field_scalars:
            for field_name in field_names:
                field_values.append(getattr(instance, field_name))
        else:
            for index, (field_name, field_scalar) in enumerate(zip(field_names, field_scalars)):
                # if it's a string field, don't apply the scalar as it represents the format, not the data
                if instance.send_fields[index][1] == 's':
                    field_values.append(getattr(instance, field_name))
                else:
                    field_values.append(int(getattr(instance, field_name) * field_scalar))
        if not (string_field is None):
            # string field
            string_field_name = field_names[string_field]
            # remove the %u and s from the format string
            if '%u' or 's' in field_formats:
                fmt_wo_string = field_formats.replace('%u', '')
                fmt_wo_string = fmt_wo_string.replace('s', '')
            string_length = len(getattr(instance, string_field_name))
            # if scalar is -1, we do not interpret the string as ascii, instead as a bytestring
            if len(field_scalars) > string_field and field_scalars[string_field] == -1:
                field_values[string_field] = field_values[string_field]
            else:
                field_values[string_field] = field_values[string_field].encode('ascii')
            values = ((instance.id,) + tuple(field_values))
            if instance.can_id is not None:
                fmt = VESCMessage._endian_fmt + VESCMessage._can_id_fmt + VESCMessage._id_fmt + (fmt % (string_length))
                values = (VESCMessage._comm_forward_can, instance.can_id) + values
            else:
                fmt = VESCMessage._endian_fmt + VESCMessage._id_fmt + (field_formats % (string_length))
            return struct.pack(fmt, *values)
        else:
            values = ((instance.id,) + tuple(field_values))
            if instance.can_id is not None:
                fmt = VESCMessage._endian_fmt + VESCMessage._can_id_fmt + VESCMessage._id_fmt + field_formats
                values = (VESCMessage._comm_forward_can, instance.can_id) + values
            else:
                fmt = VESCMessage._endian_fmt + VESCMessage._id_fmt + field_formats
            return struct.pack(fmt, *values)
