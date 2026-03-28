"""OpenWeatherMap API client."""

import requests

API_BASE = "https://api.openweathermap.org/data/3.0/onecall"


def fetch_weather(config):
    """Fetch weather data from OpenWeatherMap One Call API 3.0.

    Returns the parsed JSON response dict, or None on failure.
    """
    params = {
        "lat": config.lat,
        "lon": config.lon,
        "appid": config.api_key,
        "exclude": "daily",
        "units": "imperial" if config.unit == "imperial" else "metric",
    }
    response = requests.get(API_BASE, params=params, timeout=30)
    response.raise_for_status()
    return response.json()
