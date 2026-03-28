#!/usr/bin/env python3
"""Button watcher and scheduled screen refresh for Weather Impression."""

import sys
import os
from datetime import timedelta

import gpiod
from gpiod.line import Bias, Edge
import schedule

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import Config

# GPIO button pins (top to bottom: A, B, C, D)
BUTTONS = [5, 6, 16, 24]

# Button-to-mode mapping
BUTTON_ACTIONS = {
    5: ("mode", "0", "MODE:Forecast"),
    6: ("mode", "2", "MODE:Graph"),
    16: ("mode", "1", "MODE:Alert"),
}

request = gpiod.request_lines(
    "/dev/gpiochip0",
    consumer="weather-impression-watcher",
    config={
        tuple(BUTTONS): gpiod.LineSettings(
            edge_detection=Edge.FALLING,
            bias=Bias.PULL_UP,
            debounce_period=timedelta(milliseconds=250),
        )
    },
)


def refresh_screen():
    import weather
    weather.update()


def handle_button(pin):
    config = Config()

    if pin in BUTTON_ACTIONS:
        key, value, message = BUTTON_ACTIONS[pin]
        config.set_value("one_time_message", message)
        config.set_value(key, value)
    elif pin == 24:
        # Toggle temperature unit
        if config.unit == "imperial":
            config.set_value("one_time_message", "Unit:Metric")
            config.set_value("TEMP_UNIT", "metric")
        else:
            config.set_value("one_time_message", "Unit:Imperial")
            config.set_value("TEMP_UNIT", "imperial")

    try:
        refresh_screen()
    except Exception as e:
        print(f"Weather update failed: {e}")


# Schedule hourly screen refresh
schedule.every().hour.at(":01").do(refresh_screen)

# Main loop: poll for button events and run scheduled tasks
while True:
    if request.wait_edge_events(timeout=timedelta(seconds=1)):
        events = request.read_edge_events()
        for event in events:
            handle_button(event.line_offset)
    schedule.run_pending()
