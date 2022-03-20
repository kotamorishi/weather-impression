cp config.txt.default config.txt


#write out current crontab(Just in case..)
sudo crontab -l > mycron
#echo new cron into cron file
echo "@reboot /usr/bin/python3 /home/pi/weather-impression/watcher.py >/dev/null 2>&1" >> mycron
#install new cron file
sudo crontab mycron
rm mycron
