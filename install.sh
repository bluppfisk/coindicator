#!/bin/bash
# Install system dependencies
sudo apt-get install python3-venv python3-gi python3-gi-cairo gir1.2-gtk-3.0 libdbus-glib-1-2 gir1.2-appindicator3-0.1 python3-pip -y

# Install python packages
pip3 install --user .

# Install shortcut
echo Path=`pwd` >> coindicator.desktop
echo Exec=coin >> coindicator.desktop
echo Icon=`pwd`/src/coin/resources/logo_248px.png >> coindicator.desktop
desktop-file-install --dir=$HOME/.local/share/applications coindicator.desktop
