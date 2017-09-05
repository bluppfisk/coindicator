# -*- coding: utf-8 -*-
# Ubuntu App indicator
# https://unity.ubuntu.com/projects/appindicators/

import gi, logging, threading
logging.basicConfig(level=logging.INFO)

from gi.repository import Gtk, GdkPixbuf, GObject

try:
    from gi.repository import AppIndicator3 as AppIndicator
except ImportError:
    from gi.repository import AppIndicator

import utils

from exchange.kraken import Kraken
from exchange.bitstamp import Bitstamp
from exchange.bityep import BitYep
from exchange.gdax import Gdax
from settings import Settings
from exchange.kraken import CONFIG as KrakenConfig
from exchange.bityep import CONFIG as BitYepConfig
from exchange.gdax import CONFIG as GdaxConfig

REFRESH_TIMES = [  # seconds
    '3',
    '5',
    '10',
    '30',
    '60'
]

CURRENCY_SHOW = [
    'kraken',
    'bityep',
    'gdax'
]

CURRENCIES = {
    'kraken': KrakenConfig['asset_pairs'],
    'bityep': BitYepConfig['asset_pairs'],
    'gdax': GdaxConfig['asset_pairs']
}


class Indicator():
    instances = []

    def __init__(self, coin, counter, config, settings=None):
        Indicator.instances.append(self)
        self.counter = counter

        self.coin = coin

        self.config = config
        self.settings = Settings(settings)
        self.refresh_frequency = self.settings.refresh()
        self.active_exchange = self.settings.exchange()
        
        self.exchanges = [
            {
                'code': 'kraken',
                'name': 'Kraken',
                'instance': Kraken(self.config, self)
            },
            {
                'code': 'bitstamp',
                'name': 'Bitstamp',
                'instance': Bitstamp(self.config, self)
            },
            {
                'code': 'bityep',
                'name': 'BitYep',
                'instance': BitYep(self.config, self)
            },
            {
                'code': 'gdax',
                'name': 'Gdax',
                'instance': Gdax(self.config, self)
            }
        ]

    def start(self):
        icon = self.config['project_root'] + '/resources/icon_32px.png'
        self.indicator = AppIndicator.Indicator.new(self.config['app']['name'] + "_" + str(len(self.instances)), icon, AppIndicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.indicator.set_label('loading', 'loading')
        self.indicator.set_menu(self._menu())
        self._start_exchange()

    def set_data(self, label, bid, high, low, ask, volume=None):
        self.indicator.set_label(label, "$888.88")

        self.bid_item.get_child().set_text(bid)
        self.high_item.get_child().set_text(high)
        self.low_item.get_child().set_text(low)
        self.ask_item.get_child().set_text(ask)

        if volume:
            self.volume_item.get_child().set_text(volume)
            self.volume_item.show()
        else:
            self.volume_item.hide()

    def _start_exchange(self):
        ap = ''
        if self.active_exchange in CURRENCY_SHOW:
            self.active_asset_pair = self.settings.assetpair(self.active_exchange)
            ap = self.active_asset_pair

        home_currency = self.active_asset_pair.lower()[1:4]
        self.indicator.set_icon(self.config['project_root'] + '/resources/' + home_currency + '.png')
        logging.info("loading " + ap + " from " + self.active_exchange + " (" + str(self.refresh_frequency) + "s)")

        self._stop_exchanges()

        exchange = [e['instance'] for e in self.exchanges if self.active_exchange == e['code']]
        if len(exchange) == 1:
            exchange[0].check_price()
            exchange[0].start()
        else:
            logging.info("Error loading [" + self.active_exchange + "]")

    def _stop_exchanges(self):
        for exchange in self.exchanges:
            exchange['instance'].stop()

    def _menu(self):
        menu = Gtk.Menu()

        self.bid_item = Gtk.MenuItem(utils.category['bid'])
        self.high_item = Gtk.MenuItem(utils.category['high'])
        self.low_item = Gtk.MenuItem(utils.category['low'])
        self.ask_item = Gtk.MenuItem(utils.category['ask'])
        self.volume_item = Gtk.MenuItem(utils.category['volume'])

        remove_item = Gtk.MenuItem("Remove Ticker")
        remove_item.connect("activate", self._remove)

        refresh_item = Gtk.MenuItem("Refresh")
        refresh_item.set_submenu(self._menu_refresh())

        exchange_item = Gtk.MenuItem("Exchange")
        exchange_item.set_submenu(self._menu_exchange())

        menu.append(self.bid_item)
        menu.append(self.high_item)
        menu.append(self.low_item)
        menu.append(self.ask_item)
        menu.append(self.volume_item)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(refresh_item)
        menu.append(exchange_item)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(remove_item)

        menu.show_all()

        self._menu_currency_visible()

        return menu

    def _menu_refresh(self):
        refresh = Gtk.Menu()

        group = []
        for ri in REFRESH_TIMES:
            item = Gtk.RadioMenuItem.new_with_label(group, ri + 's')
            group.append(item)
            refresh.append(item)

            if self.refresh_frequency == int(ri):
                item.set_active(True)
            item.connect('activate', self._menu_refresh_change)

        return refresh

    def _menu_refresh_change(self, widget):
        if widget.get_active():
            self.refresh_frequency = int(widget.get_label()[:-1])
            self.settings.refresh(self.refresh_frequency)
            self._start_exchange()

    def _menu_exchange(self):
        exchange = Gtk.Menu()

        group = []
        for e in self.exchanges:
            item = Gtk.RadioMenuItem.new_with_label(group, e['name'])
            item.set_name(e['code'])
            group.append(item)
            exchange.append(item)

            if self.active_exchange == e['code']:
                item.set_active(True)

            item.connect('activate', self._menu_exchange_change)

        self._menu_currency(exchange)

        return exchange

    def _menu_exchange_change(self, widget):

        if widget.get_active():
            self.active_exchange = widget.get_name()

            for assetpair in CURRENCIES[self.active_exchange]:
                if assetpair['isocode'] == self.active_asset_pair:
                    active_asset_pair = self.active_asset_pair
                    break
                else:
                    active_asset_pair = CURRENCIES[self.active_exchange][0]['isocode']

            self.settings = Settings(self.active_exchange + ':' + active_asset_pair + ':' + str(self.refresh_frequency))

            self._menu_currency_visible()

            self._start_exchange()

    def _menu_currency(self, exchange_menu):
        self.currency_separator = Gtk.SeparatorMenuItem()
        self.currency_menu = Gtk.MenuItem("Currency")

        exchange_menu.append(self.currency_separator)
        exchange_menu.append(self.currency_menu)

        if self.active_exchange in CURRENCIES:
            self.currency_menu.set_submenu(self._menu_asset_pairs())

    def _menu_asset_pairs(self):
        asset_pairs = Gtk.Menu()

        self.active_asset_pair = self.settings.assetpair(self.active_exchange)

        group = []
        for asset in CURRENCIES[self.active_exchange]:
            item = Gtk.RadioMenuItem.new_with_label(group, asset['name'])
            item.set_name(asset['isocode'])
            group.append(item)
            asset_pairs.append(item)

            if self.active_asset_pair == asset['isocode']:
                item.set_active(True)

            item.connect('activate', self._menu_asset_pairs_change)

        return asset_pairs

    def _menu_asset_pairs_change(self, widget):
        if widget.get_active():
            self.active_asset_pair = widget.get_name()
            self.settings = Settings(self.active_exchange + ':' + self.active_asset_pair + ':' + str(self.refresh_frequency))

            self._start_exchange()

    def _menu_currency_visible(self):
        if self.active_exchange in CURRENCY_SHOW:
            self.currency_separator.show()
            self.currency_menu.set_submenu(self._menu_asset_pairs())
            self.currency_menu.show_all()
        else:
            self.currency_separator.hide()
            self.currency_menu.hide()

    def _remove(self, widget):
        if len(self.instances) == 1:
            Gtk.main_quit()
        else:
            self.instances.remove(self)
            self._stop_exchanges()
            del self.indicator
            logging.info("Indicator removed")