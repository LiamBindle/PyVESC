from abc import ABC, abstractmethod
import struct
from math import ldexp, frexp


def buffer_pop(buffer, length, ind):
    """
    Pop the first `length` bytes from the buffer and return them.
    The buffer is updated in place.

    :ind: Index of the buffer to pop from, unused - to be removed
    """
    # Ensure buffer is a bytearray for in-place modification
    if not isinstance(buffer, bytearray):
        raise TypeError("Buffer must be of type 'bytearray'")

    popped = buffer[:length]
    del buffer[:length]  # Modify the buffer in place
    return popped


class ConfigParam(ABC):

    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    @abstractmethod
    def deserialise(self, buffer):
        pass

    @abstractmethod
    def serialise(self):
        pass

    def __repr__(self):
        return f"{self.name}: {self.value}"


class Param_Bool(ConfigParam):

    def __init__(self, name, value=None):
        super().__init__(name, value)
        self.format = '?'

    def deserialise(self, buffer):
        if len(buffer) != 1:
            raise ValueError("Buffer must be exactly 1 byte long.")
        self.value = struct.unpack(self.format, buffer)[0]

    def serialise(self):
        return struct.pack(self.format, self.value)


class Param_UInt8(ConfigParam):

    def __init__(self, name, value=None):
        super().__init__(name, value)
        self.format = 'B'  # Format for unsigned 8-bit integer

    def deserialise(self, buffer):
        if len(buffer) != 1:
            raise ValueError("Buffer must be exactly 1 byte long.")
        self.value = int.from_bytes(buffer, byteorder='big', signed=False)

    def serialise(self):
        if self.value < 0 or self.value > 255:
            raise ValueError("Value must be between 0 and 255 for uint8.")
        return self.value.to_bytes(1, byteorder='big', signed=False)


class Param_Int8(ConfigParam):

    def __init__(self, name, value=None):
        super().__init__(name, value)
        self.format = 'b'  # Format for signed 8-bit integer

    def deserialise(self, buffer):
        if len(buffer) != 1:
            raise ValueError("Buffer must be exactly 1 byte long.")
        self.value = int.from_bytes(buffer, byteorder='big', signed=True)

    def serialise(self):
        if self.value < -128 or self.value > 127:
            raise ValueError("Value must be between -128 and 127 for int8.")
        return self.value.to_bytes(1, byteorder='big', signed=True)


class Param_UInt16(ConfigParam):

    def __init__(self, name, value=None):
        super().__init__(name, value)
        self.format = 'H'  # Format for unsigned 16-bit integer

    def deserialise(self, buffer):
        if len(buffer) != 2:
            raise ValueError("Buffer must be exactly 2 bytes long.")
        self.value = int.from_bytes(buffer, byteorder='big', signed=False)

    def serialise(self):
        if self.value < 0 or self.value > 65535:
            raise ValueError("Value must be between 0 and 65535 for uint16.")
        return self.value.to_bytes(2, byteorder='big', signed=False)


class Param_Int16(ConfigParam):

    def __init__(self, name, value=None):
        super().__init__(name, value)
        self.format = 'h'  # Format for signed 16-bit integer

    def deserialise(self, buffer):
        if len(buffer) != 2:
            raise ValueError("Buffer must be exactly 2 bytes long.")
        self.value = int.from_bytes(buffer, byteorder='big', signed=True)

    def serialise(self):
        if self.value < -32768 or self.value > 32767:
            raise ValueError("Value must be between -32768 and 32767 for int16.")
        return self.value.to_bytes(2, byteorder='big', signed=True)


class Param_UInt32(ConfigParam):

    def __init__(self, name, value=None):
        super().__init__(name, value)
        self.format = 'I'  # Format for unsigned 32-bit integer

    def deserialise(self, buffer):
        if len(buffer) != 4:
            raise ValueError("Buffer must be exactly 4 bytes long.")
        self.value = int.from_bytes(buffer, byteorder='big', signed=False)

    def serialise(self):
        if self.value < 0 or self.value > 4294967295:
            raise ValueError("Value must be between 0 and 4294967295 for uint32.")
        return self.value.to_bytes(4, byteorder='big', signed=False)


class Param_Int32(ConfigParam):

    def __init__(self, name, value=None):
        super().__init__(name, value)
        self.format = 'i'  # Format for signed 32-bit integer

    def deserialise(self, buffer):
        if len(buffer) != 4:
            raise ValueError("Buffer must be exactly 4 bytes long.")
        self.value = int.from_bytes(buffer, byteorder='big', signed=True)

    def serialise(self):
        if self.value < -2147483648 or self.value > 2147483647:
            raise ValueError("Value must be between -2147483648 and 2147483647 for int32.")
        return self.value.to_bytes(4, byteorder='big', signed=True)


class Param_Double16(Param_Int16):
    """
        In vesc, is rounded to nearest integer and then sent as a uint16
    """

    def __init__(self, name, value=None):
        super().__init__(name, value)
        self.format = 'e'  # Format for 16-bit floating point (half precision)

    def deserialise(self, buffer):

        super().deserialise(buffer)
        self.value = float(self.value)  # Convert to float

    def serialise(self):
        rounded = round(self.value)
        if rounded < -32768 or rounded > 32767:
            raise ValueError("Value must be between -32768 and 32767 for int16.")
        return rounded.to_bytes(2, byteorder='big', signed=True)


class Param_Double32(Param_Int32):
    """
        In vesc, is rounded to nearest integer and then sent as a uint32
    """

    def __init__(self, name, value=None):
        super().__init__(name, value)
        self.format = 'f'  # Format for 32-bit floating point (single precision)

    def deserialise(self, buffer):
        super().deserialise(buffer)
        self.value = float(self.value)  # Convert to float

    def serialise(self):
        rounded = round(self.value)
        if rounded < -2147483648 or rounded > 2147483647:
            raise ValueError("Value must be between -2147483648 and 2147483647 for int32.")
        return rounded.to_bytes(4, byteorder='big', signed=True)


class Param_Double32_Auto(Param_Int32):
    """
        In vesc, is properly cast as a float, to be implemented
    """

    def __init__(self, name, value=None):
        super().__init__(name, value)
        self.format = 'f'  # Assumed to be similar to Double32 (single precision)

    def deserialise(self, buffer):
        # TODO: Implement proper deserialisation
        buffer = int.from_bytes(buffer, byteorder='big', signed=False)
        e = (buffer >> 23) & 0xFF
        m = buffer & 0x7FFFFF
        negative = buffer & (1 << 31)

        f = 0.0
        if (e != 0 or m != 0):
            f = float(m) / (8388608.0 * 2.0) + 0.5
            e -= 126

        if (negative):
            f = -f

        self.value = ldexp(f, e)

    def serialise(self):

        number = self.value

        # Set subnormal numbers to 0
        if abs(number) < 1.5e-38:
            number = 0.0

        fr, e = frexp(number)  # Use math.frexp to get mantissa and exponent
        fr_abs = abs(fr)
        fr_s = 0

        # Handle the mantissa for normalized numbers
        if fr_abs >= 0.5:
            fr_s = int((fr_abs - 0.5) * 2.0 * 8388608.0)  # Convert mantissa to 23-bit fraction
            e += 126  # Adjust exponent

        # Combine exponent and mantissa into a 32-bit integer
        res = ((e & 0xFF) << 23) | (fr_s & 0x7FFFFF)

        # Set the sign bit if the original number was negative
        if fr < 0:
            res |= 1 << 31

        # Return the result as 4 bytes (big-endian, unsigned)
        return res.to_bytes(4, byteorder='big', signed=False)
