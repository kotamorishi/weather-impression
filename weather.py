#!/usr/bin/env python3
"""Weather Impression - main entry point."""

import sys
import os

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.weather_api import fetch_weather
from src.renderer import render
from src.display import DisplayController


def update():
    display = DisplayController()
    display.set_busy(True)
    try:
        try:
            config = Config()
            weather_data = fetch_weather(config)
        except Exception as e:
            print(f"Failed to load weather data: {e}")
            weather_data = None
            config = Config.__new__(Config)
            config.one_time_message = str(e)
            config.mode = "0"

        image = render(config, weather_data)
        display.show(image)
    finally:
        display.set_busy(False)


if __name__ == "__main__":
    update()
