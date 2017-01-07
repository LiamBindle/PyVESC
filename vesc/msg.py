import struct
from exceptions import *

class MsgRegistry(type):
    _registry = {}

    def __init__(cls, name, bases, clsdict):
        if len(cls.mro()) > 2:
            MsgRegistry._registry[clsdict['id']] = cls
            print("added subclass to registry")
        super(MsgRegistry, cls).__init__(name, bases, clsdict)

    @staticmethod
    def find(id):
        return MsgRegistry._registry[id]

class Msg(metaclass=MsgRegistry):
    endian_fmt = '<'
    _fmt_id = 'B'

    @property
    def id(self):
        raise NotImplementedError

    @property
    def fields(self):
        raise NotImplementedError

    def __init__(self, *args):
        self._fmt_fields = ''
        self._field_names = []
        for field in self.fields:
            self._field_names.append(field[0])
            self._fmt_fields += field[1]
        if args:
            if len(args) != len(self.fields):
                raise Exception("Expected %u arguments, received %u" % (len(self.fields), len(args)))
            for name, value in zip(self._field_names, args):
                setattr(self, name, value)

    def pack(self):
        field_values = []
        for field_name in self._field_names:
            field_values.append(getattr(self, field_name))
        return struct.pack(Msg.endian_fmt + Msg._fmt_id + self._fmt_fields, * ((self.id,) + tuple(field_values)))

    @staticmethod
    def fmt(msg_subclass):
        return ''.join([field[1] for field in msg_subclass.fields])

    @staticmethod
    def unpack(bytestring):
        id = struct.unpack_from(Msg.endian_fmt + Msg._fmt_id, bytestring, 0)
        msg_t = MsgRegistry.find(*id)
        t = Msg.fmt(msg_t)
        data = struct.unpack_from(Msg.endian_fmt + Msg.fmt(msg_t), bytestring, 1)
        msg = msg_t(*data)
        return msg

class example_msg(Msg):
    id = 0x34
    fields = [
        ('pwm', 'H'),
        ('fwd', 'B')
    ]

if __name__ == "__main__":
    print("hi")
    p1 = example_msg()
    p1.pwm = 54
    p1.fwd = 12

    p2 = Msg.unpack(p1.pack())




