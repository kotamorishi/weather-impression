#!/usr/bin/env python3
#
# This scirpt is used to update the config file.
# You can modify the config file with any text editor.
#
import configparser
import os

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    CYELLOW = '\33[33m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


print("Weather Impression - Config")
# print multiple lines
print(
    f"""{bcolors.OKCYAN}
  __      __               __  .__                               
/  \    /  \ ____ _____ _/  |_|  |__   ___________              
\   \/\/   // __ \\\\__  \\\\   __\  |  \_/ __ \_  __ \             
 \        /\  ___/ / __ \|  | |   Y  \  ___/|  | \/             
  \__/\  /  \___  >____  /__| |___|  /\___  >__|                
       \/       \/     \/          \/     \/                    
{bcolors.CYELLOW}.__                                           .__               
|__| _____ _____________   ____   ______ _____|__| ____   ____  
|  |/     \\\\____ \_  __ \_/ __ \ /  ___//  ___/  |/  _ \ /    \ 
|  |  Y Y  \  |_> >  | \/\  ___/ \___ \ \___ \|  (  <_> )   |  \\
|__|__|_|  /   __/|__|    \___  >____  >____  >__|\____/|___|  /
         \/|__|               \/     \/     \/               \/     
         {bcolors.ENDC}""")


# config file should be the same folder.
os.chdir('/home/pi/weather-impression')
project_root = os.getcwd()
configFilePath = project_root + '/config.txt'

print(f"{bcolors.OKBLUE}Config file : " + configFilePath + f"{bcolors.ENDC}")


config = configparser.ConfigParser()
config.read_file(open(configFilePath))

print(f"{bcolors.OKCYAN}Note : Press enter to keep the current(default) value.{bcolors.ENDC}")

print(f"Please enter {bcolors.BOLD}latitude{bcolors.ENDC}")

latitude = input()
if latitude == "":
    latitude = config.get('openweathermap', 'LAT', raw=False)
    print(f"{bcolors.OKCYAN}Latitude : " + latitude + f"{bcolors.ENDC}")

print(f"Please enter {bcolors.BOLD}longitude{bcolors.ENDC}")
longitude = input()
if longitude == "":
    longitude = config.get('openweathermap', 'LON', raw=False)
    print(f"{bcolors.OKCYAN}longitude : " + longitude + f"{bcolors.ENDC}")

print("Please enter openweathermap API key")
print(f"{bcolors.OKBLUE}You can get your key at https://openweathermap.com{bcolors.ENDC}")
api_key = input()
if api_key == "":
    api_key = config.get('openweathermap', 'API_KEY', raw=False)
    print(f"{bcolors.OKCYAN}API key : " + api_key + f"{bcolors.ENDC}")


print("Please enter weather forecast interval in hours. (default : 1 hours x 4 forecasts)")
print(f"{bcolors.OKBLUE}Number 1 to 4{bcolors.ENDC}")
forecast_interval = input()
if forecast_interval == "":
    forecast_interval = config.get('openweathermap', 'FORECAST_INTERVAL', raw=False)
    print(f"{bcolors.OKCYAN}Forecast interval : " + forecast_interval + f"{bcolors.ENDC}")

# ask user to save or not
# print latitude, longitude, api_key
print("Latitude : " + f"{bcolors.OKGREEN}" + latitude + f"{bcolors.ENDC}")
print("Longitude : " + f"{bcolors.OKGREEN}" + longitude + f"{bcolors.ENDC}")
print("API key : " + f"{bcolors.OKGREEN}" + api_key + f"{bcolors.ENDC}")

print(f"{bcolors.CYELLOW}Do you want to save the configuration? (y/n){bcolors.ENDC}")
save = input()

# when user enter y, save the configuration
if save == 'y':

    config.set("openweathermap", "LAT", latitude)
    config.set("openweathermap", "LON", longitude)
    config.set("openweathermap", "API_KEY", api_key)
    config.set("openweathermap", "FORECAST_INTERVAL", forecast_interval)

    config.set("openweathermap", "one_time_message", "Configured.")
    config.set("openweathermap", "mode", "2")
    config.set("openweathermap", "TEMP_UNIT", "metric")
    config.set("openweathermap", "cold_temp", "7")
    config.set("openweathermap", "hot_temp", "27")

    with open(configFilePath, 'w') as configfile:
        config.write(configfile)

    print(f"{bcolors.OKCYAN}Configuration saved.{bcolors.ENDC}")
else:
    print(f"{bcolors.FAIL}Configuration not saved.{bcolors.ENDC}")
