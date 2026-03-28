#!/usr/bin/env python3
"""Weather Impression - main entry point."""

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.weather_api import fetch_weather
from src.weather_data import WeatherData
from src.renderer import render
from src.display import DisplayController

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

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
        weather = None
        error_message = None
        try:
            config = Config()
            raw_data = fetch_weather(config)
            weather = WeatherData.from_dict(raw_data)
            logger.info("Weather data loaded successfully")
        except Exception as e:
            logger.error("Failed to load weather data: %s", e)
            error_message = str(e)

        image = render(config, weather, error_message=error_message)
        display.show(image)
        logger.info("Display updated")
    finally:
        display.set_busy(False)


if __name__ == "__main__":
    update()
