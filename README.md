
# Coin Price indicator
This is a crypto curency price indicator applet for Ubuntu Linux. It shows latest 24 hour price and also bid, high low, ask prices from the menu.

Right now it supports the following exchanges

* [Kraken](https://www.kraken.com)
* [Bitstamp](https://www.bitstamp.net)

Exchanges can be switched from the Preferences dialog.

## Requirements
Should work on a standard Ubuntu Linux installation. Tested only on my machine (Ubuntu 13.10). Using python-gtk2, python-appindicator, python-gobject, python-requests, python-yaml libraries.

## Running
Type `make` to run and the indicator should appear in the notification area.

### Author
Nil Gradisnik <nil.gradisnik@gmail.com>