"""Tests for constants.py — mapping consistency."""

import os
from src.constants import ICON_MAP, ICON_COLOR_MAP, FontType, Color, COLOR_PALETTE


class TestIconMaps:
    def test_all_weather_icons_have_colors(self):
        """Every weather icon code in ICON_COLOR_MAP should be in ICON_MAP."""
        for key in ICON_COLOR_MAP:
            assert key in ICON_MAP, f"ICON_COLOR_MAP has '{key}' but ICON_MAP doesn't"

    def test_all_weather_codes_have_day_and_night(self):
        """Standard weather codes should have both day (d) and night (n) variants."""
        base_codes = ["01", "02", "03", "04", "09", "10", "11", "13", "50"]
        for code in base_codes:
            assert f"{code}d" in ICON_MAP, f"Missing day icon for {code}"
            assert f"{code}n" in ICON_MAP, f"Missing night icon for {code}"
            assert f"{code}d" in ICON_COLOR_MAP, f"Missing day color for {code}"
            assert f"{code}n" in ICON_COLOR_MAP, f"Missing night color for {code}"

    def test_special_icons_exist(self):
        assert "celsius" in ICON_MAP
        assert "fahrenheit" in ICON_MAP
        assert "sunrise" in ICON_MAP
        assert "sunset" in ICON_MAP

    def test_clock_icons_0_through_12(self):
        for h in range(13):
            assert f"clock{h}" in ICON_MAP, f"Missing clock icon for hour {h}"

    def test_icon_values_are_strings(self):
        for key, value in ICON_MAP.items():
            assert isinstance(value, str), f"ICON_MAP['{key}'] is not a string"
            assert len(value) > 0, f"ICON_MAP['{key}'] is empty"

    def test_icon_colors_are_valid_color_enum(self):
        for key, value in ICON_COLOR_MAP.items():
            assert isinstance(value, Color), f"ICON_COLOR_MAP['{key}'] is not a Color enum"


class TestColorPalette:
    def test_palette_has_entries_for_all_colors(self):
        for color in Color:
            assert color.value < len(COLOR_PALETTE), f"No palette entry for {color.name}"

    def test_palette_values_are_rgb_tuples(self):
        for i, rgb in enumerate(COLOR_PALETTE):
            assert isinstance(rgb, tuple), f"Palette[{i}] is not a tuple"
            assert len(rgb) == 3, f"Palette[{i}] doesn't have 3 components"
            assert all(0 <= c <= 255 for c in rgb), f"Palette[{i}] has out-of-range values"


class TestFontType:
    def test_all_font_paths_are_absolute(self):
        for ft in FontType:
            assert os.path.isabs(ft.value), f"{ft.name} path is not absolute"

    def test_all_font_files_exist(self):
        for ft in FontType:
            assert os.path.isfile(ft.value), f"{ft.name} file not found: {ft.value}"
