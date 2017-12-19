# -*- coding: utf-8 -*-
# Ubuntu App indicator
# https://unity.ubuntu.com/projects/appindicators/

import logging
logging.basicConfig(level=logging.INFO)

from gi.repository import Gtk, GdkPixbuf, GLib, Gdk
try:
    from gi.repository import AppIndicator3 as AppIndicator
except ImportError:
    from gi.repository import AppIndicator

from settings import Settings
import os, sys
import glob, importlib

from exchanges.kraken import Kraken
from exchanges.bitstamp import Bitstamp
from exchanges.bitfinex import Bitfinex
from exchanges.gdax import Gdax
from exchanges.gemini import Gemini
from exchanges.bittrex import Bittrex

VALUE_DOWN = Gdk.RGBA()
VALUE_DOWN.red = 255
VALUE_DOWN.alpha = 255

REFRESH_TIMES = [  # seconds
    '3',
    '5',
    '10',
    '30',
    '60'
]

CURRENCY_SHOW = [
    'kraken',
    'gdax',
    'gemini',
    'bitstamp',
    'bittrex',
    'bitfinex'
]

CURRENCIES = {
    'kraken': Kraken.CONFIG['asset_pairs'],
    'gdax': Gdax.CONFIG['asset_pairs'],
    'gemini': Gemini.CONFIG['asset_pairs'],
    'bitstamp': Bitstamp.CONFIG['asset_pairs'],
    'bittrex': Bittrex.CONFIG['asset_pairs'],
    'bitfinex': Bitfinex.CONFIG['asset_pairs'],
}


class Indicator():
    def __init__(self, coin, counter, config, settings=None):
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
                'instance': Kraken(self)
            },
            {
                'code': 'bitstamp',
                'name': 'Bitstamp',
                'instance': Bitstamp(self)
            },
            {
                'code': 'bitfinex',
                'name': 'Bitfinex',
                'instance': Bitfinex(self)
            },
            {
                'code': 'gdax',
                'name': 'Gdax',
                'instance': Gdax(self)
            },
            {
                'code': 'gemini',
                'name': 'Gemini',
                'instance': Gemini(self)
            },
            {
                'code': 'bittrex',
                'name': 'Bittrex',
                'instance': Bittrex(self)
            }
        ]

    def start(self):
        icon = self.config['project_root'] + '/resources/icon_32px.png'
        self.indicator = AppIndicator.Indicator.new(self.config['app']['name'] + "_" + str(len(self.coin.instances)), icon, AppIndicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self._menu())
        self._start_exchange()

    def set_data(self, label, bid, high, low, ask, volume=None):
        self.indicator.set_label(label, "$888.88")

        if bid:
            self.bid_item.set_label(bid)
            self.bid_item.show()
        else:
            self.bid_item.hide()

        if high:
            self.high_item.set_label(high)
            self.high_item.show()
        else:
            self.high_item.hide()

        if low:
            self.low_item.set_label(low)
            self.low_item.show()
        else:
            self.low_item.hide()

        if ask:
            self.ask_item.set_label(ask)
            self.ask_item.show()
        else:
            self.ask_item.hide()

        if volume:
            self.volume_item.set_label(volume)
            self.volume_item.show()
        else:
            self.volume_item.hide()

    def _start_exchange(self):
        self.indicator.set_label('loading', 'loading')
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

        self.bid_item = Gtk.MenuItem('loading...')
        self.high_item = Gtk.MenuItem('loading...')
        self.low_item = Gtk.MenuItem('loading...')
        self.ask_item = Gtk.MenuItem('loading...')
        self.volume_item = Gtk.MenuItem('loading...')

        remove_item = Gtk.MenuItem("Remove Ticker")
        remove_item.connect("activate", self._remove)

        self.refresh_menu = Gtk.MenuItem("Refresh")
        self.refresh_menu.set_submenu(self._menu_refresh())

        self.exchange_menu = Gtk.MenuItem("Exchange")
        self.exchange_menu.set_submenu(self._menu_exchange())

        self.currency_menu = Gtk.MenuItem("Currency")
        self.currency_menu.set_submenu(self._menu_asset_pairs())

        menu.append(self.bid_item)
        menu.append(self.high_item)
        menu.append(self.low_item)
        menu.append(self.ask_item)
        menu.append(self.volume_item)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(self.exchange_menu)
        menu.append(self.currency_menu)
        menu.append(self.refresh_menu)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(remove_item)

        menu.show_all()

        self._menu_currency_visible()

        return menu

    def _menu_refresh(self):
        refresh = Gtk.Menu()

        group = []
        for ri in REFRESH_TIMES:
            item = Gtk.RadioMenuItem.new_with_label(group, ri + ' sec')
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
            self.currency_menu.set_submenu(self._menu_asset_pairs())
            self.currency_menu.show_all()
        else:
            self.currency_menu.hide()

    def _remove(self, widget):
        if len(self.coin.instances) == 1:
            Gtk.main_quit()
        else:
            self.coin.instances.remove(self)
            self._stop_exchanges()
            del self.indicator