#!/bin/bash
set -e

echo "=== Weather Impression Installer ==="
echo "Supports Raspberry Pi OS Bookworm / Trixie"
echo ""

# Detect home directory and install path
INSTALL_DIR="$HOME/weather-impression"
VENV_DIR="$HOME/.virtualenvs/weather-impression"

# Install system dependencies
echo "[1/5] Installing system dependencies..."
sudo apt-get update
sudo apt -y install git python3-pip python3-venv libopenjp2-7 libatlas-base-dev libopenblas-dev

# Install libtiff (package name varies by OS version)
sudo apt -y install libtiff6 2>/dev/null || sudo apt -y install libtiff5

# Clone or update the project
echo "[2/5] Setting up weather-impression..."
if [ -d "$INSTALL_DIR" ]; then
    echo "  Directory already exists, pulling latest..."
    cd "$INSTALL_DIR" && git pull
else
    git clone https://github.com/kotamorishi/weather-impression.git "$INSTALL_DIR"
fi

# Create virtual environment and install Python dependencies
echo "[3/5] Setting up Python virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

pip3 install --upgrade pip
pip3 install Pillow numpy matplotlib gpiod schedule requests

deactivate

# Install Inky driver (uses Pimoroni's installer)
echo "[4/5] Installing Inky display driver..."
if [ -d "$HOME/inky" ]; then
    echo "  Inky directory already exists, pulling latest..."
    cd "$HOME/inky" && git pull
else
    cd "$HOME"
    git clone https://github.com/pimoroni/inky
fi
cd "$HOME/inky"
./install.sh

# Copy default config if needed
cd "$INSTALL_DIR"
if [ ! -f config.txt ]; then
    cp config.txt.default config.txt
    echo "  Created config.txt from default template."
fi

# Set up cron job
echo "[5/5] Setting up cron job..."
CRON_CMD="@reboot $VENV_DIR/bin/python3 $INSTALL_DIR/watcher.py >/dev/null 2>&1"
(sudo crontab -l 2>/dev/null | grep -v "weather-impression/watcher.py"; echo "$CRON_CMD") | sudo crontab -

echo ""
echo "=== Installation complete! ==="
echo ""
echo "Next steps:"
echo "  1. Edit $INSTALL_DIR/config.txt with your OpenWeatherMap API key"
echo "  2. Or run: $VENV_DIR/bin/python3 $INSTALL_DIR/updateConfig.py"
echo "  3. Reboot to start the weather station"
