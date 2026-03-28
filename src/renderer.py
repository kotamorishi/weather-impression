"""Weather display rendering for Inky Impression 5.7"."""

import math
import os
import re
import time
from datetime import datetime
from enum import Enum

from PIL import Image, ImageDraw, ImageFont

from inky.inky_uc8159 import (
    BLACK, WHITE, GREEN, RED, YELLOW, ORANGE, BLUE,
    DESATURATED_PALETTE as COLOR_PALETTE,
)

from .config import PROJECT_ROOT, CANVAS_SIZE, TMPFS_PATH, UNIT_IMPERIAL

# --- Font management ---

class FontType(Enum):
    THIN = os.path.join(PROJECT_ROOT, "fonts", "Roboto-Thin.ttf")
    LIGHT = os.path.join(PROJECT_ROOT, "fonts", "Roboto-Light.ttf")
    BOLD = os.path.join(PROJECT_ROOT, "fonts", "Roboto-Black.ttf")
    ICON = os.path.join(PROJECT_ROOT, "fonts", "weathericons-regular-webfont.ttf")


def get_font(font_type, size=12):
    return ImageFont.truetype(font_type.value, size)


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


# --- Icon / color mappings ---

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
# clock12 is same as clock0
ICON_MAP["clock12"] = "\uf089"

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


# --- Text helpers ---

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


# --- Rendering entry point ---

def render(config, weather_data):
    """Render the weather display and return a PIL Image."""
    canvas = Image.new("RGB", CANVAS_SIZE, display_color(WHITE))
    draw = ImageDraw.Draw(canvas)
    width, height = CANVAS_SIZE

    # No weather data — show error screen
    if weather_data is None:
        _draw_error(draw, width, height, config)
        return canvas

    one_time_msg = config.consume_one_time_message()
    if one_time_msg:
        draw.text(
            (width - 10, 2), one_time_msg,
            display_color(BLACK), anchor="ra",
            font=get_font(FontType.BOLD, 12),
        )

    current = weather_data["current"]
    _draw_header(draw, width, current)
    _draw_current_weather(draw, width, current, config)

    mode = config.mode
    if mode == "1" and "alerts" in weather_data:
        _draw_alert(draw, width, weather_data["alerts"][0])
    elif mode == "2":
        _draw_graph(draw, canvas, width, height, weather_data)
    elif mode == "3":
        _draw_sunrise_icon(draw, width, current)
    elif mode == "4":
        _draw_sunrise_graph(canvas, current)
    else:
        _draw_feels_pressure(draw, width, current, config)
        _draw_forecast(draw, width, weather_data, config)

    return canvas


# --- Section renderers ---

def _draw_error(draw, width, height, config):
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
    msg = getattr(config, "one_time_message", "") or ""
    if not msg:
        msg = "Configuration file is not found or settings are wrong.\n"
        msg += "Please check config.txt\n\nAlso check your internet connection."
    draw.text(
        (width / 2, height / 2), msg,
        display_color(BLACK), anchor="mm",
        font=get_font(FontType.BOLD, 16),
    )


def _draw_header(draw, width, current):
    epoch = int(current["dt"])
    date_str = time.strftime("%B %-d", time.localtime(epoch))
    weekday_str = time.strftime("%a", time.localtime(epoch))

    draw.text(
        (15, 5), date_str, display_color(BLACK),
        font=get_font(FontType.BOLD, 64),
    )
    draw.text(
        (width - 8, 5), weekday_str, display_color(BLACK),
        anchor="ra", font=get_font(FontType.BOLD, 64),
    )


def _draw_current_weather(draw, width, current, config):
    temp = current["temp"]
    icon = str(current["weather"][0]["icon"])
    description = current["weather"][0]["description"]

    ox, oy = 10, 40

    # Temperature
    temp_str = format_temperature(temp)
    temp_w, _ = text_size(draw, temp_str, get_font(FontType.BOLD, 120))
    temp_offset = 45 if temp_w < 71 else 20

    draw.text(
        (5 + ox, 35 + oy), "Temperature", display_color(BLACK),
        font=get_font(FontType.LIGHT, 24),
    )
    draw.text(
        (temp_offset + ox, 50 + oy), temp_str,
        temp_color(temp, config), font=get_font(FontType.BOLD, 120),
    )
    draw.text(
        (temp_w + 10 + temp_offset + ox, 85 + oy),
        unit_icon(config.unit), temp_color(temp, config),
        anchor="la", font=get_font(FontType.ICON, 80),
    )

    # Weather icon
    draw.text(
        (440 + ox, 40 + oy), ICON_MAP[icon],
        display_color(ICON_COLOR_MAP[icon]),
        anchor="ma", font=get_font(FontType.ICON, 160),
    )

    # Description
    draw.text(
        (width - 8, 35 + oy), description, display_color(BLACK),
        anchor="ra", font=get_font(FontType.LIGHT, 24),
    )


def _draw_feels_pressure(draw, width, current, config):
    ox = 10
    temp_feels = current["feels_like"]
    pressure = current["pressure"]

    draw.text(
        (5 + ox, 215), "Feels like", display_color(BLACK),
        font=get_font(FontType.LIGHT, 24),
    )
    feels_str = format_temperature(temp_feels)
    draw.text(
        (10 + ox, 240), feels_str,
        temp_color(temp_feels, config), font=get_font(FontType.BOLD, 50),
    )
    feels_w, _ = text_size(draw, feels_str, get_font(FontType.BOLD, 50))
    draw.text(
        (feels_w + 20 + ox, 240), unit_icon(config.unit),
        temp_color(temp_feels, config),
        anchor="la", font=get_font(FontType.ICON, 50),
    )

    draw.text(
        (feels_w + 85 + ox, 215), "Pressure", display_color(BLACK),
        font=get_font(FontType.LIGHT, 24),
    )
    pressure_str = "%d" % pressure
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
        "%B %-d, %-I:%M %p", time.localtime(alert["start"])
    )

    desc = alert["description"]
    desc = desc.replace("\n###\n", "").replace("\n\n", "")
    desc = desc.replace("https://", "")
    desc = re.sub(r"([A-Za-z]*:)", r"\n\1", desc)
    desc = re.sub(r"((?=.{90})(.{0,89}([\.[ ]|[ ]))|.{0,89})", r"\1\n", desc)
    desc = desc.replace("\n\n", "")

    draw.text(
        (5 + ox, 215), alert["event"].capitalize(),
        display_color(RED), anchor="la",
        font=get_font(FontType.LIGHT, 24),
    )
    draw.text(
        (5 + ox, 240), f'{start_str}/{alert["sender_name"]}',
        display_color(BLACK), font=get_font(FontType.BOLD, 12),
    )
    draw.text(
        (5 + ox, 270), desc, display_color(RED),
        anchor="la", font=get_font(FontType.BOLD, 14),
    )


def _draw_forecast(draw, width, weather_data, config):
    oy = 210
    interval = config.forecast_interval
    num_forecasts = 4
    col_width = width / num_forecasts
    text_color = (50, 50, 50)

    for i in range(num_forecasts):
        idx = i * interval + interval
        try:
            hourly = weather_data["hourly"][idx]
        except IndexError:
            break

        t = time.strftime("%-I %p", time.localtime(hourly["dt"]))
        temp = hourly["temp"]
        icon = hourly["weather"][0]["icon"]
        desc = hourly["weather"][0]["description"]

        draw.text(
            (30 + i * col_width, oy + 220), t, text_color,
            anchor="la", font=get_font(FontType.BOLD, 12),
        )
        draw.text(
            (120 + i * col_width, oy + 220), "%2.1f" % temp,
            text_color, anchor="ra", font=get_font(FontType.BOLD, 12),
        )
        draw.text(
            (col_width / 2 + i * col_width, oy + 200), desc,
            text_color, anchor="ma", font=get_font(FontType.BOLD, 16),
        )
        draw.text(
            (70 + i * col_width, oy + 90), ICON_MAP[icon],
            display_color(ICON_COLOR_MAP[icon]),
            anchor="ma", font=get_font(FontType.ICON, 80),
        )


def _draw_graph(draw, canvas, width, height, weather_data):
    import matplotlib.pyplot as plt
    import numpy as np

    timestamps, temps, feels, pressures = [], [], [], []
    for hourly in weather_data["hourly"][:47]:
        timestamps.append(hourly["dt"])
        temps.append(hourly["temp"])
        feels.append(hourly["feels_like"])
        pressures.append(hourly["pressure"])

    if not timestamps:
        return

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
    sunrise = current["sunrise"]
    sunset = current["sunset"]
    sunrise_fmt = datetime.fromtimestamp(sunrise).strftime("%-I:%M %p")
    sunset_fmt = datetime.fromtimestamp(sunset).strftime("%-I:%M %p")

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

    sunrise_ts = current["sunrise"]
    sunset_ts = current["sunset"]

    def to_hour(ts):
        dt = datetime.fromtimestamp(ts)
        return dt.hour + dt.minute / 60

    sunrise_h = to_hour(sunrise_ts)
    sunset_h = to_hour(sunset_ts)
    sunrise_fmt = datetime.fromtimestamp(sunrise_ts).strftime("%-I:%M %p")
    sunset_fmt = datetime.fromtimestamp(sunset_ts).strftime("%-I:%M %p")

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

    # Sunrise/sunset icons with shadow effect
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
