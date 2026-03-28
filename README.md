![Weather Impression](/sample.jpg)

# weather-impression
Weather station for PIMORONI Inky Impression (5.7")
https://shop.pimoroni.com/products/inky-impression-5-7

## Supported Environment
- Raspberry Pi OS **Trixie** (Debian 13) or **Bookworm** (Debian 12)
- Python 3.11+
- Pimoroni Inky library v2.3.0+

## How to install

### Option 1: Easy install
This command will install all required libraries, enable SPI/I2C, and set up a cron job.
This script may take 10 to 20 minutes on Pi 3 or older.
```bash
curl https://raw.githubusercontent.com/kotamorishi/weather-impression/main/install.sh | bash
```

### Option 2: Manual install

#### 2-1 Install system dependencies
```bash
sudo apt-get update
sudo apt-get -y install git python3-pip python3-venv libopenjp2-7 libopenblas-dev
sudo apt-get -y install libtiff6  # or libtiff5 on Bookworm
```

#### 2-2 Enable SPI and I2C
The Inky display communicates via SPI and I2C. Enable them:
```bash
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0
```

Also add the SPI CS0 overlay so Inky can control the chip-select pin via GPIO.
Add this line to `/boot/firmware/config.txt` after `dtparam=spi=on`:
```
dtoverlay=spi0-0cs
```

A reboot is required after these changes.

#### 2-3 Clone this repo
```bash
git clone https://github.com/kotamorishi/weather-impression.git ~/weather-impression
```

#### 2-4 Set up Python virtual environment
```bash
mkdir -p ~/.virtualenvs
python3 -m venv ~/.virtualenvs/weather-impression
source ~/.virtualenvs/weather-impression/bin/activate

pip3 install --upgrade pip
pip3 install inky Pillow numpy matplotlib "gpiod>=2" schedule requests
```

#### 2-5 Install Inky driver
The Pimoroni installer configures system-level SPI/I2C support:
```bash
cd ~
git clone https://github.com/pimoroni/inky
cd inky
sudo ./install.sh
```

#### 2-6 Get your weather information API key
This project uses the OpenWeatherMap API to obtain weather information. You will need an API key with a One Call API 3.0 Subscription. The subscription allows for 1,000 API calls per day for free. You can obtain the API key at [openweathermap.org](https://openweathermap.org/)

#### 2-7 Configure your weather station
Copy `config.txt.default` to `config.txt` and update your settings:

```bash
cd ~/weather-impression
cp config.txt.default config.txt
nano config.txt
```

```ini
[openweathermap]
LAT=43.6532
LON=-79.3832
API_KEY=COPY_AND_PASTE_YOUR_API_KEY_HERE

# Display modes:
# 0: Default - 4 forecast icons at the bottom
# 1: Alert - Show warning message when in effect
# 2: Graph - Temperature and air pressure graphs
# 3: Sunrise/Sunset icons
# 4: Sunrise/Sunset graph
mode=0

# Forecast interval in hours (1-12)
FORECAST_INTERVAL=1

# Temperature unit: metric or imperial
TEMP_UNIT=imperial

# Temperature thresholds for color coding
cold_temp=41
hot_temp=88
```

#### 2-8 Test the display
```bash
~/.virtualenvs/weather-impression/bin/python3 ~/weather-impression/weather.py
```

#### 2-9 Set up cron
Open up the cron setting file:
```bash
sudo crontab -e
```

Add this line:
```bash
@reboot /home/<your-username>/.virtualenvs/weather-impression/bin/python3 /home/<your-username>/weather-impression/watcher.py >/dev/null 2>&1
```

`watcher.py` handles button presses and updates the display on a schedule.

## Fonts
- Weather icons: https://erikflowers.github.io/weather-icons/
- Roboto: https://fonts.google.com/specimen/Roboto
