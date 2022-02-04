# This is just works - NO GOOD code at all.
I will fix this up when I feel to do it.

![lib directory contents](/frame.jpg)

# weather-impression
Weather station for PIMORONI Inky Impression(5.7")
https://shop.pimoroni.com/products/inky-impression-5-7

# Pre requesties
Library for Inky Impression.
https://github.com/pimoroni/inky

For graph drawing, you need to install numpy and matplotlib.
```bash
pip3 install -U numpy
pip3 install -U matplotlib
```
# Weather information
Get your API key.
https://openweathermap.org/

# Configure your weather station
copy ```config.txt.default``` to ```config.txt```
```
[openweathermap]
# set latitude and longitude for your weather info.
LAT=43.6532,
LON=-79.3832

# Your openweathermap API key
API_KEY=COPY_AND_PASTE_YOUR_API_KEY_HERE

# 0:default
# 1:Show warning message, when the warning is in effect
# 2:Graph(temp and air pressure)
mode=0

# Forecast interval(Hours) MIN:1
FORECAST_INTERVAL=1
```

# Set up cron
```bash
sudo crontab -e
```

add 2 lines at the end(adjust for your path)
```bash
22 * * * * /usr/bin/python3 /home/pi/weather-impression/weather.py >/dev/null 2>&1
@reboot /usr/bin/python3 /home/pi/weather-impression/watcher.py >/dev/null 2>&1
```

watcher.py handling button press and update config.txt(mode and one time message)
I will change watcher.py to run it every one hour.

# Fonts
These fonts are already included in this project.

Weather icon
https://erikflowers.github.io/weather-icons/

Roboto
https://fonts.google.com/specimen/Roboto#standard-styles

