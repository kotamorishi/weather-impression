"""Display constants, icon/color mappings, and font definitions.

This module is hardware-independent — no imports from inky or gpiod.
Color palette values are defined here directly so that renderer and
tests can work without the Inky hardware library installed.
"""

import os
from enum import Enum, IntEnum

# --- Project paths ---

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMPFS_PATH = "/dev/shm/"

# --- Display settings ---

CANVAS_WIDTH = 600
CANVAS_HEIGHT = 448
CANVAS_SIZE = (CANVAS_WIDTH, CANVAS_HEIGHT)
SATURATION = 0.5

UNIT_IMPERIAL = "imperial"

# --- Color palette (matches Inky Impression DESATURATED_PALETTE) ---


class Color(IntEnum):
    BLACK = 0
    WHITE = 1
    GREEN = 2
    BLUE = 3
    RED = 4
    YELLOW = 5
    ORANGE = 6
    CLEAN = 7


# RGB values matching inky.inky_uc8159.DESATURATED_PALETTE
COLOR_PALETTE = [
    (0, 0, 0),        # BLACK
    (255, 255, 255),   # WHITE
    (0, 255, 0),       # GREEN
    (0, 0, 255),       # BLUE
    (255, 0, 0),       # RED
    (255, 255, 0),     # YELLOW
    (255, 128, 0),     # ORANGE
    (255, 255, 255),   # CLEAN (same as white)
]

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

# --- Icon color mappings (Color enum per weather icon) ---

ICON_COLOR_MAP = {
    "01d": Color.ORANGE, "01n": Color.YELLOW,
    "02d": Color.BLACK, "02n": Color.BLACK,
    "03d": Color.BLACK, "03n": Color.BLACK,
    "04d": Color.BLACK, "04n": Color.BLACK,
    "09d": Color.BLACK, "09n": Color.BLACK,
    "10d": Color.BLUE, "10n": Color.BLUE,
    "11d": Color.RED, "11n": Color.RED,
    "13d": Color.BLUE, "13n": Color.BLUE,
    "50d": Color.BLACK, "50n": Color.BLACK,
    "sunrise": Color.BLACK, "sunset": Color.BLACK,
}
