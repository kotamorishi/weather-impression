#!/usr/bin/env python3
from os import path, DirEntry
import sys
import math
import time
import calendar
from datetime import date
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from inky.inky_uc8159 import Inky, BLACK, WHITE, GREEN, RED, YELLOW, ORANGE, BLUE

saturation = 0.5
canvasSize = (600, 448)

# font files
titleFontFile = "fonts/Roboto-BlackItalic.ttf"
detailFontFile = "fonts/Roboto-Black.ttf"

dayOfWeekColor = {
    '0':(0, 0, 0),
    '1':(255, 255, 255),
    '2':(0, 255, 0),
    '3':(0, 0, 255),
    '4':(255, 0, 0),
    '5':(255, 255, 0),
    '6':(255, 140, 0),

}

colorMap = {
    '01d':(255,140,0), # clear sky
    '01n':(208, 190, 71),
    '02d':(0,0,0), # few clouds
    '02n':(0,0,0),
    '03d':(0,0,0), # scattered clouds
    '03n':(0,0,0),
    '04d':(0,0,0), # broken clouds
    '04n':(0,0,0),
    '09d':(0,0,0), # shower rain
    '09n':(0,0,0),
    '10d':(0,0,255), # rain
    '10n':(0,0,255),
    '11d':(255,0,0), # thunderstorm
    '11n':(255,0,0),
    '13d':(0,255,255), # snow
    '13n':(0,255,255),
    '50d':(0,0,0), # fog
    '50n':(0,0,0),
}
# icon name to weather icon mapping
iconMap = {
    '01d':u'', # clear sky
    '01n':u'',
    '02d':u'', # few clouds
    '02n':u'',
    '03d':u'', # scattered clouds
    '03n':u'',
    '04d':u'', # broken clouds
    '04n':u'',
    '09d':u'', # shower rain
    '09n':u'',
    '10d':u'', # rain
    '10n':u'',
    '11d':u'', # thunderstorm
    '11n':u'',
    '13d':u'', # snow
    '13n':u'',
    '50d':u'', # fog
    '50n':u'',

    'clock0':u'', # same as 12
    'clock1':u'',
    'clock2':u'',
    'clock3':u'',
    'clock4':u'',
    'clock5':u'',
    'clock6':u'',
    'clock7':u'',
    'clock8':u'',
    'clock9':u'',
    'clock10':u'',
    'clock11':u'',
    'clock12':u''
}

#empty structure
class forecastInfo:
    pass



class weatherInfomation(object):
    def __init__(self):
        #load configuration from config.txt using configparser
        import configparser
        self.config = configparser.ConfigParser()
        self.config.read_file(open('config.txt'))
        self.city_id = self.config.get('openweathermap', 'CITY_ID', raw=False)
        self.api_key = self.config.get('openweathermap', 'API_KEY', raw=False)
        # API document at https://openweathermap.org/current
        self.current_api_uri = 'https://api.openweathermap.org/data/2.5/weather?id=' + self.city_id + '&appid=' + self.api_key + '&units=metric'
        # API document at https://openweathermap.org/forecast5
        self.forecast_api_uri = 'https://api.openweathermap.org/data/2.5/forecast?id=' + self.city_id + '&appid=' + self.api_key + '&units=metric'


    def loadWeatherData(self):
        import requests
        # api response in json format
        self.currentWeatherInfo = requests.get(self.current_api_uri).json()
        #print(self.currentWeatherInfo)
        self.forecastWeatherInfo = requests.get(self.forecast_api_uri).json()
        #print(self.forecastWeatherInfo)

# draw current weather and forecast into canvas
def drawWeather(wi, cv):
    draw = ImageDraw.Draw(cv)
    width, height = cv.size
    
    dateFont = ImageFont.truetype("fonts/Roboto-Black.ttf", 56)
    textFont = ImageFont.truetype("fonts/Roboto-Black.ttf", 24)
    tempurtureFont = ImageFont.truetype("fonts/Roboto-Black.ttf", 120)
    feelslikeFont = ImageFont.truetype("fonts/Roboto-Black.ttf", 70)
    smallFont = ImageFont.truetype("fonts/Roboto-Black.ttf", 16)

    iconFont = ImageFont.truetype("/usr/share/fonts/weathericons-regular-webfont.ttf", 160)
    iconForecastFont = ImageFont.truetype("/usr/share/fonts/weathericons-regular-webfont.ttf", 80)
    
    temp_cur = wi.currentWeatherInfo[u'main'][u'temp']
    temp_cur_feels = wi.currentWeatherInfo[u'main'][u'feels_like']
    icon = str(wi.currentWeatherInfo[u'weather'][0][u'icon'])
    description = wi.currentWeatherInfo[u'weather'][0][u'description']
    humidity = wi.currentWeatherInfo[u'main'][u'humidity']
    epoch = int(wi.currentWeatherInfo[u'dt'])
    dateString = time.strftime("%B %-d", time.localtime(epoch))
    weekDayString = time.strftime("%A", time.localtime(epoch))
    weekDayNumber = time.strftime("%w", time.localtime(epoch))

    # date 
    draw.text((15 , 5), dateString, (0,0,0),font =dateFont)
    draw.text((width - 8 , 5), weekDayString, (0,0,0), anchor="ra", font =dateFont)

    offsetX = 10
    offsetY = 40
    
    tempColor = (0,0,0)
    if temp_cur < -10:
        tempColor = (0,0,255)
    if temp_cur > 28:
        tempColor = (255,0,0)
    # draw date string
    draw.text((5 + offsetX , 35 + offsetY), "Temperature", tempColor,font =textFont)
    draw.text((0 + offsetX, 50 + offsetY), "%2.0fC" % temp_cur, tempColor,font =tempurtureFont)
    draw.text((5 + offsetX , 175 + offsetY), "Feels like", (0,0,0),font =textFont)
    draw.text((10 + offsetX, 200 + offsetY), "%2.0fC" % temp_cur_feels, (0,0,0),font =feelslikeFont)

    # humidity
    draw.text((width - 8, 270 + offsetY), str(humidity) + "%", (0,0,0), anchor="rs",font =textFont)

    # draw current weather icon
    draw.text((430 + offsetX, 50 + offsetY), iconMap[icon], colorMap[icon], anchor="ma",font=iconFont)

    draw.text((width - 8, 35 + offsetY), description, (0,0,0), anchor="ra", font =textFont)

    offsetY = 210
    # forecast draw : fi = forecast index (every 3 hours)
    for fi in range(4):
        finfo = forecastInfo()
        finfo.time_dt  = wi.forecastWeatherInfo[u'list'][fi][u'dt']
        finfo.time     = time.strftime('%-I %p', time.localtime(finfo.time_dt))
        #finfo.ampm     = time.strftime('%p', time.localtime(finfo.time_dt))
        #finfo.time     = time.strftime('%-I', time.localtime(finfo.time_dt))
        finfo.timePfx  = time.strftime('%p', time.localtime(finfo.time_dt))
        finfo.temp     = wi.forecastWeatherInfo[u'list'][fi][u'main'][u'temp']
        finfo.humidity = wi.forecastWeatherInfo[u'list'][fi][u'main'][u'humidity']
        finfo.icon     = wi.forecastWeatherInfo[u'list'][fi][u'weather'][0][u'icon']
        finfo.description = wi.forecastWeatherInfo[u'list'][fi][u'weather'][0][u'description'] # show the first 

        columnWidth = 600 / 4

        
        draw.text((30 + (fi * columnWidth), offsetY + 220), finfo.time, (0,0,0),anchor="la", font =smallFont)
        draw.text((120 + (fi * columnWidth), offsetY + 220), ("%2.1f" % finfo.temp), (0,0,0), anchor="ra", font=smallFont )
        
        draw.text(((columnWidth / 2) + (fi * columnWidth),  offsetY + 200), finfo.description, (0,0,0),anchor="ma", font =smallFont)
        draw.text((70 + (fi * columnWidth), offsetY + 100), iconMap[finfo.icon], colorMap[finfo.icon], anchor="ma",font =iconForecastFont)


wi = weatherInfomation()
wi.loadWeatherData()

cv = Image.new("RGB", canvasSize, (255, 255, 255))
#cv = cv.rotate(90, expand=True)
drawWeather(wi, cv)
cv.save("test.png")
#cv = cv.rotate(-90, expand=True)
inky = Inky()
inky.set_image(cv, saturation=saturation)
inky.show() 