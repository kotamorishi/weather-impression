#!/usr/bin/env python3
"""Interactive configuration editor for Weather Impression."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import shutil
from src.config import Config, CONFIG_PATH
from src.constants import PROJECT_ROOT


class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[33m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"


def colored(text, color):
    return f"{color}{text}{Colors.END}"


def prompt(label, current_value):
    """Prompt user for input, returning current value if empty."""
    print(f"Please enter {colored(label, Colors.BOLD)}")
    value = input()
    if not value:
        value = current_value
        print(colored(f"  {label}: {value}", Colors.CYAN))
    return value


def main():
    print(colored("""
  __      __               __  .__
 /  \\    /  \\ ____ _____ _/  |_|  |__   ___________
 \\   \\/\\/   // __ \\\\__  \\\\   __\\  |  \\_/ __ \\_  __ \\
  \\        /\\  ___/ / __ \\|  | |   Y  \\  ___/|  | \\/
   \\__/\\  /  \\___  >____  /__| |___|  /\\___  >__|
        \\/       \\/     \\/          \\/     \\/
    """, Colors.CYAN))

    print(colored(""".__
|__| _____ _____________   ____   ______ _____|__| ____   ____
|  |/     \\\\____ \\_  __ \\_/ __ \\ /  ___//  ___/  |/  _ \\ /    \\
|  |  Y Y  \\  |_> >  | \\/\\  ___/ \\___ \\ \\___ \\|  (  <_> )   |  \\
|__|__|_|  /   __/|__|    \\___  >____  >____  >__|\\____/|___|  /
         \\/|__|               \\/     \\/     \\/               \\/
    """, Colors.YELLOW))

    print(colored(f"Config file: {CONFIG_PATH}", Colors.BLUE))

    if not os.path.exists(CONFIG_PATH):
        default_path = os.path.join(PROJECT_ROOT, "config.txt.default")
        if os.path.exists(default_path):
            shutil.copy(default_path, CONFIG_PATH)
            print(colored("Created config.txt from default template.", Colors.CYAN))
        else:
            print(colored(f"Error: {CONFIG_PATH} not found and no default template available.", Colors.RED))
            return

    config = Config()

    print(colored("Note: Press enter to keep the current (default) value.", Colors.CYAN))

    latitude = prompt("Latitude", config.lat)
    longitude = prompt("Longitude", config.lon)
    api_key = prompt("API Key", config.api_key)
    print(colored("You can get your key at https://openweathermap.org", Colors.BLUE))

    while True:
        raw_interval = prompt("Forecast interval (hours, 1-12)", str(config.forecast_interval))
        try:
            interval_int = int(raw_interval)
            if 1 <= interval_int <= 12:
                forecast_interval = str(interval_int)
                break
            else:
                print(colored("Forecast interval must be between 1 and 12.", Colors.RED))
        except ValueError:
            print(colored("Forecast interval must be an integer between 1 and 12.", Colors.RED))

    print()
    print(f"Latitude:  {colored(latitude, Colors.GREEN)}")
    print(f"Longitude: {colored(longitude, Colors.GREEN)}")
    print(f"API key:   {colored(api_key, Colors.GREEN)}")
    print(f"Interval:  {colored(forecast_interval, Colors.GREEN)}")

    print(colored("\nDo you want to save the configuration? (y/n)", Colors.YELLOW))
    if input().strip().lower() == "y":
        config.set_values({
            "LAT": latitude,
            "LON": longitude,
            "API_KEY": api_key,
            "FORECAST_INTERVAL": forecast_interval,
            "one_time_message": "Configured.",
            "mode": "2",
            "TEMP_UNIT": "metric",
            "cold_temp": "7",
            "hot_temp": "27",
        })
        print(colored("Configuration saved.", Colors.CYAN))
    else:
        print(colored("Configuration not saved.", Colors.RED))


if __name__ == "__main__":
    main()
