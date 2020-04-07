# Coin Price Indicator

![Coin Price logo](https://raw.github.com/nilgradisnik/coinprice-indicator/master/resources/logo_124px.png)

Coin Price Indicator is a cryptocurrency price indicator applet for Linux.

## Features

* Multiple price tickers in the status bar
* Automatic trade pair discovery on supported exchanges
* Additional price points in the dropdown menu
* Audiovisual price alerts
* Adjust the refresh rate
* Thousands of cryptocurrency pairs from the following exchanges:

	* [Kraken](https://www.kraken.com)
	* [Bitstamp](https://www.bitstamp.net)
	* [Gdax](https://www.gdax.com)
	* [Gemini](https://www.gemini.com)
	* [Binance](https://www.binance.com)
	* [Bittrex](https://bittrex.com)
	* [Bitfinex](https://www.bitfinex.com/)
	* [Bx.in.th](https://www.bx.in.th/)
	* [Poloniex](https://poloniex.com)
	* [HitBTC](https://hitbtc.com/)
	* [CEX.io](https://cex.io/)
	* [OKCoin](https://www.okcoin.cn/)
	* [Unocoin](https://www.unocoin.com/)
	* Add your own easily (See **Extending (Plugins)** below)

![Screenshot](https://raw.githubusercontent.com/nilgradisnik/coinprice-indicator/master/resources/screenshot.png)

## Installing

You will need Git and Python 3.5 or higher.
Clone the repository and install python dependencies by running the following commands:

```
 git clone https://github.com/nilgradisnik/coinprice-indicator.git
 cd coinprice-indicator
 ./install.sh
```

## Running

* Run `./run.sh` to activate the virtual environment and start the app.
* Alternatively, activate it yourself with `source bin/activate` and then run `coin/coin.py &` or `python3 coin/coin.py &` to start the app

## Configuring

Use the GUI to add and remove indicators (find the piggy icon), to pick assets, to set refresh frequency and to set alarms. Alternatively, edit the user.conf YAML file in the project root.

## Extending (Plug-ins)

Adding your own exchange plug-in is easy. Just create class file with methods for returning a ticker URL, a discovery URL, and parsing the responses from the ticker and discovery APIs. Then add the file to the `exchanges` folder.

Have a peek at the existing plug-ins (e.g. **kraken.py**) for an example and don't forget to contribute your plug-ins here on GitHub!

## Troubleshooting

This software was tested and found working on the following configurations:
* Ubuntu Linux 16.04 (Xenial Xurus) with Unity 7
* Ubuntu Linux 17.10 (Artful Aardvark) with GNOME 3
* Ubuntu Linux 18.04 (Bionic Beaver) with GNOME 3
* Ubuntu Linux 19.04 (Disco Dingo) with GNOME 3
* Ubuntu Linux 19.10 (Eoan Ermine) with GNOME 3

For GNOME 3 set-ups, you may need to install LibAppIndicator support (see point 3 below).

1. Before reporting bugs or issues, please try removing **user.conf** first and then the **.conf** files in the **/exchanges/data/** folder. Then run the application and choose **Discover Assets** from the piggy menu first.

2. If you're getting a `SyntaxError: Missing parentheses in call to 'print'.`, you may be using a Python2 library in there somewhere. Look through the error to identify which package it is. If it is `gi`, you can install the correct version with `sudo apt install python3-gi`. Additionally, you may have to uninstall the python2 gi library `pip3 uninstall gi` for it to work.  You will also need to install the libcairo2-dev library `sudo apt-get install libcairo2-dev`

3. If you're not on an Ubuntu Linux or if you're not running the Unity desktop manager, you can still get the app running (depending on the system). Here's how to do it for Ubuntu 17.10 and Ubuntu 18.04 with GNOME 3:

	* After running `make install`, run `sudo apt install gir1.2-appindicator3-0.1` to install libappindicator support.
	* On Ubuntu, install the KStatusNotifierItem/AppIndicator support shell extension for Gnome from the Ubuntu Software Installer OR
	* On other systems, get the [KStatusNotifierItem/AppIndicator support shell extension for Gnome](https://extensions.gnome.org/extension/615/appindicator-support/) (there's a browser extension to help you; follow the instructions on the page)
	* The Indicators should now show. If they don't, you may have to `sudo apt install gnome-tweak-tool` to manually activate the extension.

## Sponsorship and Funding

![Gitcoin logo](resources/gitcoin.png)

This project has been funded in the past by generous maecenas @ghettodev through [Gitcoin](https://gitcoin.co/), a platform that directs the attention of bounty hunters (coders) to open issues and feature requests on Github.

If you would like to sponsor a feature request, bug report or just donate to the project, be sure to check out [Gitcoin](https://gitcoin.co/).
