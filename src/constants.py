"""Display constants, icon/color mappings, and font definitions."""

import os
from enum import Enum

from inky.inky_uc8159 import (
    BLACK, WHITE, GREEN, RED, YELLOW, ORANGE, BLUE,
    DESATURATED_PALETTE as COLOR_PALETTE,
)

# --- Project paths ---

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMPFS_PATH = "/dev/shm/"

# --- Display settings ---

CANVAS_WIDTH = 600
CANVAS_HEIGHT = 448
CANVAS_SIZE = (CANVAS_WIDTH, CANVAS_HEIGHT)
SATURATION = 0.5

UNIT_IMPERIAL = "imperial"

# --- Font definitions ---


class FontType(Enum):
    THIN = os.path.join(PROJECT_ROOT, "fonts", "Roboto-Thin.ttf")
    LIGHT = os.path.join(PROJECT_ROOT, "fonts", "Roboto-Light.ttf")
    BOLD = os.path.join(PROJECT_ROOT, "fonts", "Roboto-Black.ttf")
    ICON = os.path.join(PROJECT_ROOT, "fonts", "weathericons-regular-webfont.ttf")


# --- Icon mappings (Weather Icons font codepoints) ---

ICON_MAP = {
    "01d": "\uf00d", "01n": "\uf02e",   # clear sky
    "02d": "\uf002", "02n": "\uf031",   # few clouds
    "03d": "\uf041", "03n": "\uf041",   # scattered clouds
    "04d": "\uf013", "04n": "\uf013",   # broken clouds
    "09d": "\uf004", "09n": "\uf024",   # shower rain
    "10d": "\uf00b", "10n": "\uf02b",   # rain
    "11d": "\uf00e", "11n": "\uf02c",   # thunderstorm
    "13d": "\uf00a", "13n": "\uf038",   # snow
    "50d": "\uf003", "50n": "\uf023",   # fog
    "celsius": "\uf03c",
    "fahrenheit": "\uf045",
    "sunrise": "\uf051",
    "sunset": "\uf052",
}

# Clock icons for 12-hour display
ICON_MAP["clock0"] = "\uf089"
for _h in range(1, 13):
    ICON_MAP[f"clock{_h}"] = chr(0xF089 + _h)
ICON_MAP["clock12"] = "\uf089"

# --- Icon color mappings (palette index per weather icon) ---

ICON_COLOR_MAP = {
    "01d": ORANGE, "01n": YELLOW,
    "02d": BLACK, "02n": BLACK,
    "03d": BLACK, "03n": BLACK,
    "04d": BLACK, "04n": BLACK,
    "09d": BLACK, "09n": BLACK,
    "10d": BLUE, "10n": BLUE,
    "11d": RED, "11n": RED,
    "13d": BLUE, "13n": BLUE,
    "50d": BLACK, "50n": BLACK,
    "sunrise": BLACK, "sunset": BLACK,
}
