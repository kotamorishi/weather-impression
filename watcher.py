#!/usr/bin/env python3

import signal
import RPi.GPIO as GPIO
import configparser
import os

# config file should be the same folder.
project_root = os.getcwd()
configFilePath = project_root + 'config.txt'

print("""buttons.py - Detect which button has been pressed
This example should demonstrate how to:
 1. set up RPi.GPIO to read buttons,
 2. determine which button has been pressed
Press Ctrl+C to exit!
""")

# Gpio pins for each button (from top to bottom)
BUTTONS = [5, 6, 16, 24]

# These correspond to buttons A, B, C and D respectively
LABELS = ['A', 'B', 'C', 'D']

# Set up RPi.GPIO with the "BCM" numbering scheme
GPIO.setmode(GPIO.BCM)

# Buttons connect to ground when pressed, so we should set them up
# with a "PULL UP", which weakly pulls the input signal to 3.3V.
GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# "handle_button" will be called every time a button is pressed
# It receives one argument: the associated input pin.
def handle_button(pin):
    label = LABELS[BUTTONS.index(pin)]
    print("Button press detected on pin: {} label: {}".format(pin, label))

    if pin == 5:
        config = configparser.ConfigParser()
        config.read_file(open(configFilePath))
        show_warn = config.get('openweathermap', 'SHOW_WARN', raw=False)
        if show_warn == '1':
            config.set("openweathermap", "SHOW_WARN", "0")
            config.set("openweathermap", "one_time_message", "WARNING OFF")
        else:
            config.set("openweathermap", "SHOW_WARN", "1")
            config.set("openweathermap", "one_time_message", "WARNING ON")
        with open(configFilePath, 'w') as configfile:
            config.write(configfile)

        # refresh the screen
        import weather
        weather.update()


        


# Loop through out buttons and attach the "handle_button" function to each
# We're watching the "FALLING" edge (transition from 3.3V to Ground) and
# picking a generous bouncetime of 250ms to smooth out button presses.
for pin in BUTTONS:
    GPIO.add_event_detect(pin, GPIO.FALLING, handle_button, bouncetime=250)

# Finally, since button handlers don't require a "while True" loop,
# we pause the script to prevent it exiting immediately.
signal.pause()