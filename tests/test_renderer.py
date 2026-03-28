"""Tests for renderer.py — rendering helpers and render() with edge cases."""

import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from PIL import Image

from src.renderer import (
    format_temperature, unit_icon, text_size, font_text_width,
    display_color, graph_color, temp_color, get_font,
    render, _get_icon, _get_icon_color,
)
from src.constants import FontType, ICON_MAP, UNIT_IMPERIAL, Color
from src.weather_data import WeatherData


# --- Helper function tests ---

class TestFormatTemperature:
    def test_positive(self):
        assert format_temperature(72.4) == "72"

    def test_negative(self):
        assert format_temperature(-5.3) == "-5"

    def test_zero(self):
        assert format_temperature(0.0) == "0"

    def test_negative_zero(self):
        assert format_temperature(-0.4) == "0"

    def test_rounding_up(self):
        assert format_temperature(72.6) == "73"

    def test_large_value(self):
        assert format_temperature(120.0) == "120"

    def test_very_negative(self):
        assert format_temperature(-40.0) == "-40"


class TestUnitIcon:
    def test_imperial(self):
        assert unit_icon("imperial") == ICON_MAP["fahrenheit"]

    def test_metric(self):
        assert unit_icon("metric") == ICON_MAP["celsius"]

    def test_unknown_defaults_to_celsius(self):
        assert unit_icon("unknown") == ICON_MAP["celsius"]


class TestGetIcon:
    def test_known_icon(self):
        assert _get_icon("01d") == ICON_MAP["01d"]

    def test_unknown_icon_falls_back(self):
        result = _get_icon("99x")
        assert result == ICON_MAP["01d"]


class TestGetIconColor:
    def test_known_icon(self):
        assert _get_icon_color("01d") == Color.ORANGE

    def test_unknown_icon_falls_back_to_black(self):
        assert _get_icon_color("99x") == Color.BLACK


class TestDisplayColor:
    def test_returns_tuple(self):
        result = display_color(0)
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_each_color_index(self):
        for c in Color:
            result = display_color(c)
            assert isinstance(result, tuple)
            assert len(result) == 3


class TestGraphColor:
    def test_returns_normalized_tuple(self):
        result = graph_color(0)
        assert isinstance(result, tuple)
        assert all(0.0 <= c <= 1.0 for c in result)

    def test_each_color_index(self):
        for c in Color:
            result = graph_color(c)
            assert all(0.0 <= v <= 1.0 for v in result)


class TestTempColor:
    def test_cold(self):
        config = MagicMock(cold_temp=41, hot_temp=88)
        assert temp_color(30, config) == (0, 0, 255)

    def test_hot(self):
        config = MagicMock(cold_temp=41, hot_temp=88)
        assert temp_color(95, config) == (255, 0, 0)

    def test_normal(self):
        config = MagicMock(cold_temp=41, hot_temp=88)
        result = temp_color(60, config)
        assert result != (0, 0, 255)
        assert result != (255, 0, 0)

    def test_at_cold_boundary(self):
        config = MagicMock(cold_temp=41, hot_temp=88)
        result = temp_color(41, config)
        assert result != (0, 0, 255)  # not cold at boundary

    def test_at_hot_boundary(self):
        config = MagicMock(cold_temp=41, hot_temp=88)
        result = temp_color(88, config)
        assert result != (255, 0, 0)  # not hot at boundary


class TestTextSize:
    def test_returns_width_height(self):
        img = Image.new("RGB", (100, 100))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        font = get_font(FontType.BOLD, 12)
        w, h = text_size(draw, "Hello", font)
        assert w > 0
        assert h > 0

    def test_empty_string(self):
        img = Image.new("RGB", (100, 100))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        font = get_font(FontType.BOLD, 12)
        w, h = text_size(draw, "", font)
        assert w == 0


class TestFontTextWidth:
    def test_returns_positive_width(self):
        font = get_font(FontType.BOLD, 12)
        w = font_text_width(font, "Hello")
        assert w > 0

    def test_longer_string_is_wider(self):
        font = get_font(FontType.BOLD, 12)
        w_short = font_text_width(font, "Hi")
        w_long = font_text_width(font, "Hello World")
        assert w_long > w_short


class TestGetFont:
    def test_all_font_types_load(self):
        for ft in FontType:
            font = get_font(ft, 16)
            assert font is not None

    def test_different_sizes(self):
        f12 = get_font(FontType.BOLD, 12)
        f48 = get_font(FontType.BOLD, 48)
        assert f12 is not None
        assert f48 is not None


# --- Render function integration tests ---

@pytest.fixture
def tmp_render_dir(tmp_path):
    """Patch TMPFS_PATH to use pytest's tmp_path for graph file output."""
    tmpfs = str(tmp_path) + "/"
    with patch("src.renderer.TMPFS_PATH", tmpfs):
        yield tmpfs


class TestRender:
    def _make_config(self, mode="0"):
        config = MagicMock()
        config.mode = mode
        config.unit = "imperial"
        config.cold_temp = 41.0
        config.hot_temp = 88.0
        config.forecast_interval = 1
        config.consume_one_time_message.return_value = ""
        return config

    def test_render_none_weather_returns_image(self):
        """weather=None should produce an error screen, not crash."""
        img = render(None, None, error_message="Test error")
        assert isinstance(img, Image.Image)
        assert img.size == (600, 448)

    def test_render_none_weather_no_message(self):
        """weather=None with no error_message should still work."""
        img = render(None, None)
        assert isinstance(img, Image.Image)

    def test_render_valid_mode0(self, valid_weather_data):
        config = self._make_config("0")
        weather = WeatherData.from_dict(valid_weather_data)
        img = render(config, weather)
        assert isinstance(img, Image.Image)
        assert img.size == (600, 448)

    def test_render_valid_mode1_with_alerts(self, valid_weather_data):
        config = self._make_config("1")
        weather = WeatherData.from_dict(valid_weather_data)
        img = render(config, weather)
        assert isinstance(img, Image.Image)

    def test_render_mode1_without_alerts(self, valid_weather_data):
        """Mode 1 without alerts should fall back to default."""
        del valid_weather_data["alerts"]
        config = self._make_config("1")
        weather = WeatherData.from_dict(valid_weather_data)
        img = render(config, weather)
        assert isinstance(img, Image.Image)

    def test_render_mode2_graph(self, valid_weather_data, tmp_render_dir):
        """Mode 2 graph rendering should produce an image."""
        config = self._make_config("2")
        weather = WeatherData.from_dict(valid_weather_data)
        img = render(config, weather)
        assert isinstance(img, Image.Image)
        # Verify graph files were created
        assert os.path.exists(tmp_render_dir + "pressure.png")
        assert os.path.exists(tmp_render_dir + "temp.png")

    def test_render_mode2_empty_hourly(self, tmp_render_dir):
        """Mode 2 with no hourly data should not crash."""
        config = self._make_config("2")
        weather = WeatherData.from_dict({
            "current": {"dt": 1700000000, "temp": 70},
            "hourly": [],
        })
        img = render(config, weather)
        assert isinstance(img, Image.Image)

    def test_render_mode2_single_hourly(self, tmp_render_dir):
        """Mode 2 with only one hourly entry should render."""
        config = self._make_config("2")
        weather = WeatherData.from_dict({
            "current": {"dt": 1700000000, "temp": 70},
            "hourly": [
                {"dt": 1700003600, "temp": 71, "feels_like": 69, "pressure": 1013},
            ],
        })
        img = render(config, weather)
        assert isinstance(img, Image.Image)

    def test_render_mode2_extreme_pressures(self, tmp_render_dir):
        """Mode 2 with extreme pressure values should not crash."""
        config = self._make_config("2")
        weather = WeatherData.from_dict({
            "current": {"dt": 1700000000, "temp": 70},
            "hourly": [
                {"dt": 1700000000 + i * 3600, "temp": 70, "feels_like": 68, "pressure": 950 + i * 5}
                for i in range(10)
            ],
        })
        img = render(config, weather)
        assert isinstance(img, Image.Image)

    def test_render_mode3_sunrise_icon(self, valid_weather_data):
        config = self._make_config("3")
        weather = WeatherData.from_dict(valid_weather_data)
        img = render(config, weather)
        assert isinstance(img, Image.Image)

    def test_render_mode3_zero_sunrise_sunset(self):
        """Mode 3 with zero timestamps should not crash."""
        config = self._make_config("3")
        weather = WeatherData.from_dict({
            "current": {"dt": 0, "sunrise": 0, "sunset": 0},
        })
        img = render(config, weather)
        assert isinstance(img, Image.Image)

    def test_render_mode4_sunrise_graph(self, valid_weather_data, tmp_render_dir):
        """Mode 4 sunrise graph should produce an image."""
        config = self._make_config("4")
        weather = WeatherData.from_dict(valid_weather_data)
        img = render(config, weather)
        assert isinstance(img, Image.Image)
        assert os.path.exists(tmp_render_dir + "day.png")

    def test_render_mode4_zero_sunrise_sunset(self, tmp_render_dir):
        """Mode 4 with zero timestamps should not crash."""
        config = self._make_config("4")
        weather = WeatherData.from_dict({
            "current": {"dt": 0, "sunrise": 0, "sunset": 0},
        })
        img = render(config, weather)
        assert isinstance(img, Image.Image)

    def test_render_empty_weather_data(self):
        """Completely empty dict should not crash."""
        config = self._make_config("0")
        weather = WeatherData.from_dict({})
        img = render(config, weather)
        assert isinstance(img, Image.Image)

    def test_render_missing_hourly(self):
        """No hourly data should not crash in forecast mode."""
        config = self._make_config("0")
        weather = WeatherData.from_dict({"current": {"dt": 100}})
        img = render(config, weather)
        assert isinstance(img, Image.Image)

    def test_render_unknown_icon_code(self):
        """Unknown icon code in weather data should not crash."""
        config = self._make_config("0")
        data = {
            "current": {
                "dt": 1700000000,
                "temp": 72,
                "feels_like": 70,
                "pressure": 1013,
                "weather": [{"icon": "UNKNOWN", "description": "mystery"}],
            },
            "hourly": [],
        }
        weather = WeatherData.from_dict(data)
        img = render(config, weather)
        assert isinstance(img, Image.Image)

    def test_render_with_one_time_message(self, valid_weather_data):
        config = self._make_config("0")
        config.consume_one_time_message.return_value = "MODE:Forecast"
        weather = WeatherData.from_dict(valid_weather_data)
        img = render(config, weather)
        assert isinstance(img, Image.Image)

    def test_render_all_zeros(self):
        """All zero values should not crash."""
        config = self._make_config("0")
        weather = WeatherData.from_dict({
            "current": {"dt": 0, "temp": 0, "feels_like": 0, "pressure": 0},
            "hourly": [],
        })
        img = render(config, weather)
        assert isinstance(img, Image.Image)

    def test_render_negative_temperatures(self):
        """Negative temps should not crash."""
        config = self._make_config("0")
        weather = WeatherData.from_dict({
            "current": {
                "dt": 1700000000,
                "temp": -40,
                "feels_like": -50,
                "pressure": 980,
                "weather": [{"icon": "13d", "description": "snow"}],
            },
            "hourly": [],
        })
        img = render(config, weather)
        assert isinstance(img, Image.Image)

    def test_render_extreme_temperatures(self):
        """Extreme temps should not crash."""
        config = self._make_config("0")
        weather = WeatherData.from_dict({
            "current": {
                "dt": 1700000000,
                "temp": 150,
                "feels_like": 160,
                "pressure": 1050,
                "weather": [{"icon": "01d", "description": "hot"}],
            },
            "hourly": [],
        })
        img = render(config, weather)
        assert isinstance(img, Image.Image)

    def test_render_forecast_short_hourly(self):
        """Fewer than expected hourly entries should not crash."""
        config = self._make_config("0")
        config.forecast_interval = 3
        weather = WeatherData.from_dict({
            "current": {"dt": 1700000000, "temp": 70},
            "hourly": [
                {"dt": 1700003600, "temp": 71, "weather": [{"icon": "01d"}]},
            ],
        })
        img = render(config, weather)
        assert isinstance(img, Image.Image)

    def test_render_forecast_large_interval(self):
        """Large forecast interval with limited hourly data should not crash."""
        config = self._make_config("0")
        config.forecast_interval = 12
        weather = WeatherData.from_dict({
            "current": {"dt": 1700000000, "temp": 70},
            "hourly": [
                {"dt": 1700000000 + i * 3600, "temp": 70 + i}
                for i in range(48)
            ],
        })
        img = render(config, weather)
        assert isinstance(img, Image.Image)

    def test_render_mode2_full_48_hourly(self, valid_weather_data, tmp_render_dir):
        """Mode 2 with full 48 hourly entries."""
        config = self._make_config("2")
        weather = WeatherData.from_dict(valid_weather_data)
        img = render(config, weather)
        assert isinstance(img, Image.Image)

    def test_render_unknown_mode_falls_back(self, valid_weather_data):
        """Unknown mode should fall back to default (mode 0 behavior)."""
        config = self._make_config("99")
        weather = WeatherData.from_dict(valid_weather_data)
        img = render(config, weather)
        assert isinstance(img, Image.Image)

    def test_render_mode_metric(self, valid_weather_data):
        """Metric unit rendering should work."""
        config = self._make_config("0")
        config.unit = "metric"
        weather = WeatherData.from_dict(valid_weather_data)
        img = render(config, weather)
        assert isinstance(img, Image.Image)

    def test_render_alert_with_urls(self):
        """Alert with URLs in description should be cleaned."""
        config = self._make_config("1")
        data = {
            "current": {"dt": 1700000000, "temp": 70},
            "alerts": [{
                "event": "severe weather",
                "sender_name": "NWS",
                "start": 1700000000,
                "description": "Warning:\n###\nhttps://example.com\n\nDetails here.",
            }],
        }
        weather = WeatherData.from_dict(data)
        img = render(config, weather)
        assert isinstance(img, Image.Image)

    def test_render_alert_empty_description(self):
        """Alert with empty fields should not crash."""
        config = self._make_config("1")
        data = {
            "current": {"dt": 1700000000, "temp": 70},
            "alerts": [{
                "event": "",
                "sender_name": "",
                "start": 0,
                "description": "",
            }],
        }
        weather = WeatherData.from_dict(data)
        img = render(config, weather)
        assert isinstance(img, Image.Image)
