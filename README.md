# Coin Price indicator

![Coin Price logo](https://raw.github.com/nilgradisnik/coinprice-indicator/master/resources/logo_124px.png)

Coin Price indicator is a cryptocurrency (such as Bitcoin) price indicator applet for Ubuntu Linux. It shows various price points (depending on what the exchange API provides) in the indicator menu.

Right now it supports the following exchanges:

* [Kraken](https://www.kraken.com)
* [Bitstamp](https://www.bitstamp.net)
* [BitYep](https://bityep.com)
* [Gdax](https://www.gdax.com)

Exchanges can be switched from the menu. Feel free to [contact me](mailto:nil.gradisnik@gmail.com) to implement your favorite cryptocurrency exchange.

![Screenshot](https://raw.githubusercontent.com/nilgradisnik/coinprice-indicator/master/resources/screenshot.png)


## Installation
Should work on a standard Ubuntu Linux installation with python3 installed. Tested on Ubuntu 16.04). Using python3-gi, python3-requests, python3-yaml, python3-notify2 libraries.

Install python dependencies and install [GSettings schema](https://developer.gnome.org/gio/2.32/glib-compile-schemas.html) by running the following command
```
 make install
```

## Running
To run the indicator with the default settings or with the previous settings, type `make` to run and the indicator should appear in the notification area. Alternatively, you can run `python3 coin/coin.py` to configure the app.

## Configuration
Coin.py takes two parameters to configure the instance(s):

* `python3 coin/coin.py asset=kraken:XXBTZEUR:30` will launch a single indicator for the asset pair XBT/EUR on the Kraken exchange with a refresh rate of 30 seconds. Asset pairs must always be in this format: `X XBT Z EUR` where `X` means `from` and `Z` means `to`. According to the ISO standard, currencies that are not bound to a country take an X as the first letter of their abbreviation, hence `XBT` for Bitcoin.

* `python3 coin/coin.py file=startmany.yaml` will read startmany.yaml from the `coin` directory and start an indicator for each configuration it finds in there. Take a peek in `startmany.yaml`for examples and edit it to configure the exchanges, currency pairs and refresh rates for each instance.

## Known Issues

* [#10](https://github.com/nilgradisnik/coinprice-indicator/issues/10) App sometimes freezes after suspending and resuming the computer. Workaround: Kill the app manually or exit it before resuming.
