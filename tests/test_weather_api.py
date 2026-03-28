"""Tests for weather_api.py."""

import pytest
from unittest.mock import patch, MagicMock
from src.weather_api import fetch_weather


class TestFetchWeather:
    def _make_config(self, unit="imperial"):
        config = MagicMock()
        config.lat = "43.6532"
        config.lon = "-79.3832"
        config.api_key = "test_key"
        config.unit = unit
        return config

    @patch("src.weather_api.requests.get")
    def test_builds_correct_params_imperial(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"current": {}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        config = self._make_config("imperial")
        fetch_weather(config)

        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args
        params = call_kwargs.kwargs["params"] if "params" in call_kwargs.kwargs else call_kwargs[1]["params"]
        assert params["lat"] == "43.6532"
        assert params["lon"] == "-79.3832"
        assert params["appid"] == "test_key"
        assert params["units"] == "imperial"
        assert params["exclude"] == "daily"

    @patch("src.weather_api.requests.get")
    def test_builds_correct_params_metric(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"current": {}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        config = self._make_config("metric")
        fetch_weather(config)

        params = mock_get.call_args.kwargs["params"]
        assert params["units"] == "metric"

    @patch("src.weather_api.requests.get")
    def test_raises_on_http_error(self, mock_get):
        import requests
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404")
        mock_get.return_value = mock_response

        config = self._make_config()
        with pytest.raises(requests.HTTPError):
            fetch_weather(config)

    @patch("src.weather_api.requests.get")
    def test_timeout_is_set(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        config = self._make_config()
        fetch_weather(config)

        assert mock_get.call_args.kwargs["timeout"] == 30
