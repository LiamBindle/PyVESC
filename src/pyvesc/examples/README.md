# Testing with the Dualshock 4 controller

Bluetooth pairing didn't work out of the box on my Ubuntu 20.04. 
The first connection can be annoying, but once it has paired once, it should pair again automagically even if the controller was tuned off and on again.
My best guess of a procedure is:
1) Connect the controller with the USB câble. The bluetooth manager should ask for permission for the device, accept it. Then unplug the controller.
2) Try conncting with the GUI or with the CLI (below).

Adapt the MAC Address as needed:
```
sudo rfcomm bind /dev/rfcomm0 84:17:66:88:21:F1
sudo chmod 777 /dev/rfcomm0
```

The controller turns blue once it's paired.

Try it with. 
```
python test_controller.py
```
Press the "playstation symbol" button for 10 seconds to shutdown the controller and check that the script detected it (useful as a safety feature).
