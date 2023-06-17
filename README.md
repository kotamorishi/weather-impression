![lib directory contents](/sample.jpg)

# weather-impression
Weather station for PIMORONI Inky Impression(5.7")
https://shop.pimoroni.com/products/inky-impression-5-7

# How to install
This app can be installed on a fresh installation of Raspberry Pi OS (Buster). While it may work with other versions of Raspberry Pi OS, I have not tested it on those versions.

## Option 1 : Easy install for Raspberry Pi OS(Buster)
This command will install all required libraries also set up a cron job for the superuser.
This script may take 10 to 20 minuits on Pi 3 or older☕
```bash
curl https://raw.githubusercontent.com/kotamorishi/weather-impression/main/install.sh | bash
```

## Option 2:Manual install
### 2-1 Install libraries.
To use [Pimoroni Inky Impression](https://github.com/pimoroni/inky), install the required Python libraries. Additionally, if you want to draw graphs, you will need to install numpy and matplotlib. For LED notifications, gpiod is also required.
```bash
sudo -H pip3 install Pillow
sudo apt -y install libopenjp2-7 libtiff5 libatlas-base-dev
sudo -H pip3 install numpy
sudo -H pip3 install matplotlib
sudo -H pip3 install gpiod
sudo -H pip3 install schedule
```
### 2-2 Get your weather information API key
This project uses the OpenWeatherMap API to obtain weather information. To use this API, you will need to obtain an API key with a One Call API 3.0 Subscription. The subscription allows for 1,000 API calls per day for free. You can obtain the API key at [openweathermap.org](https://openweathermap.org/)

### 2-3 Clone this repo
```bash
git clone https://github.com/kotamorishi/weather-impression.git
```

### 2-4 Configure your weather station
copy ```config.txt.default``` to ```config.txt```

Update LAT, LON, API_KEY and mode.
```ini
[openweathermap]
# set latitude and longitude for your weather info.
LAT=43.6532
LON=-79.3832

# Your openweathermap API key
API_KEY=COPY_AND_PASTE_YOUR_API_KEY_HERE

# 0:default
# 1:Show warning message, when the warning is in effect
# 2:Graph(temp and air pressure)
# 3:Sunrise/Sunset Icon
# 4:Sunrise/Sunset Graph
mode=0

# Forecast interval(Hours) MIN:1
FORECAST_INTERVAL=1

# tempture unit metric or imperial
TEMP_UNIT=imperial

# Font color for hot/cold tempture
# blue
cold_temp=41
# red
hot_temp=88
```

### 2-5 Set up cron
Open up the cron setting file.
```bash
sudo crontab -e
```

Add this line at the end of cron setting file.
```bash
@reboot /usr/bin/python3 /home/pi/weather-impression/watcher.py >/dev/null 2>&1
```
Just for your information, watcher.py is responsible for handling button presses and updating the config.txt file (which includes the mode and one-time message).

## Fonts
Weather icon
https://erikflowers.github.io/weather-icons/

Roboto
https://fonts.google.com/specimen/Roboto#standard-styles
