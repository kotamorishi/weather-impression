"""Weather display rendering for Inky Impression 5.7"."""

import math
import re
import time
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from inky.inky_uc8159 import (
    BLACK, WHITE, GREEN, RED, YELLOW, ORANGE, BLUE,
    DESATURATED_PALETTE as COLOR_PALETTE,
)

from .constants import (
    CANVAS_SIZE, TMPFS_PATH, UNIT_IMPERIAL,
    FontType, ICON_MAP, ICON_COLOR_MAP,
)
from .weather_data import WeatherData

# --- Color helpers ---


def display_color(color_index):
    """Convert a palette index to an RGB tuple (0-255)."""
    return tuple(COLOR_PALETTE[color_index])


def graph_color(color_index):
    """Convert a palette index to an RGB tuple (0.0-1.0) for matplotlib."""
    return tuple(c / 255 for c in COLOR_PALETTE[color_index])


def temp_color(temp, config):
    """Return font color based on temperature thresholds."""
    if temp < config.cold_temp:
        return (0, 0, 255)
    if temp > config.hot_temp:
        return (255, 0, 0)
    return display_color(BLACK)


# --- Font / text helpers ---


def get_font(font_type, size=12):
    return ImageFont.truetype(font_type.value, size)


def format_temperature(temp):
    """Format temperature, avoiding '-0'."""
    s = "%0.0f" % temp
    return "0" if s == "-0" else s


def unit_icon(unit):
    return ICON_MAP["fahrenheit"] if unit == UNIT_IMPERIAL else ICON_MAP["celsius"]


def text_size(draw, text, font):
    """Measure text width and height using textbbox."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return (bbox[2] - bbox[0], bbox[3] - bbox[1])


def font_text_width(font, text):
    """Measure text width using font.getbbox."""
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]


def _get_icon(icon_code):
    """Safely look up an icon code, falling back to clear sky."""
    return ICON_MAP.get(icon_code, ICON_MAP["01d"])


def _get_icon_color(icon_code):
    """Safely look up an icon color, falling back to BLACK."""
    return ICON_COLOR_MAP.get(icon_code, BLACK)


# --- Rendering entry point ---


def render(config, weather, error_message=None):
    """Render the weather display and return a PIL Image.

    Args:
        config: Config object (may be None if loading failed).
        weather: WeatherData dataclass, or None on error.
        error_message: Optional error message to display on error screen.
    """
    canvas = Image.new("RGB", CANVAS_SIZE, display_color(WHITE))
    draw = ImageDraw.Draw(canvas)
    width, height = CANVAS_SIZE

    if weather is None:
        _draw_error(draw, width, height, error_message)
        return canvas

    one_time_msg = config.consume_one_time_message()
    if one_time_msg:
        draw.text(
            (width - 10, 2), one_time_msg,
            display_color(BLACK), anchor="ra",
            font=get_font(FontType.BOLD, 12),
        )

    _draw_header(draw, width, weather.current)
    _draw_current_weather(draw, width, weather.current, config)

    mode = config.mode
    if mode == "1" and weather.alerts:
        _draw_alert(draw, width, weather.alerts[0])
    elif mode == "2":
        _draw_graph(draw, canvas, width, height, weather.hourly)
    elif mode == "3":
        _draw_sunrise_icon(draw, width, weather.current)
    elif mode == "4":
        _draw_sunrise_graph(canvas, weather.current)
    else:
        _draw_feels_pressure(draw, width, weather.current, config)
        _draw_forecast(draw, width, weather.hourly, config)

    return canvas


# --- Section renderers ---


def _draw_error(draw, width, height, error_message=None):
    draw.rectangle((0, 0, width, height), fill=display_color(ORANGE))
    draw.text(
        (20, 70), "\uf071", display_color(BLACK),
        anchor="lm", font=get_font(FontType.ICON, 130),
    )
    draw.text(
        (150, 80),
        "Weather information is not available at this time.",
        display_color(BLACK), anchor="lm",
        font=get_font(FontType.BOLD, 18),
    )
    msg = error_message or (
        "Configuration file is not found or settings are wrong.\n"
        "Please check config.txt\n\nAlso check your internet connection."
    )
    draw.text(
        (width / 2, height / 2), msg,
        display_color(BLACK), anchor="mm",
        font=get_font(FontType.BOLD, 16),
    )


def _draw_header(draw, width, current):
    date_str = time.strftime("%B %-d", time.localtime(current.dt))
    weekday_str = time.strftime("%a", time.localtime(current.dt))

    draw.text(
        (15, 5), date_str, display_color(BLACK),
        font=get_font(FontType.BOLD, 64),
    )
    draw.text(
        (width - 8, 5), weekday_str, display_color(BLACK),
        anchor="ra", font=get_font(FontType.BOLD, 64),
    )


def _draw_current_weather(draw, width, current, config):
    icon_code = current.condition.icon
    description = current.condition.description

    ox, oy = 10, 40

    temp_str = format_temperature(current.temp)
    temp_w, _ = text_size(draw, temp_str, get_font(FontType.BOLD, 120))
    temp_offset = 45 if temp_w < 71 else 20

    draw.text(
        (5 + ox, 35 + oy), "Temperature", display_color(BLACK),
        font=get_font(FontType.LIGHT, 24),
    )
    draw.text(
        (temp_offset + ox, 50 + oy), temp_str,
        temp_color(current.temp, config), font=get_font(FontType.BOLD, 120),
    )
    draw.text(
        (temp_w + 10 + temp_offset + ox, 85 + oy),
        unit_icon(config.unit), temp_color(current.temp, config),
        anchor="la", font=get_font(FontType.ICON, 80),
    )

    draw.text(
        (440 + ox, 40 + oy), _get_icon(icon_code),
        display_color(_get_icon_color(icon_code)),
        anchor="ma", font=get_font(FontType.ICON, 160),
    )

    draw.text(
        (width - 8, 35 + oy), description, display_color(BLACK),
        anchor="ra", font=get_font(FontType.LIGHT, 24),
    )


def _draw_feels_pressure(draw, width, current, config):
    ox = 10

    draw.text(
        (5 + ox, 215), "Feels like", display_color(BLACK),
        font=get_font(FontType.LIGHT, 24),
    )
    feels_str = format_temperature(current.feels_like)
    draw.text(
        (10 + ox, 240), feels_str,
        temp_color(current.feels_like, config), font=get_font(FontType.BOLD, 50),
    )
    feels_w, _ = text_size(draw, feels_str, get_font(FontType.BOLD, 50))
    draw.text(
        (feels_w + 20 + ox, 240), unit_icon(config.unit),
        temp_color(current.feels_like, config),
        anchor="la", font=get_font(FontType.ICON, 50),
    )

    draw.text(
        (feels_w + 85 + ox, 215), "Pressure", display_color(BLACK),
        font=get_font(FontType.LIGHT, 24),
    )
    pressure_str = "%d" % current.pressure
    draw.text(
        (feels_w + 90 + ox, 240), pressure_str,
        display_color(BLACK), font=get_font(FontType.BOLD, 50),
    )
    pressure_w, _ = text_size(draw, pressure_str, get_font(FontType.BOLD, 50))
    draw.text(
        (feels_w + pressure_w + 95 + ox, 264), "hPa",
        display_color(BLACK), font=get_font(FontType.BOLD, 22),
    )


def _draw_alert(draw, width, alert):
    ox = 10
    start_str = time.strftime(
        "%B %-d, %-I:%M %p", time.localtime(alert.start)
    )

    desc = alert.description
    desc = desc.replace("\n###\n", "").replace("\n\n", "")
    desc = desc.replace("https://", "")
    desc = re.sub(r"([A-Za-z]*:)", r"\n\1", desc)
    desc = re.sub(r"((?=.{90})(.{0,89}([\.[ ]|[ ]))|.{0,89})", r"\1\n", desc)
    desc = desc.replace("\n\n", "")

    draw.text(
        (5 + ox, 215), alert.event.capitalize(),
        display_color(RED), anchor="la",
        font=get_font(FontType.LIGHT, 24),
    )
    draw.text(
        (5 + ox, 240), f"{start_str}/{alert.sender_name}",
        display_color(BLACK), font=get_font(FontType.BOLD, 12),
    )
    draw.text(
        (5 + ox, 270), desc, display_color(RED),
        anchor="la", font=get_font(FontType.BOLD, 14),
    )


def _draw_forecast(draw, width, hourly, config):
    oy = 210
    interval = config.forecast_interval
    num_forecasts = 4
    col_width = width / num_forecasts
    text_color = (50, 50, 50)

    for i in range(num_forecasts):
        idx = i * interval + interval
        if idx >= len(hourly):
            break

        entry = hourly[idx]
        icon_code = entry.condition.icon
        desc = entry.condition.description

        t = time.strftime("%-I %p", time.localtime(entry.dt))

        draw.text(
            (30 + i * col_width, oy + 220), t, text_color,
            anchor="la", font=get_font(FontType.BOLD, 12),
        )
        draw.text(
            (120 + i * col_width, oy + 220), "%2.1f" % entry.temp,
            text_color, anchor="ra", font=get_font(FontType.BOLD, 12),
        )
        draw.text(
            (col_width / 2 + i * col_width, oy + 200), desc,
            text_color, anchor="ma", font=get_font(FontType.BOLD, 16),
        )
        draw.text(
            (70 + i * col_width, oy + 90), _get_icon(icon_code),
            display_color(_get_icon_color(icon_code)),
            anchor="ma", font=get_font(FontType.ICON, 80),
        )


def _draw_graph(draw, canvas, width, height, hourly):
    import matplotlib.pyplot as plt
    import numpy as np

    entries = hourly[:47]
    if not entries:
        return

    timestamps = [e.dt for e in entries]
    temps = [e.temp for e in entries]
    feels = [e.feels_like for e in entries]
    pressures = [e.pressure for e in entries]

    graph_h, graph_w = 1.1, 8.4

    # Pressure graph
    fig = plt.figure()
    fig.set_figheight(graph_h)
    fig.set_figwidth(graph_w)
    plt.plot(timestamps, pressures, linewidth=3, color=graph_color(RED))
    plt.axis("off")

    p_min, p_max = 990, 1020
    if min(pressures) < p_min - 2:
        p_min = min(pressures) + 2
    if max(pressures) > p_max - 2:
        p_max = max(pressures) + 2
    plt.ylim(p_min, p_max)

    plt.savefig(TMPFS_PATH + "pressure.png", bbox_inches="tight", transparent=True)
    plt.close(fig)
    with Image.open(TMPFS_PATH + "pressure.png") as img:
        canvas.paste(img, (-35, 330), img)

    # Temperature + feels-like graph
    fig = plt.figure()
    fig.set_figheight(graph_h)
    fig.set_figwidth(graph_w)
    plt.plot(timestamps, feels, linewidth=3, color=graph_color(GREEN), linestyle=":")
    plt.plot(timestamps, temps, linewidth=3, color=graph_color(BLUE))

    for idx in range(1, len(timestamps)):
        h = time.strftime("%-I", time.localtime(timestamps[idx]))
        if h in ("0", "12"):
            plt.axvline(x=timestamps[idx], color="black", linestyle=":")
            pos_y = np.array(temps).max() + 1
            plt.text(
                timestamps[idx - 1], pos_y,
                time.strftime("%p", time.localtime(timestamps[idx])),
            )
    plt.axis("off")
    plt.savefig(TMPFS_PATH + "temp.png", bbox_inches="tight", transparent=True)
    plt.close(fig)
    with Image.open(TMPFS_PATH + "temp.png") as img:
        canvas.paste(img, (-35, 300), img)

    # Legend
    ox = 10
    draw.rectangle((5, 430, 20, 446), fill=display_color(RED))
    draw.text((15 + ox, 428), "Pressure", display_color(BLACK), font=get_font(FontType.BOLD, 16))
    draw.rectangle((135, 430, 150, 446), fill=display_color(BLUE))
    draw.text((145 + ox, 428), "Temp", display_color(BLACK), font=get_font(FontType.BOLD, 16))
    draw.rectangle((265, 430, 280, 446), fill=display_color(GREEN))
    draw.text((275 + ox, 428), "Feels like", display_color(BLACK), font=get_font(FontType.BOLD, 16))


def _draw_sunrise_icon(draw, width, current):
    oy = 210
    sunrise_fmt = datetime.fromtimestamp(current.sunrise).strftime("%-I:%M %p")
    sunset_fmt = datetime.fromtimestamp(current.sunset).strftime("%-I:%M %p")

    col_w = width / 2
    text_color = (50, 50, 50)

    for label, formatted, icon_key, x_base in [
        ("Sunrise", sunrise_fmt, "sunrise", 0),
        ("Sunset", sunset_fmt, "sunset", col_w),
    ]:
        center = x_base + col_w / 2

        lbl_w = font_text_width(get_font(FontType.BOLD, 16), label)
        fmt_w = font_text_width(get_font(FontType.BOLD, 12), formatted)
        ico_w = font_text_width(get_font(FontType.ICON, 90), ICON_MAP[icon_key])

        draw.text(
            (center - fmt_w / 2, oy + 220), formatted, text_color,
            anchor="la", font=get_font(FontType.BOLD, 12),
        )
        draw.text(
            (center - ico_w / 2, oy + 90), ICON_MAP[icon_key],
            display_color(ICON_COLOR_MAP[icon_key]),
            anchor="la", font=get_font(FontType.ICON, 90),
        )
        draw.text(
            (center - lbl_w / 2, oy + 200), label, text_color,
            anchor="la", font=get_font(FontType.BOLD, 16),
        )


def _draw_sunrise_graph(canvas, current):
    import matplotlib.pyplot as plt
    from matplotlib import font_manager as fm

    def to_hour(ts):
        dt = datetime.fromtimestamp(ts)
        return dt.hour + dt.minute / 60

    sunrise_h = to_hour(current.sunrise)
    sunset_h = to_hour(current.sunset)
    sunrise_fmt = datetime.fromtimestamp(current.sunrise).strftime("%-I:%M %p")
    sunset_fmt = datetime.fromtimestamp(current.sunset).strftime("%-I:%M %p")

    icon_font = get_font(FontType.ICON, 12)
    icon_prop = fm.FontProperties(fname=icon_font.path)
    text_font = get_font(FontType.BOLD, 12)
    text_prop = fm.FontProperties(fname=text_font.path)

    x = list(range(24))
    y = [math.cos((i / 12 - 1) * math.pi) for i in x]

    fig = plt.figure()
    fig.set_figheight(1.1)
    fig.set_figwidth(8.4)
    plt.xlim(0, 23)
    plt.ylim(-1.2, 1.2)

    plt.axvline(x=sunrise_h, color="blue", linestyle="--")
    plt.axvline(x=sunset_h, color="blue", linestyle="--")

    for offset, ha, hour, icon_key, fmt in [
        (-0.3, "right", sunrise_h, "sunrise", sunrise_fmt),
        (0.3, "left", sunset_h, "sunset", sunset_fmt),
    ]:
        plt.text(hour + offset - 0.05, 1.35, ICON_MAP[icon_key],
                 fontproperties=icon_prop, ha=ha, va="top", color=graph_color(YELLOW))
        plt.text(hour + offset, 1.3, ICON_MAP[icon_key],
                 fontproperties=icon_prop, ha=ha, va="top", color=graph_color(BLUE))
        plt.text(hour + offset, 0.8, fmt, ha=ha, va="top",
                 fontproperties=text_prop, color=graph_color(BLUE))

    plt.plot(x, y, linewidth=3, color=graph_color(RED))
    plt.axis("off")

    plt.savefig(TMPFS_PATH + "day.png", bbox_inches="tight", transparent=True)
    plt.close(fig)
    with Image.open(TMPFS_PATH + "day.png") as img:
        canvas.paste(img, (-35, 300), img)
