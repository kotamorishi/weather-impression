#!/bin/bash
set -e

echo "=== Weather Impression Installer ==="
echo "Supports Raspberry Pi OS Bookworm / Trixie"
echo ""

# Detect home directory and install path
INSTALL_DIR="$HOME/weather-impression"
VENV_DIR="$HOME/.virtualenvs/weather-impression"

# Install system dependencies
echo "[1/6] Installing system dependencies..."
sudo apt-get update
sudo apt-get -y install git python3-pip python3-venv libopenjp2-7 libopenblas-dev

# Install libtiff (package name varies by OS version)
sudo apt-get -y install libtiff6 || sudo apt-get -y install libtiff5 || true

# Enable SPI and I2C (required for Inky display)
echo "[2/6] Enabling SPI and I2C interfaces..."
if command -v raspi-config &> /dev/null; then
    sudo raspi-config nonint do_spi 0
    sudo raspi-config nonint do_i2c 0
    echo "  SPI and I2C enabled."
else
    echo "  raspi-config not found. Please enable SPI and I2C manually."
fi

# Release SPI CS0 pin so Inky can control it via GPIO
BOOT_CONFIG="/boot/firmware/config.txt"
if [ -f "$BOOT_CONFIG" ] && ! grep -q "dtoverlay=spi0-0cs" "$BOOT_CONFIG"; then
    sudo sed -i '/dtparam=spi=on/a dtoverlay=spi0-0cs' "$BOOT_CONFIG"
    echo "  Added spi0-0cs overlay (reboot required)."
    NEEDS_REBOOT=1
fi

# Clone or update the project
echo "[3/6] Setting up weather-impression..."
if [ -d "$INSTALL_DIR" ]; then
    echo "  Directory already exists, pulling latest..."
    cd "$INSTALL_DIR" && git pull
else
    git clone https://github.com/kotamorishi/weather-impression.git "$INSTALL_DIR"
fi

# Create virtual environment and install Python dependencies
echo "[4/6] Setting up Python virtual environment..."
mkdir -p "$(dirname "$VENV_DIR")"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

pip3 install --upgrade pip
pip3 install inky Pillow numpy matplotlib "gpiod>=2" schedule requests

deactivate

# Install Inky driver (system-level SPI/I2C support)
echo "[5/6] Installing Inky display driver..."
if [ -d "$HOME/inky" ]; then
    echo "  Inky directory already exists, pulling latest..."
    cd "$HOME/inky" && git pull
else
    cd "$HOME"
    git clone https://github.com/pimoroni/inky
fi
cd "$HOME/inky"
sudo ./install.sh

# Copy default config if needed
cd "$INSTALL_DIR"
if [ ! -f config.txt ]; then
    cp config.txt.default config.txt
    echo "  Created config.txt from default template."
fi

# Set up cron job
echo "[6/6] Setting up cron job..."
CRON_CMD="@reboot $VENV_DIR/bin/python3 $INSTALL_DIR/watcher.py >/dev/null 2>&1"
(sudo crontab -l 2>/dev/null | grep -v "weather-impression/watcher.py" || true; echo "$CRON_CMD") | sudo crontab -

echo ""
echo "=== Installation complete! ==="
echo ""
echo "Next steps:"
echo "  1. Edit $INSTALL_DIR/config.txt with your OpenWeatherMap API key"
echo "     - Set LAT and LON to your location"
echo "     - Set API_KEY from https://openweathermap.org/"
echo "  2. Or run: $VENV_DIR/bin/python3 $INSTALL_DIR/updateConfig.py"
echo "  3. Reboot to start the weather station"
echo ""
echo "To test immediately:"
echo "  $VENV_DIR/bin/python3 $INSTALL_DIR/weather.py"

if [ "${NEEDS_REBOOT:-0}" = "1" ]; then
    echo ""
    echo "*** IMPORTANT: A reboot is required to apply SPI overlay changes. ***"
    echo "    Run: sudo reboot"
fi
