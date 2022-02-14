#!/bin/bash
# Install system dependencies
sudo apt-get install python3-venv libcairo2-dev libdbus-glib-1-2 gir1.2-gtk-3.0 gir1.2-appindicator3-0.1 python3-pip -y
pip3 install pygame
# Install environment
python3 -m venv --system-site-packages ./
source ./bin/activate
# Install python packages
pip3 install -r requirements.txt
chmod u+x coin/coin.py
deactivate
# Install shortcut
echo Exec=`pwd`/run.sh >> coindicator.desktop
echo Icon=`pwd`/resources/logo_248px.png >> coindicator.desktop
desktop-file-install --dir=$HOME/.local/share/applications coindicator.desktop
