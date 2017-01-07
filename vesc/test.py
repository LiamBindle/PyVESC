from unittest import TestCase

class TestPacket(TestCase):
    def exact_single_frame(self, length):
        """
        Simplest test possible. Create a packet, then parse a buffer containing this packet. Size of buffer is exactly
        one packet (no excess).
        :param length: Number of bytes in payload.
        """
        import random
        from packet import Stateless
        correct_payload_index = None
        if length < 256:
            correct_payload_index = 2
        else:
            correct_payload_index = 3
        test_payload = bytes(random.getrandbits(8) for i in range(length))
        # test framing
        packet = Stateless.pack(test_payload)
        self.assertEqual(len(packet), correct_payload_index + length + 3, "size of packet")
        buffer = bytearray(packet)
        # test Parser
        parsed, consumed = Stateless.unpack(buffer)
        buffer = buffer[consumed:]
        self.assertEqual(parsed, test_payload)
        self.assertEqual(len(buffer), 0)

    def exact_two_frames(self, length1, length2):
        """
        Check that if there is more than one packet in a buffer, that the unpacker will properly unpack the packets.
        Size of buffer for this test is exactly two packets.
        :param length1: Length of first payload
        :param length2: Length of second payload
        """
        import random
        from packet import Stateless
        correct_payload_index1 = None
        correct_payload_index2 = None
        if length1 < 256:
            correct_payload_index1 = 2
        else:
            correct_payload_index1 = 3
        if length2 < 256:
            correct_payload_index2 = 2
        else:
            correct_payload_index2 = 3
        test_payload1 = bytes(random.getrandbits(8) for i in range(length1))
        test_payload2 = bytes(random.getrandbits(8) for i in range(length2))
        # test framing
        packet1 = Stateless.pack(test_payload1)
        packet2 = Stateless.pack(test_payload2)
        self.assertEqual(len(packet1), correct_payload_index1 + length1 + 3, "size of packet")
        self.assertEqual(len(packet2), correct_payload_index2 + length2 + 3, "size of packet")
        buffer = bytearray(packet1 + packet2)
        # test Parser
        parsed, consumed = Stateless.unpack(buffer)
        buffer = buffer[consumed:]
        self.assertEqual(parsed, test_payload1)
        self.assertEqual(len(buffer), len(packet2))
        parsed, consumed = Stateless.unpack(buffer)
        buffer = buffer[consumed:]
        self.assertEqual(parsed, test_payload2)
        self.assertEqual(len(buffer), 0)

    def parse_buffer(self, length):
        import random
        from packet import Stateless
        correct_payload_index = None
        if length < 256:
            correct_payload_index = 2
        else:
            correct_payload_index = 3
        test_payload = bytes(random.getrandbits(8) for i in range(length))
        packet = Stateless.pack(test_payload)

        # test on small buffers
        for n in range(0, 5):
            in_buffer = bytearray(packet[:n])
            parsed, consumed = Stateless.unpack(in_buffer)
            out_buffer = in_buffer[consumed:]
            self.assertEqual(parsed, None)
            self.assertEqual(in_buffer, out_buffer)
        # test on buffer almost big enough
        for n in range(len(packet) - 4, len(packet)):
            in_buffer = bytearray(packet[:n])
            parsed, consumed = Stateless.unpack(in_buffer)
            out_buffer = in_buffer[consumed:]
            self.assertEqual(parsed, None)
            self.assertEqual(in_buffer, out_buffer)
        # test on buffer slightly too big
        extension = b'\x02\x04\x07'
        extended_packet = packet + b'\x02\x04\x07'
        for n in range(len(packet) + 1, len(packet) + 4):
            in_buffer = bytearray(extended_packet[:n])
            parsed, consumed = Stateless.unpack(in_buffer)
            out_buffer = in_buffer[consumed:]
            self.assertEqual(parsed, test_payload)
            self.assertEqual(out_buffer, extension[:n - len(packet)])

    def test_small_packets(self):
        for length in range(1, 5):
            self.exact_single_frame(length)
            self.exact_two_frames(length, length + 2)
            self.parse_buffer(length)
    """
    def test_med_packets(self):
        for length in range(254, 258):
            self.exact_single_frame(length)
            self.exact_two_frames(length, length - 23)
            self.parse_buffer(length)

    def test_large_packets(self):
        for length in range(1022, 1024):
            self.exact_single_frame(length)
            self.exact_two_frames(length, length + 100)
            self.parse_buffer(length)

    def test_corrupt_packet_exactly_1_packet(self):
        import random
        import struct
        from packet import Stateless
        # make a good packet
        test_payload = b'Te!'
        good_packet = b'\x02\x03Te!\xaa\x98\x03'
        corrupt_packets = []
        # corrupt first byte
        corrupt = b'\x01\x03Te!\xaa\x98\x03'
        corrupt_packets.append(corrupt)
        # corrupt payload_length (to be smaller and larger)
        smaller_corrupt = b'\x02\x02Te!\xaa\x98\x03'
        larger_corrupt = b'\x02\x04Te!\xaa\x98\x03\x03'
        corrupt_packets.append(smaller_corrupt)
        corrupt_packets.append(larger_corrupt)
        # corrupt first byte in payload
        corrupt = b'\x02\x03se!\xaa\x98\x03'
        corrupt_packets.append(corrupt)
        # corrupt last byte in payload
        corrupt = b'\x02\x03Tey\xaa\x98\x03'
        corrupt_packets.append(corrupt)
        # corrupt crc
        corrupt = b'\x02\x03Te!\xaa\x91\x03'
        corrupt_packets.append(corrupt)
        # corrupt terminator
        corrupt = b'\x02\x03Te!\xaa\x98\x09'
        corrupt_packets.append(corrupt)
        # check that exceptions are given on each corrupt packet
        for corrupt in corrupt_packets:
            in_buffer = bytearray(corrupt)
            parsed, consumed = Stateless.unpack(in_buffer)
            out_buffer = in_buffer[consumed:]
            self.assertEqual(parsed, None)
            self.assertEqual(out_buffer, corrupt)
        # check that the good packet is parsed
        in_buffer = bytearray(good_packet)
        parsed, consumed = parse(in_buffer)
        out_buffer = in_buffer[consumed:]
        self.assertEqual(parsed, test_payload)
        self.assertEqual(out_buffer, b'')
"""
class TestMsg(TestCase):
    pass

class TestCodec(TestCase):
    pass


