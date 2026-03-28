"""Shared test fixtures."""

import os
import sys
import pytest
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# --- Test data fixtures ---

def make_valid_weather_data():
    """Return a complete, valid OpenWeatherMap API response dict."""
    return {
        "current": {
            "dt": 1700000000,
            "temp": 72.5,
            "feels_like": 70.0,
            "pressure": 1013,
            "humidity": 65,
            "sunrise": 1699963200,
            "sunset": 1700000400,
            "weather": [
                {"icon": "01d", "description": "clear sky"}
            ],
        },
        "hourly": [
            {
                "dt": 1700000000 + i * 3600,
                "temp": 70.0 + i * 0.5,
                "feels_like": 68.0 + i * 0.5,
                "pressure": 1013 + i,
                "weather": [
                    {"icon": "01d", "description": "clear sky"}
                ],
            }
            for i in range(48)
        ],
        "alerts": [
            {
                "event": "winter storm warning",
                "sender_name": "NWS",
                "start": 1700000000,
                "description": "Heavy snow expected.\n###\nStay indoors.",
            }
        ],
    }


@pytest.fixture
def valid_weather_data():
    return make_valid_weather_data()


@pytest.fixture
def config_dir():
    """Create a temporary directory with a valid config.txt."""
    tmpdir = tempfile.mkdtemp()
    config_content = """[openweathermap]
LAT=43.6532
LON=-79.3832
API_KEY=test_key_123
mode=0
FORECAST_INTERVAL=1
TEMP_UNIT=imperial
cold_temp=41
hot_temp=88
one_time_message=Hello
"""
    with open(os.path.join(tmpdir, "config.txt"), "w") as f:
        f.write(config_content)
    yield tmpdir
    shutil.rmtree(tmpdir)
