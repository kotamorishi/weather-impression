#!/usr/bin/env python3
from os import path, DirEntry
import os
import sys
import math
import time
import calendar
from datetime import date
from datetime import datetime
import re

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from inky.inky_uc8159 import Inky, BLACK, WHITE, GREEN, RED, YELLOW, ORANGE, BLUE

saturation = 0.5
canvasSize = (600, 448)

# font file path(Adjust or change whatever you want)
project_root = os.getcwd()
defaultFont = project_root + "/fonts/Roboto-Black.ttf"
lightFont = project_root + "/fonts/Roboto-Light.ttf"
thinFont = project_root + "/fonts/Roboto-Thin.ttf"

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
    '01n':(255, 255, 0),
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
    '13d':(0,0,255), # snow
    '13n':(0,0,255),
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
    'clock12':u'',

    'celsius':u''
}

#empty structure
class forecastInfo:
    pass



class weatherInfomation(object):
    def __init__(self):
        #load configuration from config.txt using configparser
        import configparser
        self.config = configparser.ConfigParser()
        try:
            self.config.read_file(open(project_root + '/config.txt'))
            self.lat = self.config.get('openweathermap', 'LAT', raw=False)
            self.lon = self.config.get('openweathermap', 'LON', raw=False)
            self.show_warn = self.config.get('openweathermap', 'SHOW_WARN', raw=False)
            self.forecast_interval = self.config.get('openweathermap', 'FORECAST_INTERVAL', raw=False)
            self.api_key = self.config.get('openweathermap', 'API_KEY', raw=False)
            # API document at https://openweathermap.org/api/one-call-api
            self.forecast_api_uri = 'https://api.openweathermap.org/data/2.5/onecall?&lat=' + self.lat + '&lon=' + self.lon +'&appid=' + self.api_key + '&exclude=daily&units=metric'
            self.loadWeatherData()
        except:
            self.one_time_message = "Configuration file is not found or settings are wrong.\n\nplease check the file : " + project_root + "/config.txt"
            return

        # load one time messge and remove it from the file. one_time_message can be None.
        try:
            self.one_time_message = self.config.get('openweathermap', 'one_time_message', raw=False)
            self.config.set("openweathermap", "one_time_message", "")
            # remove it.
            with open(project_root + '/config.txt', 'w') as configfile:
                self.config.write(configfile)
        except:
            self.one_time_message = ""
            pass

    def loadWeatherData(self):
        import requests
        self.weatherInfo = requests.get(self.forecast_api_uri).json()

# draw current weather and forecast into canvas
def drawWeather(wi, cv):
    draw = ImageDraw.Draw(cv)
    width, height = cv.size
    
    dateFont = ImageFont.truetype(defaultFont, 64)
    textFont = ImageFont.truetype(lightFont, 24)
    textBoldFont = ImageFont.truetype(defaultFont, 22)
    tempurtureFont = ImageFont.truetype(defaultFont, 120)
    feelslikeFont = ImageFont.truetype(defaultFont, 50)
    smallFont = ImageFont.truetype(defaultFont, 16)
    textFont12 = ImageFont.truetype(defaultFont, 12)
    lightFont14 = ImageFont.truetype(lightFont, 14)

    iconFont = ImageFont.truetype(project_root + "fonts/weathericons-regular-webfont.ttf", 160)
    iconForecastFont = ImageFont.truetype(project_root + "fonts/weathericons-regular-webfont.ttf", 80)
    iconFeelslikeFont = ImageFont.truetype(project_root + "fonts/weathericons-regular-webfont.ttf", 50)

    # one time message
    if hasattr( wi, "weatherInfo") == False:
        draw.text((width / 2, height / 2), wi.one_time_message, (255,0,0), anchor="mm", font=smallFont )
        return
    draw.text((width - 10, 2), wi.one_time_message, (0,0,0), anchor="ra", font=textFont12 )
    
    temp_cur = wi.weatherInfo[u'current'][u'temp']
    temp_cur_feels = wi.weatherInfo[u'current'][u'feels_like']
    icon = str(wi.weatherInfo[u'current'][u'weather'][0][u'icon'])
    description = wi.weatherInfo[u'current'][u'weather'][0][u'description']
    humidity = wi.weatherInfo[u'current'][u'humidity']
    pressure = wi.weatherInfo[u'current'][u'pressure']
    epoch = int(wi.weatherInfo[u'current'][u'dt'])
    dateString = time.strftime("%B %-d", time.localtime(epoch))
    weekDayString = time.strftime("%a", time.localtime(epoch))
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
    draw.text((0 + offsetX, 50 + offsetY), "%2.0f" % temp_cur, tempColor,font =tempurtureFont)
    temperatureTextSize = draw.textsize("%2.0f" % temp_cur, font =tempurtureFont)
    draw.text((temperatureTextSize[0] + 10 + offsetX, 85 + offsetY), iconMap['celsius'], tempColor, anchor="la", font =iconForecastFont)
    # humidity
    # draw.text((width - 8, 270 + offsetY), str(humidity) + "%", (0,0,0), anchor="rs",font =textFont)

    # draw current weather icon
    draw.text((440 + offsetX, 40 + offsetY), iconMap[icon], colorMap[icon], anchor="ma",font=iconFont)

    draw.text((width - 8, 35 + offsetY), description, (0,0,0), anchor="ra", font =textFont)

    offsetY = 210
    
    # When alerts are in effect, show it to forecast area.
    if wi.show_warn == '1' and u'alerts' in wi.weatherInfo:
        alertInEffectString = time.strftime('%B %-d, %H:%m %p', time.localtime(wi.weatherInfo[u'alerts'][0][u'start']))
        #+ " - " + time.strftime('%B %-d, %-I %p', time.localtime(wi.weatherInfo[u'alerts'][0][u'end']))
        # + " from " + str(wi.weatherInfo[u'alerts'][0][u'sender_name'])

        # remove "\n###\n" and \n\n
        desc = wi.weatherInfo[u'alerts'][0][u'description'].replace("\n###\n", '')
        desc = desc.replace("\n\n", '')
        desc = desc.replace("https://", '') # remove https://
        desc = re.sub(r"([A-Za-z]*:)", "\n\g<1>", desc)
        #print(desc)
        #desc = re.sub(r"([A-Za-z]*\.)", "\g<1>\n", desc)
        #desc = re.sub(r"([A-Za-z]*\.)", "\g<1>\n", desc)
        desc = re.sub(r'((?=.{90})(.{0,89}([\.[ ]|[ ]))|.{0,89})', "\g<1>\n", desc)

        desc = desc.replace("\n\n", '')
#        desc = re.sub(r"^\n", "HAHAHA", desc) # eliminate blank lines
        
        #desc  = re.sub("(.{150})", "\\1\n", desc, 0, re.DOTALL)
        #print("=========>")
        #print(desc)


        descFont = ImageFont.truetype(defaultFont, 14)

        draw.text((5 + offsetX , 215), wi.weatherInfo[u'alerts'][0][u'event'].capitalize() , (255,0,0),anchor="la", font =textFont)
        draw.text((5 + offsetX , 240), alertInEffectString + "/" + wi.weatherInfo[u'alerts'][0][u'sender_name'] , (0,0,0), font=textFont12)

        draw.text((5 + offsetX, 270), desc, (255,0,0),anchor="la", font =descFont)
        return
    # feels like
    draw.text((5 + offsetX , 175 + 40), "Feels like", (0,0,0),font =textFont)
    draw.text((10 + offsetX, 200 + 40), "%2.0f" % temp_cur_feels, (0,0,0),font =feelslikeFont)
    feelslikeTextSize = draw.textsize("%2.0f" % temp_cur_feels, font =feelslikeFont)
    draw.text((feelslikeTextSize[0] + 20 + offsetX, 200 + 40), iconMap['celsius'], tempColor, anchor="la", font =iconFeelslikeFont)

    # Pressure
    draw.text((feelslikeTextSize[0] + 85 + offsetX , 175 + 40), "Pressure", (0,0,0),font =textFont)
    draw.text((feelslikeTextSize[0] + 90 + offsetX, 200 + 40), "%d" % pressure, (0,0,0),font =feelslikeFont)
    pressureTextSize = draw.textsize("%d" % pressure, font =feelslikeFont)
    draw.text((feelslikeTextSize[0] + pressureTextSize[0] + 95 + offsetX, 224 + 40), "hPa", (0,0,0),font=textBoldFont)
    
    
    #draw.rectangle(((0, 405), (width, height)), fill=(230, 230, 230), outline=None, width=1)
    forecastIntervalHours = int(wi.forecast_interval)
    forecastRange = 4
    for fi in range(forecastRange):
        finfo = forecastInfo()
        finfo.time_dt  = wi.weatherInfo[u'hourly'][fi * forecastIntervalHours + forecastIntervalHours][u'dt']
        finfo.time     = time.strftime('%-I %p', time.localtime(finfo.time_dt))
        finfo.timeIn12h = time.strftime('clock%-I', time.localtime(finfo.time_dt))
        #finfo.ampm     = time.strftime('%p', time.localtime(finfo.time_dt))
        #finfo.time     = time.strftime('%-I', time.localtime(finfo.time_dt))
        finfo.timePfx  = time.strftime('%p', time.localtime(finfo.time_dt))
        finfo.temp     = wi.weatherInfo[u'hourly'][fi * forecastIntervalHours + forecastIntervalHours][u'temp']
        finfo.humidity = wi.weatherInfo[u'hourly'][fi * forecastIntervalHours + forecastIntervalHours][u'humidity']
        finfo.pressure = wi.weatherInfo[u'hourly'][fi * forecastIntervalHours + forecastIntervalHours][u'pressure']
        finfo.icon     = wi.weatherInfo[u'hourly'][fi * forecastIntervalHours + forecastIntervalHours][u'weather'][0][u'icon']
        finfo.description = wi.weatherInfo[u'hourly'][fi * forecastIntervalHours + forecastIntervalHours][u'weather'][0][u'description'] # show the first 

        columnWidth = width / forecastRange
        textColor = (50,50,50)
        # Clock icon for the time.(Not so nice.)
        #draw.text((20 + (fi * columnWidth),  offsetY + 90), iconMap[finfo.timeIn12h], textColor, anchor="ma",font =ImageFont.truetype(project_root + "fonts/weathericons-regular-webfont.ttf", 35))
        draw.text((30 + (fi * columnWidth), offsetY + 220), finfo.time,textColor,anchor="la", font =smallFont)
        draw.text((120 + (fi * columnWidth), offsetY + 220), ("%2.1f" % finfo.temp), textColor, anchor="ra", font=smallFont )
        
        draw.text(((columnWidth / 2) + (fi * columnWidth),  offsetY + 200), finfo.description, textColor,anchor="ma", font =smallFont)
        draw.text((70 + (fi * columnWidth), offsetY + 90), iconMap[finfo.icon], colorMap[finfo.icon], anchor="ma",font =iconForecastFont)


def update():
    wi = weatherInfomation()

    cv = Image.new("RGB", canvasSize, (255, 255, 255))
    #cv = cv.rotate(90, expand=True)
    drawWeather(wi, cv)
    #cv.save("test.png")
    #cv = cv.rotate(-90, expand=True)
    inky = Inky()
    inky.set_image(cv, saturation=saturation)
    inky.show()

if __name__ == "__main__":
    update()