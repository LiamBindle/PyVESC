import pyvesc
from pyvesc.VESC.messages import GetValues, SetRPM, SetCurrent, SetRotorPositionMode, GetRotorPosition
import serial
import time

# Set your serial port here (either /dev/ttyX or COMX)
serialport = 'COM3'


def get_values_example():
    with serial.Serial(serialport, baudrate=115200, timeout=0.05) as ser:
        try:
            # Optional: Turn on rotor position reading if an encoder is installed
            ser.write(pyvesc.encode(SetRotorPositionMode(SetRotorPositionMode.DISP_POS_MODE_ENCODER)))
            while True:
                # Set the ERPM of the VESC motor
                #    Note: if you want to set the real RPM you can set a scalar
                #          manually in setters.py
                #          12 poles and 19:1 gearbox would have a scalar of 1/228
                ser.write(pyvesc.encode(SetRPM(10000)))

                # Request the current measurement from the vesc
                ser.write(pyvesc.encode_request(GetValues))

                # Check if there is enough data back for a measurement
                if ser.in_waiting > 61:
                    (response, consumed) = pyvesc.decode(ser.read(61))

                    # Print out the values
                    try:
                        print(response.rpm)

                    except:
                        # ToDo: Figure out how to isolate rotor position and other sensor data
                        #       in the incoming datastream
                        #try:
                        #    print(response.rotor_pos)
                        #except:
                        #    pass
                        pass

                time.sleep(0.1)

        except KeyboardInterrupt:
            # Turn Off the VESC
            ser.write(pyvesc.encode(SetCurrent(0)))


if __name__ == "__main__":
    get_values_example()
