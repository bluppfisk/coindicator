# -*- coding: utf-8 -*-
# Ubuntu App indicator
# https://unity.ubuntu.com/projects/appindicators/

import logging, os, sys, inspect, importlib, glob, exchanges
from os.path import dirname, basename, isfile
from settings import Settings
from gi.repository import Gtk, GdkPixbuf
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

CATEGORIES = [
    ('current', 'Now:\t\t'),
    ('bid', 'Bid:\t\t'),
    ('ask', 'Ask:\t\t'),
    ('high', 'High:\t\t'),
    ('low', 'Low:\t\t')
]

class Indicator(object):
    def __init__(self, coin, settings=None):
        self.coin = coin # reference to main object

        self.default_label = 'bid'
        self.latest_response = 0 # helps with discarding outdated responses
        
        self.settings = Settings(settings) # override pre-set values if settings is set

        # get the various settings for this indicator
        self.refresh_frequency = self.settings.getRefresh()
        self.active_exchange = self.settings.getExchange()
        self.active_asset_pair = self.settings.getAssetpair()

        # load all the exchange modules and the classes contained within
        self.EXCHANGES = []
        self.CURRENCIES = {}

        for exchange in self.coin.exchanges:
            class_name = exchange.capitalize()
            class_ = getattr(importlib.import_module('exchanges.' + exchange), class_name)

            self.EXCHANGES.append({
                'code': exchange,
                'name': class_name,
                'instance': class_(self),
                'default_label': class_.CONFIG.get('default_label') or 'bid'
            })
            self.CURRENCIES[exchange] = class_.CONFIG.get('asset_pairs')

    # initialisation and start of indicator and exchanges
    def start(self):
        icon = self.coin.config['project_root'] + '/resources/icon_32px.png'
        self.indicator = AppIndicator.Indicator.new("CoinPriceIndicator_" + str(len(self.coin.instances)), icon, AppIndicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self._menu())
        self._start_exchange()

    # updates GUI menus with data stored in the object
    def update_gui(self):
        logging.debug('Updating GUI, last response was: ' + str(self.latest_response))
        if getattr(self, self.default_label):
            label = self.currency + getattr(self, self.default_label)
        else:
            label = 'no label selected'

        self.indicator.set_label(label, label)
        
        for item, name in CATEGORIES:
            price_menu_item = getattr(self, item + '_item')
            if getattr(self, item):
                if item == self.default_label:
                    price_menu_item.set_active(True)
                price_menu_item.set_label(name + self.currency + getattr(self, item))
                price_menu_item.show()
            else:
                price_menu_item.hide()

        if self.volume:
            self.volume_item.set_label('Vol (' + self.volumecurrency + '):\t' + self.volume)
            self.volume_item.show()
        else:
            self.volume_item.hide()

    # (re)starts the exchange logic and its timer
    def _start_exchange(self):
        logging.info("loading " + self.active_asset_pair + " from " + self.active_exchange + " (" + str(self.refresh_frequency) + "s)")
        
        # don't show any data until first response is in
        self.indicator.set_label('loading', 'loading')
        for item in self.price_group:
            item.set_active(False)
            item.set_label('loading')

        self.volume_item.set_label('loading')

        home_currency = self.active_asset_pair.lower()[1:4]
        self.indicator.set_icon(self.coin.config.get('project_root') + '/resources/' + home_currency + '.png')

        # stop any running timers, clear error counter
        if hasattr(self, 'exchange_instance'):
            self.exchange_instance.stop()

        # load new exchange instance
        self.exchange_instance = [e.get('instance') for e in self.EXCHANGES if self.active_exchange == e.get('code')][0]
        self.default_label = [e.get('default_label') for e in self.EXCHANGES if self.active_exchange == e.get('code')][0] or 'bid'

        # start the timers and logic
        self.exchange_instance.start()

    # promotes a price value to the main label position
    def _make_label(self, widget, label):
        if widget.get_active():
            self.default_label = label
            if hasattr(self, label):
                new_label = getattr(self, label)
                if new_label:
                    self.indicator.set_label(self.currency + new_label, new_label)

    def _menu(self):
        menu = Gtk.Menu()
        self.price_group = [] # so that a radio button can be set on the active one

        # hacky way to get every price item on the menu and filled
        for price_type, name in CATEGORIES:
            price_item = price_type + '_item'
            setattr(self, price_item, Gtk.RadioMenuItem.new_with_label(self.price_group, 'loading...'))
            getattr(self, price_item).connect('activate', self._make_label, price_type)
            self.price_group.append(getattr(self, price_item))
            menu.append(getattr(self, price_item))

        # trading volume display
        self.volume_item = Gtk.MenuItem('loading')
        menu.append(self.volume_item)

        menu.append(Gtk.SeparatorMenuItem())

        # exchange choice menu
        self.exchange_menu = Gtk.MenuItem("Exchange")
        self.exchange_menu.set_submenu(self._menu_exchange())
        menu.append(self.exchange_menu)

        # refresh rate choice menu
        self.refresh_menu = Gtk.MenuItem("Refresh")
        self.refresh_menu.set_submenu(self._menu_refresh())
        menu.append(self.refresh_menu)

        menu.append(Gtk.SeparatorMenuItem())

        # menu to remove current indicator from app
        remove_item = Gtk.MenuItem("Remove Ticker")
        remove_item.connect("activate", self._remove)
        menu.append(remove_item)

        menu.show_all()

        return menu

    def _menu_refresh(self):
        refresh_menu = Gtk.Menu()

        group = []
        for ri in REFRESH_TIMES:
            item = Gtk.RadioMenuItem.new_with_label(group, str(ri) + ' sec')
            group.append(item)
            refresh_menu.append(item)

            if self.refresh_frequency == ri:
                item.set_active(True)
            item.connect('activate', self._menu_refresh_change, ri)

        return refresh_menu

    def _menu_refresh_change(self, widget, ri):
        if widget.get_active():
            print(str(ri))
            self.refresh_frequency = ri
            self.settings.setRefresh(self.refresh_frequency)
            self.exchange_instance.stop().start()

    def _menu_exchange(self):
        exchange_menu = Gtk.Menu()
        group = []
        subgroup = [] # group all asset pairs of all exchange menus together
        for exchange in self.EXCHANGES:
            item = Gtk.RadioMenuItem.new_with_label(group, exchange.get('name'))
            item.set_submenu(self._menu_asset_pairs(exchange, subgroup))
            group.append(item)
            exchange_menu.append(item)

            if self.active_exchange == exchange.get('code'):
                item.set_active(True)

        return exchange_menu

    def _menu_asset_pairs(self, exchange, subgroup):
        asset_pairs_menu = Gtk.Menu()
        for asset in self.CURRENCIES[exchange.get('code')]:
            item = Gtk.RadioMenuItem.new_with_label(subgroup, asset['name'])
            subgroup.append(item)
            asset_pairs_menu.append(item)

            if self.active_asset_pair == asset['isocode'] and self.active_exchange == exchange.get('code'):
                item.set_active(True)
                item.get_parent().set_active(True)

            item.connect('activate', self._menu_asset_pairs_change, asset['isocode'], exchange)

        return asset_pairs_menu

    # if the asset pairs change
    def _menu_asset_pairs_change(self, widget, assetpair, exchange):
        if widget.get_active():
            self.active_exchange = exchange.get('code')
            tentative_asset_pair = [item.get('isocode') for item in self.CURRENCIES[exchange.get('code')] if item.get('isocode') == self.active_asset_pair]
            if len(tentative_asset_pair) == 0:
                self.active_asset_pair = self.CURRENCIES[exchange.get('code')][0]['isocode']
            else:
                self.active_asset_pair = tentative_asset_pair[0]

            self.active_asset_pair = assetpair
            self.default_label = exchange.get('default_label')
            self.settings.setExchange(self.active_exchange)
            self.settings.setAssetpair(self.active_asset_pair)

            self._start_exchange()

    def _remove(self, widget):
        if len(self.coin.instances) == 1: # is this the last ticker?
            Gtk.main_quit() # then quit entirely
        else: # otherwise just remove this one
            self.coin.instances.remove(self)
            self.exchange_instance.stop()
            del self.indicator