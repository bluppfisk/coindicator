#!/bin/bash
sudo apt-get install libcairo2-dev libdbus-glib-1-2 gir1.2-gtk-3.0 gir1.2-appindicator3-0.1
python3 -m venv ./
source ./bin/activate
pip3 install -r requirements.txt
vext -i gi.vext
chmod u+x coin/coin.py
deactivate
