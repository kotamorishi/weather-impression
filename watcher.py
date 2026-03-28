#!/usr/bin/env python3
"""Button watcher and scheduled screen refresh for Weather Impression."""

import logging
import sys
import os
from datetime import timedelta

import gpiod
from gpiod.line import Bias, Edge
import schedule

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# GPIO button pins (top to bottom: A, B, C, D)
BUTTONS = [5, 6, 16, 24]

# Button-to-mode mapping
BUTTON_ACTIONS = {
    5: ("mode", "0", "MODE:Forecast"),
    6: ("mode", "2", "MODE:Graph"),
    16: ("mode", "1", "MODE:Alert"),
}


def refresh_screen():
    import weather
    weather.update()


def handle_button(pin):
    logger.info("Button pressed: pin %d", pin)
    try:
        config = Config()
    except Exception as e:
        logger.error("Failed to load config: %s", e)
        return

    if pin in BUTTON_ACTIONS:
        key, value, message = BUTTON_ACTIONS[pin]
        config.set_values({"one_time_message": message, key: value})
    elif pin == 24:
        if config.unit == "imperial":
            config.set_values({"one_time_message": "Unit:Metric", "TEMP_UNIT": "metric"})
        else:
            config.set_values({"one_time_message": "Unit:Imperial", "TEMP_UNIT": "imperial"})

    try:
        refresh_screen()
    except Exception as e:
        logger.error("Weather update failed: %s", e)


def main():
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

    schedule.every().hour.at(":01").do(refresh_screen)

    logger.info("Watcher started, listening for button events")

    while True:
        if request.wait_edge_events(timeout=timedelta(seconds=1)):
            events = request.read_edge_events()
            for event in events:
                handle_button(event.line_offset)
        schedule.run_pending()


if __name__ == "__main__":
    main()
