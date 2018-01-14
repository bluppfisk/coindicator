# Coin Price Indicator

![Coin Price logo](https://raw.github.com/nilgradisnik/coinprice-indicator/master/resources/logo_124px.png)

Coin Price indicator is a cryptocurrency (such as Bitcoin) price indicator applet for Ubuntu Linux. It shows various price points (depending on what the exchange API provides) in the indicator menu.

It currently supports the following exchanges:

* [Kraken](https://www.kraken.com)
* [Bitstamp](https://www.bitstamp.net)
* [Gdax](https://www.gdax.com)
* [Gemini](https://www.gemini.com)
* [Bittrex](https://bittrex.com)
* [Bitfinex](https://www.bitfinex.com/)
* [Bx](https://www.bx.in.th/)

**NEW**: Since version 0.9 you can easily add your own exchanges (see *Extending* below).

![Screenshot](https://raw.githubusercontent.com/nilgradisnik/coinprice-indicator/master/resources/screenshot.png)

## Installation
Tested and working on Ubuntu Linux 16.04 with Unity. On other systems and desktop managers (e.g. Ubuntu 17.10 with Gnome3), you can get the app working by installing Libappindicator support (see troubleshooting below).

Install python dependencies and install [GSettings schema](https://developer.gnome.org/gio/2.32/glib-compile-schemas.html) by running the following command
```
 make install
```

## Running
* To run the indicator with the default settings or with the previous settings, type `make` to run and the indicator should appear in the notification area.
* Alternatively, you can run `python3 coin/coin.py` to start the app (this will also let you specify an asset pair--see below).
* In order to run the exchanges defined in `startmany.yaml`, run `make many`.

## Configuration
Coin.py takes two optional parameters to configure the instance(s):

* `python3 coin/coin.py asset=kraken:XXBTZEUR:30` will launch a single indicator for the asset pair XBT/EUR on the Kraken exchange with a refresh rate of 30 seconds. Asset pairs must always be in this format: `X XBT Z EUR` where `X` means `from` and `Z` means `to`. According to the ISO standard, currencies that are not bound to a country take an X as the first letter of their abbreviation, hence `XBT` for Bitcoin.

* `python3 coin/coin.py file=startmany.yaml` will read startmany.yaml from the `coin` directory and start an indicator for each configuration it finds in there. Take a peek in `startmany.yaml`for examples and edit it to configure the exchanges, currency pairs and refresh rates for each instance.

## Extending (plug-ins)
Adding your own exchange plug-in is easy. Just create class file with methods for returning a ticker URL and parsing the response from the ticker API and add the file to the `exchanges` folder. Have a peek at the existing plug-ins for an example and don't forget to contribute your plug-ins here on GitHub!

## Troubleshooting
- If you're getting a BitYep error, please run `make install` again, it will now clear any old and or corrupted dconf settings before copying in the new settings schema.

- If you're getting a `SyntaxError: Missing parentheses in call to 'print'.`, you may be using a Python2 library in there somewhere. Look through the error to identify which package it is. If it is `gi`, you can install the correct version with `sudo apt install python3-gi`. Additionally, you may have to uninstall the python2 gi library `pip3 uninstall gi` for it to work.

- If you're not on an Ubuntu Linux or if you're not running the Unity desktop manager, you can still get the app running (depending on the system). Here's how to do it for Ubuntu 17.10 with Gnome3:

	* After running `make install`, run `sudo apt install gir1.2-appindicator3-0.1` to install libappindicator support.
	* On Ubuntu, install the KStatusNotifierItem/AppIndicator support shell extension for Gnome from the Ubuntu Software Installer OR
	* On other systems, get the [KStatusNotifierItem/AppIndicator support shell extension for Gnome](https://extensions.gnome.org/extension/615/appindicator-support/) (there's a browser extension to help you; follow the instructions on the page)
	* The Indicators should now show. If they don't, you may have to `sudo apt install gnome-tweak-tool` to manually activate the extension.