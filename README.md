# Coin Price indicator

![Coin Price logo](https://raw.github.com/nilgradisnik/coinprice-indicator/master/resources/logo_124px.png)

Coin Price indicator is a crypto curency(Bitcoin etc) price indicator applet for Ubuntu Linux. It shows latest 24 hour price and also bid, high low, ask prices from the indicator menu.

Right now it supports the following exchanges

* [Kraken](https://www.kraken.com)
* [Bitstamp](https://www.bitstamp.net)

Exchanges can be switched from the Preferences dialog. Feel free to [contact me](mailto:nil.gradisnik@gmail.com) to implement your favorite bitcoin echange.

## Requirements
Should work on a standard Ubuntu Linux installation with python3 installed. Tested only on my machine (Ubuntu 13.10). Using python3-gi, python3-requests, python3-yaml, python3-notify2 libraries.

Install python dependencies and install [GSettings schema](https://developer.gnome.org/gio/2.32/glib-compile-schemas.html) by running the following command
```
 make install
```

## Running
Type `make` to run and the indicator should appear in the notification area.

![Screenshot](https://raw2.github.com/nilgradisnik/coinprice-indicator/master/resources/screenshot.png)

### Donations
BTC `1BVVuiix3kWsRs8qvYq8rBnDojAwdYDSJA`

LTC `LZo6VE64mBtVJ6NAJqwwjteQr9sA1688gr`
