# -*- coding: utf-8 -*-
# Ubuntu App indicator
# https://unity.ubuntu.com/projects/appindicators/

import logging, os, sys, inspect, importlib, glob, exchanges
from os.path import dirname, basename, isfile
from settings import Settings
from exchanges import *
from gi.repository import Gtk, GdkPixbuf, GLib
try:
    from gi.repository import AppIndicator3 as AppIndicator
except ImportError:
    from gi.repository import AppIndicator

logging.basicConfig(level=logging.INFO)

REFRESH_TIMES = [  # seconds
    3,
    5,
    10,
    30,
    60
]

class Indicator(object):
    def __init__(self, coin, counter, config, settings=None):
        self.counter = counter
        self.coin = coin
        self.config = config
        self.settings = Settings(settings)
        self.refresh_frequency = self.settings.getRefresh()
        self.active_exchange = self.settings.getExchange()
        self.active_asset_pair = self.settings.getAssetpair()

        self.EXCHANGES = []
        self.CURRENCIES = {}

        for exchange in self.coin.exchanges:
            class_name = exchange.capitalize()
            class_ = getattr(__import__('exchanges.' + exchange, fromlist=[exchange]), class_name)

            self.EXCHANGES.append({
                'code': exchange,
                'name': class_name,
                'instance': class_(self)
            })
            self.CURRENCIES[exchange] = getattr(class_, 'CONFIG').get('asset_pairs')

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

        home_currency = self.active_asset_pair.lower()[1:4]
        self.indicator.set_icon(self.config.get('project_root') + '/resources/' + home_currency + '.png')

        if hasattr(self, 'exchangeInstance'):
            self.exchangeInstance.stop()

        self.exchangeInstance = [e.get('instance') for e in self.EXCHANGES if self.active_exchange == e.get('code')][0]
        self.exchangeInstance.check_price()
        self.exchangeInstance.start()

    def _stop_exchanges(self):
        for exchange in self.EXCHANGES:
            exchange.get('instance').stop()

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
            item = Gtk.RadioMenuItem.new_with_label(group, str(ri) + ' sec')
            group.append(item)
            refresh.append(item)

            if self.refresh_frequency == ri:
                item.set_active(True)
            item.connect('activate', self._menu_refresh_change, ri)

        return refresh

    def _menu_refresh_change(self, widget, ri):
        if widget.get_active():
            self.refresh_frequency = ri
            self.settings.setRefresh(self.refresh_frequency)
            self._start_exchange()

    def _menu_exchange(self):
        exchange_menu = Gtk.Menu()

        group = []
        for exchange in self.EXCHANGES:
            item = Gtk.RadioMenuItem.new_with_label(group, exchange.get('name'))
            group.append(item)
            exchange_menu.append(item)

            if self.active_exchange == exchange.get('code'):
                item.set_active(True)

            item.connect('activate', self._menu_exchange_change, exchange.get('code'))

        return exchange_menu

    def _menu_exchange_change(self, widget, exchange):
        if widget.get_active():
            self.active_exchange = exchange
            tentative_asset_pair = [item.get('isocode') for item in self.CURRENCIES[exchange] if item.get('isocode') == self.active_asset_pair]
            if len(tentative_asset_pair) == 0:
                self.active_asset_pair = self.CURRENCIES[exchange][0]['isocode']
            else:
                self.active_asset_pair = tentative_asset_pair[0]

            self.settings.setExchange(self.active_exchange)
            self.settings.setAssetpair(self.active_asset_pair)
            self._menu_currency_visible()
            self._start_exchange()

    def _menu_asset_pairs(self):
        asset_pairs = Gtk.Menu()

        group = []
        for asset in self.CURRENCIES[self.active_exchange]:
            item = Gtk.RadioMenuItem.new_with_label(group, asset['name'])
            group.append(item)
            asset_pairs.append(item)

            if self.active_asset_pair == asset['isocode']:
                item.set_active(True)

            item.connect('activate', self._menu_asset_pairs_change, asset['isocode'])

        return asset_pairs

    def _menu_asset_pairs_change(self, widget, assetpair):
        if widget.get_active():
            self.active_asset_pair = assetpair
            self.settings.setExchange(self.active_exchange)
            self.settings.setAssetpair(self.active_asset_pair)

            self._start_exchange()

    def _menu_currency_visible(self):
        self.currency_menu.set_submenu(self._menu_asset_pairs())
        self.currency_menu.show_all()

    def _remove(self, widget):
        if len(self.coin.instances) == 1:
            Gtk.main_quit()
        else:
            self.coin.instances.remove(self)
            self._stop_exchanges()
            del self.indicator