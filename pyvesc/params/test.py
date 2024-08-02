import random
import unittest
from .config_param import Param_UInt8, Param_Int8, Param_UInt16, Param_Int16, Param_UInt32, Param_Int32, Param_Double16, Param_Double32, Param_Double32_Auto


class TestConfigParam(unittest.TestCase):

    num_tests = 20

    def assert_serialization(self, param_class, value, round_result=False, assert_places=None):
        # Test serialization
        param = param_class("test_param_serialised", value=value)
        serialised = param.serialise()

        # Test deserialization
        param_deserialised = param_class("test_param_deserialised")
        param_deserialised.deserialise(serialised)
        if round_result:
            self.assertAlmostEqual(param_deserialised.value, round(value), places=assert_places)
        else:
            self.assertAlmostEqual(param_deserialised.value, value, places=assert_places)

        # Ensure that the deserialised value can be serialised back to the same data
        re_serialised = param_deserialised.serialise()
        self.assertAlmostEqual(re_serialised, serialised, places=assert_places)

    def test_param_uint8(self):
        # Test random uint8 values (0 to 255)
        for _ in range(self.num_tests):
            VALUE = random.randint(0, 255)
            self.assert_serialization(Param_UInt8, VALUE)

    def test_param_int8(self):
        # Test random int8 values (-128 to 127)
        for _ in range(self.num_tests):
            VALUE = random.randint(-128, 127)
            self.assert_serialization(Param_Int8, VALUE)

    def test_param_uint16(self):
        # Test random uint16 values (0 to 65535)
        for _ in range(self.num_tests):
            VALUE = random.randint(0, 65535)
            self.assert_serialization(Param_UInt16, VALUE)

    def test_param_int16(self):
        # Test random int16 values (-32768 to 32767)
        for _ in range(self.num_tests):
            VALUE = random.randint(-32768, 32767)
            self.assert_serialization(Param_Int16, VALUE)

    def test_param_uint32(self):
        # Test random uint32 values (0 to 4294967295)
        for _ in range(self.num_tests):
            VALUE = random.randint(0, 4294967295)
            self.assert_serialization(Param_UInt32, VALUE)

    def test_param_int32(self):
        # Test random int32 values (-2147483648 to 2147483647)
        for _ in range(self.num_tests):
            VALUE = random.randint(-2147483648, 2147483647)
            self.assert_serialization(Param_Int32, VALUE)

    def test_param_double16(self):
        # Test random double16 values within a sensible range
        for _ in range(self.num_tests):
            VALUE = random.uniform(-32768.0, 32767.99)
            self.assert_serialization(Param_Double16, VALUE, round_result=True)

    def test_param_double32(self):
        # Test random double32 values within a sensible range
        for _ in range(self.num_tests):
            VALUE = random.uniform(-1e6, 1e6)
            self.assert_serialization(Param_Double32, VALUE, round_result=True)

    def test_param_double32_auto(self):
        # Test random double32_auto values within a sensible range
        for _ in range(self.num_tests):
            VALUE = random.uniform(-100000.0, 100000.0)
            self.assert_serialization(Param_Double32_Auto, VALUE, assert_places=1)
