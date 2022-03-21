sudo apt-get update
sudo apt -y install git python3-pip libopenjp2-7 libtiff5 libatlas-base-dev
sudo -H pip3 install Pillow
sudo -H pip3 install numpy
sudo -H pip3 install matplotlib
sudo -H pip3 install gpiod
sudo -H pip3 install schedule

# download and install e-paper driver.
cd ~
git clone https://github.com/pimoroni/inky
cd inky
sudo ./install.sh

# download the app
cd ~
git clone https://github.com/kotamorishi/weather-impression

cd ~/weather-impression
# copy default configuration file
cp config.txt.default config.txt

#write out current crontab(Just in case..)
sudo crontab -l > mycron
#echo new cron into cron file
echo "@reboot /usr/bin/python3 /home/pi/weather-impression/watcher.py >/dev/null 2>&1" >> mycron
#install new cron file
sudo crontab mycron
rm mycron

echo "Run python3 updateConfig.py"
#/usr/bin/python3 /home/pi/weather-impression/updateConfig.py
