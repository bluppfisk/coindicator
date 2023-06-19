#!/bin/bash
# Install system dependencies
if [[ $# -eq 0 ]]
    then
        echo "Usage: ./install.sh install_dir"
        echo "E.g. ./install.sh /opt/coindicator"
        exit 1
fi

args=("$@")

echo Installing to ${args[0]}

sudo apt-get install python3-venv python3-setuptools-scm python3-wheel python3-gi gir1.2-gtk-3.0 gir1.2-appindicator3-0.1 python3-pip patchelf -y

# some users report requiring libgirepository1.0-dev libdbus-1-dev, libcairo2-dev, build-essential
# some report having to install a newer version of cmake

# sudo apt purge --auto-remove cmake
# wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | sudo tee /etc/apt/trusted.gpg.d/kitware.gpg >/dev/null
# sudo apt-add-repository 'deb https://apt.kitware.com/ubuntu/ focal main'
# sudo apt update
# sudo apt install cmake

# Install python packages
sudo mkdir ${args[0]} 2>/dev/null
sudo python3 -m venv ${args[0]}/venv
source ${args[0]}/venv/bin/activate
sudo -H -E env PATH=$PATH pip3 install -U coindicator

# Install shortcut
cat > /tmp/coindicator.desktop << EOL

[Desktop Entry]
Name=Coindicator
GenericName=Cryptocoin price ticker
Comment=Keep track of the cryptocoin prices on various exchanges
Terminal=false
Type=Application
Categories=Utility;
Keywords=crypto;coin;ticker;price;exchange;
StartupNotify=false
Path=${args[0]}/venv/bin
Exec=coindicator
Icon=/tmp/logo_248px.png
EOL

cp ./src/coin/resources/logo_248px.png /tmp


desktop-file-install --dir=$HOME/.local/share/applications /tmp/coindicator.desktop
