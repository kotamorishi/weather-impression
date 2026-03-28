"""OpenWeatherMap API client."""

import requests

API_BASE = "https://api.openweathermap.org/data/3.0/onecall"


def fetch_weather(config):
    """Fetch weather data from OpenWeatherMap One Call API 3.0.

    Returns:
        dict: The parsed JSON response.

    Raises:
        requests.RequestException: If the HTTP request fails or a non-success
            status code is returned.
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
