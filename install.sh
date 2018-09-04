#!/bin/bash
sudo apt install -y virtualenv
virtualenv ./
source ./bin/activate
pip3 install -r requirements.txt
vext -i gi.vext
sudo chmod u+x coin/coin.py
deactivate