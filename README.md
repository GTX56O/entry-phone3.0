To start a working entry phone and gate control, run the app.py code on the raspberry pi, run the index.html page on the raspberry pi,
run arduino.ino file on arduino. Download all required libraries on raspberry pi

Change the small gate PIN, login pin to the intercom page, IP of the device to which the image from the intercom and the conversation will be sent, launch the intercom website and log in with the login and password provided in the configuration.

On the NFC card, write down the code that you enter into the intercom to open the gate. After entering the correct code and pressing # or presenting the NFC card with the correct code, the small gate will open.

You can also call the * button on the keyboard, this device will ring at home, there is also a relay provided in the diagram that rings the bell in our house.

The entry phone also works with opening the gate on Arduino, we can open the gate using a remote control, or when someone rings our entry phone , we can open or close it from the entry phone.

!! Raspberry pi must be connected to the ethernet or wifi (recommended ethernet cable) !!

For the entry phone and gate control project we will need:

Arduino
raspberry pi 2/3/4
433MHz remote controls
433mhz receiver
12 or 24v gate actuators
infrared sensors for barma
warning light
camera for raspberry pi
4x3 keyboard
NFC card reader
nfc cards
power supply (5v for raspberry and arduino, 12v or 24v for our actuators)
electromages to our small gate
the housing of our intercom - raspberry pi (for example, printed on a 3D printer)
Housing for the gate mechanism
4 5v relays
2 5v direction changers (double relays for one coil)
cables

# entry-phone3.0
