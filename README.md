
# Coin Price indicator

![Coin Price logo](https://raw.github.com/nilgradisnik/coinprice-indicator/master/resources/logo_124px.png)

Coin Price indicator is a crypto curency(Bitcoin etc) price indicator applet for Ubuntu Linux. It shows latest 24 hour price and also bid, high low, ask prices from the indicator menu.

Right now it supports the following exchanges

* [Kraken](https://www.kraken.com)
* [Bitstamp](https://www.bitstamp.net)

Exchanges can be switched from the Preferences dialog.

## Requirements
Should work on a standard Ubuntu Linux installation with python3 installed. Tested only on my machine (Ubuntu 13.10). Using python3-gi, python3-requests, python3-yaml python3-notify libraries.

## Running
Type `make` to run and the indicator should appear in the notification area.

### Author
Nil Gradisnik <nil.gradisnik@gmail.com>