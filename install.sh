#!/bin/bash
# Install system dependencies
sudo apt-get install python3-venv python3-gi python3-gi-cairo gir1.2-gtk-3.0 libdbus-glib-1-2 gir1.2-appindicator3-0.1 python3-pip -y

# Install python packages
pip3 install -U coindicator

# Install shortcut
cat > coindicator.desktop << EOL

[Desktop Entry]
Name=Coindicator
GenericName=Cryptocoin price ticker
Comment=Keep track of the cryptocoin prices on various exchanges
Terminal=false
Type=Application
Categories=Utility;Network;
Keywords=crypto;coin;ticker;price;exchange;
StartupNotify=false
Path=`pwd`
Exec=coin
Icon=`pwd`/src/coin/resources/logo_248px.png
EOL

desktop-file-install --dir=$HOME/.local/share/applications coindicator.desktop
