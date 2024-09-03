import pyvesc


def simple_example():
    # lets make a SetDuty message
    my_msg = pyvesc.SetDutyCycle(1e5)

    # now lets encode it to make get a byte string back
    packet = pyvesc.encode(my_msg)

    # now lets create a buffer with some garbage in it and put our packet in the middle
    buffer = b'\x23\x82\x02' + packet + b'\x38\x23\x12\x01'

    # now lets parse our message which is hidden in the buffer
    msg, consumed = pyvesc.decode(buffer)

    # update the buffer
    buffer = buffer[consumed:]

    # check that the message we parsed is equivalent to my_msg
    assert my_msg.duty_cycle == msg.duty_cycle
    print("Success!")



if __name__ == "__main__":
    simple_example()
