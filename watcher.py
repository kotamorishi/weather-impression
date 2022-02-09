#!/usr/bin/env python3

import signal
import RPi.GPIO as GPIO
import configparser
import os

# config file should be the same folder.
os.chdir('/home/pi/weather-impression')
project_root = os.getcwd()
configFilePath = project_root + '/config.txt'


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

    config = configparser.ConfigParser()
    config.read_file(open(configFilePath))

    if pin == 5:
        mode = config.get('openweathermap', 'mode', raw=False)
        if mode == '1': # already in show warning mode, this set back to default.
            config.set("openweathermap", "mode", "0")
            config.set("openweathermap", "one_time_message", "MODE:Forecast")
        else:
            config.set("openweathermap", "mode", "1")
            config.set("openweathermap", "one_time_message", "MODE:Alert message")
        with open(configFilePath, 'w') as configfile:
            config.write(configfile)

    if pin == 6:
        mode = config.get('openweathermap', 'mode', raw=False)
        if mode == '2': # already in graph mode, this set back to default.
            config.set("openweathermap", "one_time_message", "MODE:Forecast")
            config.set("openweathermap", "mode", "0")
        else:
            config.set("openweathermap", "mode", "2")
            config.set("openweathermap", "one_time_message", "MODE:Graph")
        with open(configFilePath, 'w') as configfile:
            config.write(configfile)

    # refresh the screen
    try:
        import weather
        weather.update()
    except:
        print("Weather update failed.")
        pass



# Loop through out buttons and attach the "handle_button" function to each
# We're watching the "FALLING" edge (transition from 3.3V to Ground) and
# picking a generous bouncetime of 250ms to smooth out button presses.
for pin in BUTTONS:
    GPIO.add_event_detect(pin, GPIO.FALLING, handle_button, bouncetime=10000)

# Finally, since button handlers don't require a "while True" loop,
# we pause the script to prevent it exiting immediately.
signal.pause()
