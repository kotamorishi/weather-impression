"""Tests for weather_data.py — JSON parsing with edge cases."""

import pytest
from src.weather_data import (
    WeatherCondition, CurrentWeather, HourlyForecast,
    WeatherAlert, WeatherData, _int, _float, _str,
)


# --- Safe type conversion ---

class TestSafeConversion:
    def test_int_normal(self):
        assert _int(42) == 42

    def test_int_from_string(self):
        assert _int("42") == 42

    def test_int_from_float(self):
        assert _int(3.7) == 3

    def test_int_from_none(self):
        assert _int(None) == 0

    def test_int_from_invalid_string(self):
        assert _int("abc") == 0

    def test_int_from_list(self):
        assert _int([1, 2]) == 0

    def test_float_normal(self):
        assert _float(3.14) == 3.14

    def test_float_from_string(self):
        assert _float("3.14") == 3.14

    def test_float_from_none(self):
        assert _float(None) == 0.0

    def test_float_from_invalid_string(self):
        assert _float("not_a_number") == 0.0

    def test_float_from_dict(self):
        assert _float({"value": 1}) == 0.0


class TestStrConversion:
    def test_str_normal(self):
        assert _str("hello") == "hello"

    def test_str_from_int(self):
        assert _str(123) == "123"

    def test_str_from_none_returns_default(self):
        assert _str(None) == ""

    def test_str_from_none_with_custom_default(self):
        assert _str(None, "fallback") == "fallback"

    def test_str_empty_string(self):
        assert _str("") == ""


# --- WeatherCondition ---

class TestWeatherCondition:
    def test_from_valid_dict(self):
        c = WeatherCondition.from_dict({"icon": "10d", "description": "rain"})
        assert c.icon == "10d"
        assert c.description == "rain"

    def test_from_empty_dict(self):
        c = WeatherCondition.from_dict({})
        assert c.icon == "01d"
        assert c.description == ""

    def test_from_none(self):
        c = WeatherCondition.from_dict(None)
        assert c.icon == "01d"

    def test_from_string(self):
        c = WeatherCondition.from_dict("not a dict")
        assert c.icon == "01d"

    def test_from_list(self):
        c = WeatherCondition.from_dict([1, 2, 3])
        assert c.icon == "01d"

    def test_icon_as_int(self):
        c = WeatherCondition.from_dict({"icon": 123, "description": 456})
        assert c.icon == "123"
        assert c.description == "456"

    def test_missing_icon(self):
        c = WeatherCondition.from_dict({"description": "cloudy"})
        assert c.icon == "01d"
        assert c.description == "cloudy"

    def test_missing_description(self):
        c = WeatherCondition.from_dict({"icon": "04n"})
        assert c.icon == "04n"
        assert c.description == ""

    def test_null_icon(self):
        """JSON null for icon should not produce "None" string."""
        c = WeatherCondition.from_dict({"icon": None, "description": None})
        assert c.icon == "01d"
        assert c.description == ""


# --- CurrentWeather ---

class TestCurrentWeather:
    def test_from_valid_dict(self, valid_weather_data):
        raw = valid_weather_data["current"]
        cw = CurrentWeather.from_dict(raw)
        assert cw.dt == 1700000000
        assert cw.temp == 72.5
        assert cw.feels_like == 70.0
        assert cw.pressure == 1013
        assert cw.humidity == 65
        assert cw.condition.icon == "01d"
        assert cw.condition.description == "clear sky"

    def test_from_empty_dict(self):
        cw = CurrentWeather.from_dict({})
        assert cw.dt == 0
        assert cw.temp == 0.0
        assert cw.condition.icon == "01d"

    def test_from_none(self):
        cw = CurrentWeather.from_dict(None)
        assert cw.dt == 0
        assert cw.temp == 0.0

    def test_from_string(self):
        cw = CurrentWeather.from_dict("garbage")
        assert cw.dt == 0

    def test_weather_empty_list(self):
        cw = CurrentWeather.from_dict({"weather": []})
        assert cw.condition.icon == "01d"

    def test_weather_not_a_list(self):
        cw = CurrentWeather.from_dict({"weather": "not a list"})
        assert cw.condition.icon == "01d"

    def test_weather_list_with_garbage(self):
        cw = CurrentWeather.from_dict({"weather": [42]})
        assert cw.condition.icon == "01d"

    def test_temp_as_string(self):
        cw = CurrentWeather.from_dict({"temp": "72.5"})
        assert cw.temp == 72.5

    def test_temp_as_invalid_string(self):
        cw = CurrentWeather.from_dict({"temp": "hot"})
        assert cw.temp == 0.0

    def test_pressure_as_none(self):
        cw = CurrentWeather.from_dict({"pressure": None})
        assert cw.pressure == 0

    def test_dt_as_float(self):
        cw = CurrentWeather.from_dict({"dt": 1700000000.5})
        assert cw.dt == 1700000000

    def test_extra_fields_ignored(self):
        cw = CurrentWeather.from_dict({"dt": 100, "unknown_field": "value"})
        assert cw.dt == 100

    def test_nested_dict_in_temp(self):
        cw = CurrentWeather.from_dict({"temp": {"day": 72}})
        assert cw.temp == 0.0


# --- HourlyForecast ---

class TestHourlyForecast:
    def test_from_valid_dict(self):
        hf = HourlyForecast.from_dict({
            "dt": 1700003600,
            "temp": 71.0,
            "feels_like": 69.0,
            "pressure": 1014,
            "weather": [{"icon": "02d", "description": "few clouds"}],
        })
        assert hf.dt == 1700003600
        assert hf.temp == 71.0
        assert hf.condition.icon == "02d"

    def test_from_empty_dict(self):
        hf = HourlyForecast.from_dict({})
        assert hf.dt == 0
        assert hf.temp == 0.0

    def test_from_none(self):
        hf = HourlyForecast.from_dict(None)
        assert hf.dt == 0

    def test_from_int(self):
        hf = HourlyForecast.from_dict(42)
        assert hf.dt == 0

    def test_weather_missing(self):
        hf = HourlyForecast.from_dict({"dt": 100})
        assert hf.condition.icon == "01d"


# --- WeatherAlert ---

class TestWeatherAlert:
    def test_from_valid_dict(self):
        a = WeatherAlert.from_dict({
            "event": "tornado warning",
            "sender_name": "NWS",
            "start": 1700000000,
            "description": "Take shelter immediately.",
        })
        assert a.event == "tornado warning"
        assert a.sender_name == "NWS"
        assert a.start == 1700000000
        assert a.description == "Take shelter immediately."

    def test_from_empty_dict(self):
        a = WeatherAlert.from_dict({})
        assert a.event == ""
        assert a.start == 0

    def test_from_none(self):
        a = WeatherAlert.from_dict(None)
        assert a.event == ""

    def test_from_list(self):
        a = WeatherAlert.from_dict([1, 2, 3])
        assert a.event == ""

    def test_event_as_int(self):
        a = WeatherAlert.from_dict({"event": 123})
        assert a.event == "123"

    def test_start_as_string(self):
        a = WeatherAlert.from_dict({"start": "1700000000"})
        assert a.start == 1700000000

    def test_start_as_invalid(self):
        a = WeatherAlert.from_dict({"start": "not a timestamp"})
        assert a.start == 0

    def test_null_event_and_description(self):
        """JSON null values should not produce "None" string."""
        a = WeatherAlert.from_dict({"event": None, "sender_name": None, "description": None})
        assert a.event == ""
        assert a.sender_name == ""
        assert a.description == ""


# --- WeatherData (top level) ---

class TestWeatherData:
    def test_from_valid_data(self, valid_weather_data):
        wd = WeatherData.from_dict(valid_weather_data)
        assert wd.current.dt == 1700000000
        assert wd.current.temp == 72.5
        assert len(wd.hourly) == 48
        assert len(wd.alerts) == 1
        assert wd.alerts[0].event == "winter storm warning"

    def test_from_empty_dict(self):
        wd = WeatherData.from_dict({})
        assert wd.current.dt == 0
        assert len(wd.hourly) == 0
        assert len(wd.alerts) == 0

    def test_from_none(self):
        wd = WeatherData.from_dict(None)
        assert wd.current.dt == 0
        assert len(wd.hourly) == 0

    def test_from_string(self):
        wd = WeatherData.from_dict("not a dict")
        assert wd.current.dt == 0

    def test_from_int(self):
        wd = WeatherData.from_dict(42)
        assert wd.current.dt == 0

    def test_from_list(self):
        wd = WeatherData.from_dict([1, 2, 3])
        assert wd.current.dt == 0

    def test_hourly_not_a_list(self):
        wd = WeatherData.from_dict({"hourly": "not a list"})
        assert len(wd.hourly) == 0

    def test_hourly_with_mixed_types(self):
        wd = WeatherData.from_dict({
            "hourly": [
                {"dt": 100, "temp": 70},
                42,
                None,
                "garbage",
                {"dt": 200, "temp": 75},
            ]
        })
        assert len(wd.hourly) == 5
        assert wd.hourly[0].dt == 100
        assert wd.hourly[1].dt == 0  # non-dict falls back
        assert wd.hourly[4].dt == 200

    def test_alerts_not_a_list(self):
        wd = WeatherData.from_dict({"alerts": "not a list"})
        assert len(wd.alerts) == 0

    def test_alerts_with_garbage(self):
        wd = WeatherData.from_dict({"alerts": [None, 42, {"event": "flood"}]})
        assert len(wd.alerts) == 3
        assert wd.alerts[0].event == ""
        assert wd.alerts[2].event == "flood"

    def test_current_not_a_dict(self):
        wd = WeatherData.from_dict({"current": "not a dict"})
        assert wd.current.dt == 0

    def test_current_as_list(self):
        wd = WeatherData.from_dict({"current": [1, 2, 3]})
        assert wd.current.dt == 0

    def test_no_alerts_key(self):
        data = {"current": {"dt": 100}, "hourly": []}
        wd = WeatherData.from_dict(data)
        assert len(wd.alerts) == 0

    def test_completely_wrong_structure(self):
        wd = WeatherData.from_dict({"foo": "bar", "baz": [1, 2, 3]})
        assert wd.current.dt == 0
        assert len(wd.hourly) == 0
        assert len(wd.alerts) == 0

    def test_deeply_nested_wrong_types(self):
        wd = WeatherData.from_dict({
            "current": {
                "dt": {"nested": "dict"},
                "temp": [1, 2, 3],
                "weather": {"not": "a list"},
            }
        })
        assert wd.current.dt == 0
        assert wd.current.temp == 0.0
        assert wd.current.condition.icon == "01d"
