"""Parse raw OpenWeatherMap JSON into typed dataclasses with safe defaults."""

from dataclasses import dataclass, field


@dataclass
class WeatherCondition:
    icon: str = "01d"
    description: str = ""

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            return cls()
        return cls(
            icon=_str(data.get("icon"), "01d"),
            description=_str(data.get("description"), ""),
        )


@dataclass
class CurrentWeather:
    dt: int = 0
    temp: float = 0.0
    feels_like: float = 0.0
    pressure: int = 0
    humidity: int = 0
    sunrise: int = 0
    sunset: int = 0
    condition: WeatherCondition = field(default_factory=WeatherCondition)

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            return cls()

        weather_list = data.get("weather", [])
        if isinstance(weather_list, list) and len(weather_list) > 0:
            condition = WeatherCondition.from_dict(weather_list[0])
        else:
            condition = WeatherCondition()

        return cls(
            dt=_int(data.get("dt", 0)),
            temp=_float(data.get("temp", 0.0)),
            feels_like=_float(data.get("feels_like", 0.0)),
            pressure=_int(data.get("pressure", 0)),
            humidity=_int(data.get("humidity", 0)),
            sunrise=_int(data.get("sunrise", 0)),
            sunset=_int(data.get("sunset", 0)),
            condition=condition,
        )


@dataclass
class HourlyForecast:
    dt: int = 0
    temp: float = 0.0
    feels_like: float = 0.0
    pressure: int = 0
    condition: WeatherCondition = field(default_factory=WeatherCondition)

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            return cls()

        weather_list = data.get("weather", [])
        if isinstance(weather_list, list) and len(weather_list) > 0:
            condition = WeatherCondition.from_dict(weather_list[0])
        else:
            condition = WeatherCondition()

        return cls(
            dt=_int(data.get("dt", 0)),
            temp=_float(data.get("temp", 0.0)),
            feels_like=_float(data.get("feels_like", 0.0)),
            pressure=_int(data.get("pressure", 0)),
            condition=condition,
        )


@dataclass
class WeatherAlert:
    event: str = ""
    sender_name: str = ""
    start: int = 0
    description: str = ""

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            return cls()
        return cls(
            event=_str(data.get("event"), ""),
            sender_name=_str(data.get("sender_name"), ""),
            start=_int(data.get("start", 0)),
            description=_str(data.get("description"), ""),
        )


@dataclass
class WeatherData:
    """Parsed and validated weather data from OpenWeatherMap API."""
    current: CurrentWeather = field(default_factory=CurrentWeather)
    hourly: list = field(default_factory=list)
    alerts: list = field(default_factory=list)

    @classmethod
    def from_dict(cls, data):
        """Parse raw API response dict into WeatherData.

        Handles missing keys, wrong types, and malformed data gracefully
        by falling back to sensible defaults.
        """
        if not isinstance(data, dict):
            return cls()

        current = CurrentWeather.from_dict(data.get("current", {}))

        raw_hourly = data.get("hourly", [])
        if not isinstance(raw_hourly, list):
            raw_hourly = []
        hourly = [HourlyForecast.from_dict(h) for h in raw_hourly]

        raw_alerts = data.get("alerts", [])
        if not isinstance(raw_alerts, list):
            raw_alerts = []
        alerts = [WeatherAlert.from_dict(a) for a in raw_alerts]

        return cls(current=current, hourly=hourly, alerts=alerts)


def _str(value, default=""):
    """Safely convert to str, treating None as missing."""
    if value is None:
        return default
    return str(value)


def _int(value):
    """Safely convert to int."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _float(value):
    """Safely convert to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
