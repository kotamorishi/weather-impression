"""Configuration management for weather-impression."""

import configparser
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.txt")
TMPFS_PATH = "/dev/shm/"

CANVAS_WIDTH = 600
CANVAS_HEIGHT = 448
CANVAS_SIZE = (CANVAS_WIDTH, CANVAS_HEIGHT)
SATURATION = 0.5

UNIT_IMPERIAL = "imperial"


class Config:
    """Loads and manages weather station configuration from config.txt."""

    def __init__(self, path=CONFIG_PATH):
        self.path = path
        self._parser = configparser.ConfigParser()
        self._parser.read_file(open(self.path))
        section = "openweathermap"

        self.lat = self._parser.get(section, "LAT")
        self.lon = self._parser.get(section, "LON")
        self.api_key = self._parser.get(section, "API_KEY")
        self.mode = self._parser.get(section, "mode")
        self.forecast_interval = int(self._parser.get(section, "FORECAST_INTERVAL"))
        self.unit = self._parser.get(section, "TEMP_UNIT")
        self.cold_temp = float(self._parser.get(section, "cold_temp"))
        self.hot_temp = float(self._parser.get(section, "hot_temp"))

        try:
            self.one_time_message = self._parser.get(section, "one_time_message")
        except (configparser.NoSectionError, configparser.NoOptionError):
            self.one_time_message = ""

    def consume_one_time_message(self):
        """Read and clear the one-time message from the config file."""
        msg = self.one_time_message
        if msg:
            self._parser.set("openweathermap", "one_time_message", "")
            with open(self.path, "w") as f:
                self._parser.write(f)
            self.one_time_message = ""
        return msg

    def set_value(self, key, value):
        """Set a config value and save to disk."""
        self._parser.set("openweathermap", key, value)
        with open(self.path, "w") as f:
            self._parser.write(f)
