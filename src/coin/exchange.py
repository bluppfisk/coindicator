# Abstract class that provides functionality for the various exchange classes
import abc
import logging
import pickle
import time

from gi.repository import GLib
from coin.coingecko_client import CoinGeckoClient

from coin.config import Config
from coin.downloader import DownloadCommand
from coin.error import Error

CURRENCY = {
    "usd": "$",
    "eur": "€",
    "btc": "B",
    "thb": "฿",
    "gbp": "£",
    "eth": "Ξ",
    "cad": "$",
    "jpy": "¥",
    "cny": "元",
    "inr": "₹",
}

CATEGORY = {
    "cur": "Now",
    "bid": "Bid",
    "high": "High",
    "low": "Low",
    "ask": "Ask",
    "vol": "Vol",
    "first": "First",
    "avg": "Avg",
}


class Exchange(abc.ABC):
    active = True
    name = "Must be overwritten"
    code = "Must be overwritten"
    default_label = "Must be overwritten"

    def __init__(self, indicator=None):
        self.indicator = indicator
        self.downloader = indicator.coin.downloader
        self.timeout_id = None
        self.error = Error(self)
        self.started = False
        self.asset_pair = {}
        self.config = Config()

    ##
    # Abstract methods to be overwritten by the child classes
    #
    @classmethod
    @abc.abstractmethod
    def _get_discovery_url(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def _parse_discovery(cls, data):
        pass

    @abc.abstractmethod
    def _get_ticker_url(self):
        pass

    @abc.abstractmethod
    def _parse_ticker(self, data):
        pass

    @property
    def currency(self):
        return self.asset_pair.get("quote").lower()

    @property
    def symbol(self):
        return CURRENCY.get(self.currency, self.currency.upper())

    @property
    def icon(self) -> str:
        # set icon for asset if it exists
        asset = self.asset_pair.get("base", "").lower()
        asset_dir = Config()["icon_dir"]
        if (asset_dir / f"{asset}.png").exists():
            return asset_dir / f"{asset}.png"
        else:
            fetched = CoinGeckoClient().get_icon(asset)
            if fetched is not None:
                return fetched

        return asset_dir / "unknown-coin.png"

    @property
    def volume_currency(self):
        return self.asset_pair.get("volumecurrency", self.asset_pair.get("base"))

    def set_asset_pair(self, base, quote):
        for ap in self.asset_pairs:
            if (
                ap.get("base").upper() == base.upper()
                and ap.get("quote").upper() == quote.upper()
            ):
                self.asset_pair = ap
                break

        if not self.asset_pair:
            logging.warning(
                "User.conf specifies unavailable asset pair, trying default. \
                Run Asset Discovery again."
            )
            self.asset_pair = ap

    def set_asset_pair_from_code(self, code):
        for ap in self.asset_pairs:
            if ap.get("pair").upper() == code.upper():
                self.asset_pair = ap
                break

        if not self.asset_pair:
            logging.warning(
                "User.conf specifies unavailable asset pair, trying default. \
                Run Asset Discovery again."
            )
            self.asset_pair = {}

    @classmethod
    def find_asset_pair_by_code(cls, code):
        for ap in cls.asset_pairs:
            if ap.get("pair") == code:
                return ap

        return {}

    @classmethod
    def find_asset_pair(cls, quote, base):
        for ap in cls.asset_pairs:
            if ap.get("quote") == quote and ap.get("base") == base:
                return ap

        return {}

    @classmethod
    @property
    def datafile(cls):
        config = Config()
        return config["user_data_dir"] / f"cache/{cls.code}.cache"

    ##
    # Loads asset pairs from the config files or,
    # failing that, from the hard-coded lines
    #
    @classmethod
    @property
    def asset_pairs(cls):
        try:
            with open(cls.datafile, "rb") as stream:
                asset_pairs = pickle.load(stream)
                return asset_pairs if asset_pairs else []

        except IOError:
            # Faulty data file, return empty array
            return []

    ##
    # Saves asset pairs to disk
    #
    @classmethod
    def store_asset_pairs(cls, asset_pairs):
        try:
            with open(cls.datafile, "wb") as stream:
                pickle.dump(asset_pairs, stream)
        except IOError:
            logging.error("Could not write to data file %s" % cls.datafile)

    ##
    # Discovers assets from the exchange's API url retrieved
    # through the instance-specific method _get_discovery_url()
    #
    @classmethod
    def discover_assets(cls, downloader, callback):
        if cls._get_discovery_url() is None:
            cls.store_asset_pairs(cls._parse_discovery(None))
        else:
            command = DownloadCommand(cls._get_discovery_url(), callback)
            downloader.execute(command, cls._handle_discovery_result)

    ##
    # Deals with the result from the discovery HTTP request
    # Should probably be merged with _handle_result() later
    #
    @classmethod
    def _handle_discovery_result(cls, command):
        logging.debug("Response from %s: %s" % (command.url, command.error))

        if command.error:
            cls._handle_discovery_error(
                f"{cls.name}: API server {command.url}\
                     returned an error: {command.error}"
            )

        if command.response:
            data = command.response

            if data.status_code in [301, 302]:
                # hooks will be called even when requests is following a redirect
                # but we don't want to print any error messages here
                return

            if data.status_code != 200:
                cls._handle_discovery_error(
                    f"API server {command.url} returned \
                        an error: {str(data.status_code)}"
                )

            try:
                result = data.json()
                asset_pairs = cls._parse_discovery(result)
                cls.store_asset_pairs(asset_pairs)
            except Exception as e:
                cls._handle_discovery_error(str(e))

        command.callback()  # update the asset menus of all instances

    @classmethod
    def _handle_discovery_error(cls, msg):
        logging.warn("Asset Discovery: %s" % msg)

    ##
    # Start exchange
    #
    def start(self, error_refresh=None):
        if not self.started:
            self._check_price()

        self.started = True
        refresh = error_refresh if error_refresh else self.indicator.refresh_frequency
        self.timeout_id = GLib.timeout_add_seconds(refresh, self._check_price)

        return self

    ##
    # Stop exchange, reset errors
    #
    def stop(self):
        if self.timeout_id:
            GLib.source_remove(self.timeout_id)

        self.started = False
        self.indicator.alarm.deactivate()
        self.error.reset()

        return self

    ##
    # Restarts the exchange. This is necessary for restoring normal frequency as
    # False must be returned for the restart operation to be done only once
    #
    def restart(self):
        self.start()
        return False

    ##
    # This function is called frequently to get price updates from the API
    #
    def _check_price(self):
        self.pair = self.asset_pair.get("pair")
        timestamp = time.time()
        command = DownloadCommand(self._get_ticker_url(), self.indicator.update_gui)
        command.timestamp = timestamp
        command.error = self._handle_error
        command.validation = self.asset_pair
        self.downloader.execute(command, self._handle_result)

        logging.debug("Request with TS: " + str(timestamp))
        if not self.error.is_ok():
            self.timeout_id = None

        return self.error.is_ok()  # continues the timer if there are no errors

    def _handle_error(self, error):
        self.error.log(str(error))
        self.error.increment()

    # def _handle_result(self, data, validation, timestamp):
    def _handle_result(self, command):
        if not command.response:
            logging.warning("No response from API server")
            return
        data = command.response
        # Check to see if the returning response is still valid
        # (user may have changed exchanges before the request finished)
        if not self.started:
            logging.warning("Discarding packet for inactive exchange")
            return

        if command.validation is not self.asset_pair:  # we've already moved on.
            logging.warning("Discarding packet for wrong asset pair or exchange")
            return

        # also check if a newer response hasn't already been returned
        if (
            command.timestamp < self.indicator.latest_response
        ):  # this is an older request
            logging.warning("Discarding outdated packet")
            return

        if data.status_code != 200:
            self._handle_error("API server returned an error: " + str(data.status_code))
            return

        try:
            asset = data.json()
        except Exception:
            # Before, a KeyError happened when an asynchronous response comes in
            # for a previously selected asset pair (see upstream issue #27)
            self._handle_error("Invalid response for " + str(self.pair))
            return

        results = self._parse_ticker(asset)
        self.indicator.latest_response = command.timestamp
        logging.debug(
            "Response comes in with timestamp %s, last response at %s"
            % (str(command.timestamp), str(self.indicator.latest_response))
        )

        for item in CATEGORY:
            if results.get(item):
                self.indicator.prices[item] = self._decimal_auto(results.get(item))

        self.error.reset()

        GLib.idle_add(command.callback)

    ##
    # Rounds a number to a meaningful number of decimal places
    # and returns it as a string
    #
    def _decimal_auto(self, number):
        number = float(number)
        max_decimals = self.config["settings"].get("max_decimals", 8)
        significant_digits = self.config["settings"].get("significant_digits", 3)

        for decimals in range(0, max_decimals + 1):
            if number * (10**decimals) >= 10 ** (significant_digits - 1):
                break

        return ("{0:." + str(decimals) + "f}").format(number)
