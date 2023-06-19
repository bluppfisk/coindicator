# Coindicator

![Coin Price logo](src/coin/resources/logo_124px.png)

Coindicator is a cryptocurrency price indicator applet for Linux.

[![PyPI version](https://badge.fury.io/py/coindicator.svg)](https://badge.fury.io/py/coindicator)

## Features

* Multiple price tickers in the status bar
* Automatic trade pair discovery on supported exchanges
* Additional price points in the dropdown menu
* Audiovisual price alerts
* Adjust the refresh rate
* Thousands of cryptocurrency pairs from the following exchanges:

	* [Kraken](https://www.kraken.com)
	* [Bitstamp](https://www.bitstamp.net)
	* [Gemini](https://www.gemini.com)
	* [Binance](https://www.binance.com)
	* [Bittrex](https://bittrex.com)
	* [Bitfinex](https://www.bitfinex.com/)
	* [Poloniex](https://poloniex.com)
	* [HitBTC](https://hitbtc.com/)
	* [CEX.io](https://cex.io/)
	* [OKCoin](https://www.okcoin.cn/)
	* [Unocoin](https://www.unocoin.com/)
	* Add your own easily (See **Extending (Plugins)** below)

![Screenshot](img/screenshot.png)

## Installing

You will need Git and Python 3.5 or higher, as well as some system dependencies.

For your convenience, I've included a small install script that will install (or upgrade)
coindicator and its dependencies, as well as create a desktop icon. It will ask to elevate
permissions to install dependencies. It takes the install location as an argument.

```bash
 git clone https://github.com/bluppfisk/coindicator.git && cd coindicator
 ./install.sh /opt/coindicator  # or wherever you want it installed.
```

## Upgrading from 1.x

User data has moved to your home folder. To keep your settings, move the user.conf file to: **~/.config/coindicator/**.

## Running

* A launcher icon "Coindicator" should have been installed that can be used to start the app
* Alternatively, go to the install folder, activate the environment `source venv/bin/activate` and run the app with `coindicator`. Add ` &` to run it in the background.

## Configuring

Use the GUI to add and remove indicators (find the piggy icon), to pick assets, to set refresh frequency and to set alarms. Alternatively, edit the **~/.config/coindicator/user.conf** YAML file.

`max_decimals`: default 8. Lower if you want fewer decimals (takes priority over `significant_digits`)
`significant_digits`: default 3. Set to higher if you want more significant digits.

## Extending (Plug-ins)

Adding your own exchange plug-in is easy. Just create class file with methods for returning a ticker URL, a discovery URL, and parsing the responses from the ticker and discovery APIs. Then add the file to the `exchanges` folder.

Have a peek at the existing plug-ins (e.g. **kraken.py**) for an example and don't forget to contribute your plug-ins here on GitHub!

## Building

- Create and activate environment
- run `pip install -e .[develop]` to install required tools
- run `python3 setup.py build bdist`
- run `twine upload dist/{version}` if you want to upload to PyPi (will need credentials)

## Troubleshooting

This software was tested and found working on the following configurations:
* Ubuntu Linux 16.04 (Xenial Xurus) with Unity 7
* Ubuntu Linux 17.10 (Artful Aardvark) with GNOME 3 and Unity 7
* Ubuntu Linux 18.04 (Bionic Beaver) with GNOME 3 and Unity 7
* Ubuntu Linux 19.04 (Disco Dingo) with GNOME 3 and Unity 7
* Ubuntu Linux 19.10 (Eoan Ermine) with GNOME 3 and Unity 7
* Ubuntu Linux 20.04 (Focal Fossa) with GNOME 3
* Ubuntu Linux 20.10 (Groovy Gorilla) with GNOME 3
* Ubuntu Linux 21.04 (Hirsute Hippo) with GNOME 3
* Ubuntu Linux 21.10 (Impish Indri) with GNOME 40
* Ubuntu Linux 22.04 (Jammy Jellyfish) with GNOME 42
* Ubuntu Linux 22.10 (Kinetic Kudu) with GNOME 43
* Ubuntu Linux 23.04 (Lunar Lobster) with GNOME 44

For other systems, you may need to install LibAppIndicator support.

Before reporting bugs or issues, please try removing/renaming the **~/.config/coindicator** folder first.
