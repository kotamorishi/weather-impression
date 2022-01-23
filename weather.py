#!/usr/bin/env python3
from os import path, DirEntry
import sys
import math
import calendar
from datetime import date
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from inky.inky_uc8159 import Inky, BLACK, WHITE, GREEN, RED, YELLOW, ORANGE, BLUE

saturation = 0.5

# font files
titleFontFile = "fonts/Roboto-BlackItalic.ttf"
detailFontFile = "fonts/Roboto-Black.ttf"


def update():
    background = Image.open("images/background.jpg")
    #foreground = Image.open("images/title_cover.png") # cover top white thing
    #background.paste(foreground, (0, 0), foreground)

    # draw weather forecast
    drawCalendar(background)
    #background.save("jul.png")

    # update inky impression
    try:
        inky = Inky()
        inky.set_image(background, saturation=saturation)
        inky.show()
    
