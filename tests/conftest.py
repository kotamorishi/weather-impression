"""Shared test fixtures and mock setup for hardware-dependent modules."""

import os
import sys
import types
import pytest
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Mock the inky hardware module before any src imports ---

# The Inky display library is only available on Raspberry Pi hardware.
# We mock it so tests can run on any development machine.

DESATURATED_PALETTE = [
    (0, 0, 0),        # BLACK = 0
    (255, 255, 255),   # WHITE = 1
    (0, 255, 0),       # GREEN = 2
    (0, 0, 255),       # BLUE = 3
    (255, 0, 0),       # RED = 4
    (255, 255, 0),     # YELLOW = 5
    (255, 165, 0),     # ORANGE = 6
    (128, 0, 128),     # placeholder 7
]

mock_inky_uc8159 = types.ModuleType("inky.inky_uc8159")
mock_inky_uc8159.BLACK = 0
mock_inky_uc8159.WHITE = 1
mock_inky_uc8159.GREEN = 2
mock_inky_uc8159.BLUE = 3
mock_inky_uc8159.RED = 4
mock_inky_uc8159.YELLOW = 5
mock_inky_uc8159.ORANGE = 6
mock_inky_uc8159.DESATURATED_PALETTE = DESATURATED_PALETTE
mock_inky_uc8159.Inky = type("Inky", (), {
    "__init__": lambda self: None,
    "set_image": lambda self, img, saturation=0.5: None,
    "show": lambda self: None,
})

mock_inky = types.ModuleType("inky")
mock_inky.inky_uc8159 = mock_inky_uc8159

sys.modules["inky"] = mock_inky
sys.modules["inky.inky_uc8159"] = mock_inky_uc8159


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
