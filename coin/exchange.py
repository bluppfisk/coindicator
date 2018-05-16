# Abstract class that provides functionality for the various exchange classes

import logging
import time
import pickle

from gi.repository import GLib
from error import Error
from async_downloader import DownloadCommand

CURRENCY = {
    'usd': '$',
    'eur': '€',
    'btc': 'B',
    'thb': '฿',
    'gbp': '£',
    'eth': 'Ξ',
    'cad': '$',
    'jpy': '¥'
}

CATEGORY = {
    'cur': 'Now',
    'bid': 'Bid',
    'high': 'High',
    'low': 'Low',
    'ask': 'Ask',
    'vol': 'Vol',
    'first': 'First'
}


class Exchange(object):
    def __init__(self, indicator=None):
        self.indicator = indicator
        self.downloader = indicator.coin.downloader
        self.timeout_id = None
        self.error = Error(self)
        self.started = False
        self.asset_pair = {}

    ##
    # Abstract methods to be overwritten by the child classes
    #
    @classmethod
    def _get_discovery_url():
        pass

    @classmethod
    def _parse_discovery(data):
        pass

    def _get_ticker_url(self):
        pass

    @classmethod
    def _parse_ticker(self, data):
        pass

    ##
    # Getters and setters follow
    #
    @classmethod
    def get_name(cls):
        return cls.name

    @classmethod
    def get_code(cls):
        return cls.code

    @classmethod
    def get_default_label(cls):
        return cls.default_label

    def get_asset_pair(self):
        return self.asset_pair

    def get_currency(self):
        return self.asset_pair.get('quote').lower()

    def get_symbol(self):
        return CURRENCY.get(self.get_currency(), self.get_currency().upper())

    def get_volume_currency(self):
        return self.asset_pair.get('volumecurrency', self.asset_pair.get('base'))

    def set_asset_pair(self, base, quote):
        for ap in self.get_asset_pairs():
            if ap.get('base').upper() == base.upper() and ap.get('quote').upper() == quote.upper():
                self.asset_pair = ap
                break

        if not self.asset_pair:
            logging.warning("User.conf specifies unavailable asset pair, trying default. Run Asset Discovery again.")
            self.asset_pair = ap

    def set_asset_pair_from_code(self, code):
        for ap in self.get_asset_pairs():
            if ap.get('pair').upper() == code.upper():
                self.asset_pair = ap
                break

        if not self.asset_pair:
            logging.warning("User.conf specifies unavailable asset pair, trying default. Run Asset Discovery again.")
            self.asset_pair = ap

    @classmethod
    def find_asset_pair_by_code(cls, code):
        for ap in cls.get_asset_pairs():
            if ap.get('pair') == code:
                return ap

    @classmethod
    def find_asset_pair(cls, quote, base):
        for ap in cls.get_asset_pairs():
            if ap.get('quote') == quote and ap.get('base') == base:
                return ap

    ##
    # Legacy function to make sure the hard-coded asset
    # configuration is consistent with the new format
    #
    @classmethod
    def normalise_assets(cls):
        asset_pairs = cls.asset_pairs

        for ap in asset_pairs:
            if not ap.get('base'):
                ap['base'] = ap.get('name').split(' ')[0]
            if not ap.get('quote'):
                ap['quote'] = ap.get('name').split(' ')[2]
            if not ap.get('volumecurrency'):
                ap['volumecurrency'] = ap.get('base')

        return asset_pairs

    ##
    # Loads asset pairs from the config files or,
    # failing that, from the hard-coded lines
    #
    @classmethod
    def get_asset_pairs(cls):
        try:
            with open('./coin/exchanges/data/' + cls.get_code() + '.conf', 'rb') as handle:
                asset_pairs = pickle.loads(handle.read())
                return asset_pairs

        except IOError:
            # no CONF file, return predefined from config
            return cls.normalise_assets()

    ##
    # Saves asset pairs to disk
    #
    @classmethod
    def store_asset_pairs(cls, asset_pairs):
        try:
            with open('./coin/exchanges/data/' + cls.get_code() + '.conf', 'wb') as handle:
                pickle.dump(asset_pairs, handle)
        except IOError:
            logging.error('Could not write to config file')

    ##
    # Discovers assets from the exchange's API url retrieved
    # through the instance-specific method _get_discovery_url()
    #
    @classmethod
    def discover_assets(cls, downloader, callback):
        command = DownloadCommand(cls._get_discovery_url(), callback)
        command.error = cls._handle_discovery_error
        downloader.execute(command, cls._handle_discovery_result)

    ##
    # Deals with the result from the discovery HTTP request
    # Should probably be merged with _handle_result() later
    #
    @classmethod
    def _handle_discovery_result(cls, command):
        data = command.response
        if data.status_code is not 200:
            cls._handle_discovery_error('API server returned an error: ' + str(data.status_code))

        try:
            result = data.json()
            asset_pairs = cls._parse_discovery(result)
            cls.normalise_assets()
            cls.store_asset_pairs(asset_pairs)
        except Exception as e:
            cls._handle_discovery_error(str(e))

        command.callback()  # update the asset menus of all instances

    @classmethod
    def _handle_discovery_error(cls, msg):
        logging.warning("Asset Discovery: " + msg)

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
        self.pair = self.asset_pair.get('pair')
        timestamp = time.time()
        command = DownloadCommand(self._get_ticker_url(), self.indicator.update_gui)
        command.timestamp = timestamp
        command.error = self._handle_error
        command.validation = self.asset_pair
        self.downloader.execute(command, self._handle_result)

        logging.info('Request with TS: ' + str(timestamp))
        if not self.error.is_ok():
            self.timeout_id = None

        return self.error.is_ok()  # continues the timer if there are no errors

    def _handle_error(self, error):
        self.error.log(str(error))
        self.error.increment()

    # def _handle_result(self, data, validation, timestamp):
    def _handle_result(self, command):
        data = command.response
        # Check to see if the returning response is still valid
        # (user may have changed exchanges before the request finished)
        if not self.started:
            logging.info("Discarding packet for inactive exchange")
            return

        if command.validation is not self.asset_pair:  # we've already moved on.
            logging.info("Discarding packet for wrong asset pair or exchange")
            return

        # also check if a newer response hasn't already been returned
        if command.timestamp < self.indicator.latest_response:  # this is an older request
            logging.info("Discarding outdated packet")
            return

        if data.status_code != 200:
            self._handle_error('API server returned an error: ' + str(data.status_code))
            return

        try:
            asset = data.json()
        except Exception:
            # Before, a KeyError happened when an asynchronous response comes in
            # for a previously selected asset pair (see upstream issue #27)
            self._handle_error('Invalid response for ' + str(self.pair))
            return

        results = self._parse_ticker(asset)
        self.indicator.latest_response = command.timestamp
        logging.info(
            'Response comes in with timestamp ' + str(command.timestamp) +
            ', last response at ' + str(self.indicator.latest_response))

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
        if number < 10:
            for i in range(8, 0, -1):
                if number < 10**-i:
                    break
        elif number >= 100:
            i = -2
        elif number >= 10:
            i = -1

        return ('{0:.' + str(i + 2) + 'f}').format(number)
