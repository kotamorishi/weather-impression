"""Tests for config.py."""

import os
import pytest
from src.config import Config


class TestConfig:
    def test_load_valid_config(self, config_dir):
        config = Config(path=os.path.join(config_dir, "config.txt"))
        assert config.lat == "43.6532"
        assert config.lon == "-79.3832"
        assert config.api_key == "test_key_123"
        assert config.mode == "0"
        assert config.forecast_interval == 1
        assert config.unit == "imperial"
        assert config.cold_temp == 41.0
        assert config.hot_temp == 88.0
        assert config.one_time_message == "Hello"

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            Config(path="/nonexistent/config.txt")

    def test_consume_one_time_message(self, config_dir):
        path = os.path.join(config_dir, "config.txt")
        config = Config(path=path)
        msg = config.consume_one_time_message()
        assert msg == "Hello"
        assert config.one_time_message == ""

        # Second call returns empty
        msg2 = config.consume_one_time_message()
        assert msg2 == ""

        # Reload and verify it was cleared on disk
        config2 = Config(path=path)
        assert config2.one_time_message == ""

    def test_set_value(self, config_dir):
        path = os.path.join(config_dir, "config.txt")
        config = Config(path=path)
        config.set_value("mode", "2")

        config2 = Config(path=path)
        assert config2.mode == "2"

    def test_set_values_batch(self, config_dir):
        path = os.path.join(config_dir, "config.txt")
        config = Config(path=path)
        config.set_values({
            "mode": "3",
            "TEMP_UNIT": "metric",
            "one_time_message": "Updated",
        })

        config2 = Config(path=path)
        assert config2.mode == "3"
        assert config2.unit == "metric"
        assert config2.one_time_message == "Updated"

    def test_atomic_write(self, config_dir):
        """Verify no .tmp file is left after write."""
        path = os.path.join(config_dir, "config.txt")
        config = Config(path=path)
        config.set_value("mode", "1")
        assert not os.path.exists(path + ".tmp")

    def test_config_without_one_time_message(self, config_dir):
        """Config without one_time_message option should default to empty."""
        path = os.path.join(config_dir, "config.txt")
        # Rewrite without one_time_message
        with open(path, "w") as f:
            f.write("""[openweathermap]
LAT=0
LON=0
API_KEY=test
mode=0
FORECAST_INTERVAL=1
TEMP_UNIT=metric
cold_temp=5
hot_temp=30
""")
        config = Config(path=path)
        assert config.one_time_message == ""
