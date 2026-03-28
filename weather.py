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

_display = None


def _get_display():
    """Lazily initialize and reuse a single DisplayController."""
    global _display
    if _display is None:
        _display = DisplayController()
    return _display


def update():
    display = _get_display()
    display.set_busy(True)
    try:
        config = None
        weather_data = None
        error_message = None
        try:
            config = Config()
            weather_data = fetch_weather(config)
        except Exception as e:
            print(f"Failed to load weather data: {e}")
            error_message = str(e)

        image = render(config, weather_data, error_message=error_message)
        display.show(image)
    finally:
        display.set_busy(False)


if __name__ == "__main__":
    update()
