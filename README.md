![Weather Impression](/sample.jpg)

# weather-impression
Weather station for PIMORONI Inky Impression (5.7")
https://shop.pimoroni.com/products/inky-impression-5-7

## Supported Environment
- Raspberry Pi OS **Trixie** (Debian 13) or **Bookworm** (Debian 12)
- Python 3.11+
- Pimoroni Inky library v2.3.0+

## How to install

This command will install all required libraries, enable SPI/I2C, and set up a cron job.
This script may take 10 to 20 minutes on Pi 3 or older.

```bash
curl https://raw.githubusercontent.com/kotamorishi/weather-impression/main/install.sh | bash
```

After installation, edit `~/weather-impression/config.txt` with your settings:
- Set `LAT` and `LON` to your location
- Set `API_KEY` from [openweathermap.org](https://openweathermap.org/) (One Call API 3.0, free for 1,000 calls/day)

Then reboot, or test immediately:
```bash
~/.virtualenvs/weather-impression/bin/python3 ~/weather-impression/weather.py
```

> For step-by-step manual installation, see [MANUAL_INSTALL.md](MANUAL_INSTALL.md).

## Display modes

| Mode | Description |
|:----:|-------------|
| 0 | Default - 4 forecast icons at the bottom |
| 1 | Alert - Show warning message when in effect |
| 2 | Graph - Temperature and air pressure graphs |
| 3 | Sunrise/Sunset icons |
| 4 | Sunrise/Sunset graph |

Use the physical buttons on the Inky Impression to switch modes.

## Fonts
- Weather icons: https://erikflowers.github.io/weather-icons/
- Roboto: https://fonts.google.com/specimen/Roboto
