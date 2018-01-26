# -*- coding: utf-8 -*-
# Ubuntu App indicator
# https://unity.ubuntu.com/projects/appindicators/

import logging, os, sys, inspect, importlib, glob, exchanges
from os.path import dirname, basename, isfile
from settings import Settings
from alarm import Alarm, AlarmSettingsWindow
from gi.repository import Gtk
try:
    from gi.repository import AppIndicator3 as AppIndicator
except ImportError:
    from gi.repository import AppIndicator

logging.basicConfig(level=logging.ERROR)

REFRESH_TIMES = [  # seconds
    3,
    5,
    10,
    30,
    60
]

CATEGORIES = [
    ('cur', 'Now:\t\t'),
    ('bid', 'Bid:\t\t'),
    ('ask', 'Ask:\t\t'),
    ('high', 'High:\t\t'),
    ('low', 'Low:\t\t')
]

class Indicator(object):
    def __init__(self, coin, settings=None):
        self.coin = coin # reference to main object
        self.alarm = Alarm(self) # alarm

        self.prices = {}
        self.currency = ''
        self.volumecurrency = ''
        self.default_label = 'cur'
        self.latest_response = 0 # helps with discarding outdated responses
        
        self.settings = Settings(settings) # override pre-set values if settings is set

        # get the various settings for this indicator
        self.refresh_frequency = self.settings.get_refresh()
        self.active_exchange = self.settings.get_exchange()
        self.active_asset_pair = self.settings.get_asset_pair()

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
                'default_label': class_.CONFIG.get('default_label') or 'cur'
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

        if self.prices.get(self.default_label):
            label = self.currency + self.prices.get(self.default_label)
        else:
            label = 'select default label'

        self.indicator.set_label(label, label)
        
        for item, name in CATEGORIES:
            price_menu_item = self.price_menu_items.get(item) # get menu item

            # assigns prices to the corresponding menu items
            # if such a price value is returned from the exchange
            if self.prices.get(item):
                if item == self.default_label:
                    price_menu_item.set_active(True)
                    if self.alarm.active:
                        if self.alarm.check(float(self.prices.get(item))):
                            self.alarm.deactivate()

                price_menu_item.set_label(name + self.currency + self.prices.get(item))
                price_menu_item.show()
            # if no such price value is returned, hide the menu item
            else:
                price_menu_item.hide()

        # slightly different behaviour for volume menu item
        if self.prices.get('vol'):
            self.volume_item.set_label('Vol (' + self.volumecurrency + '):\t' + self.prices.get('vol'))
            self.volume_item.show()
        else:
            self.volume_item.hide()

    # (re)starts the exchange logic and its timer
    def _start_exchange(self):
        logging.info("Loading " + self.active_asset_pair + " from " + self.active_exchange + " (" + str(self.refresh_frequency) + "s)")
        
        # stop any running timers, clear error counter
        if hasattr(self, 'exchange_instance'):
            self.exchange_instance.stop()

        # don't show any data until first response is in
        self.indicator.set_label('loading', 'loading')
        for item in self.price_group:
            item.set_active(False)
            item.set_label('loading')

        self.volume_item.set_label('loading')
        home_currency = self.active_asset_pair.lower()[1:4]

        if isfile(self.coin.config.get('project_root') + '/resources/' + home_currency + '.png'):
            self.indicator.set_icon(self.coin.config.get('project_root') + '/resources/' + home_currency + '.png')
        else:
            self.indicator.set_icon(self.coin.config.get('project_root') + '/resources/unknown-coin.png')

        # load new exchange instance
        self.exchange_instance = [e.get('instance') for e in self.EXCHANGES if self.active_exchange == e.get('code')][0]
        self.default_label = [e.get('default_label') for e in self.EXCHANGES if self.active_exchange == e.get('code')][0] or 'bid'

        # start the timers and logic
        self.exchange_instance.start()

    # promotes a price value to the main label position
    def _make_label(self, widget, label):
        if widget.get_active():
            self.default_label = label
            if self.price_menu_items.get(self.default_label):
                new_label = self.prices.get(label)
                if new_label:
                    self.indicator.set_label(self.currency + new_label, new_label)

    def _menu(self):
        menu = Gtk.Menu()
        self.price_group = [] # so that a radio button can be set on the active one

        # hacky way to get every price item on the menu and filled
        self.price_menu_items = {}
        for price_type, name in CATEGORIES:
            self.price_menu_items[price_type] = Gtk.RadioMenuItem.new_with_label(self.price_group, 'loading...')
            self.price_menu_items[price_type].connect('toggled', self._make_label, price_type)
            self.price_group.append(self.price_menu_items.get(price_type))
            menu.append(self.price_menu_items.get(price_type))

        # trading volume display
        self.volume_item = Gtk.MenuItem('loading...')
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

        self.alarm_menu = Gtk.MenuItem("Set Alert" + u"\u2026")
        self.alarm_menu.connect("activate", self._alarm_settings)
        menu.append(self.alarm_menu)

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
            self.refresh_frequency = ri
            self.settings.set_refresh(self.refresh_frequency)
            self.exchange_instance.stop().start()

    def _menu_exchange(self):
        exchange_list_menu = Gtk.Menu()
        self.exchange_group = []
        subgroup = [] # group all asset pairs of all exchange menus together
        for exchange in self.EXCHANGES:
            item = Gtk.RadioMenuItem.new_with_label(self.exchange_group, exchange.get('name'))
            item.set_submenu(self._menu_asset_pairs(exchange, subgroup))
            item.connect('toggled', self._handle_toggle, exchange.get('code'))
            self.exchange_group.append(item)
            exchange_list_menu.append(item)

            if self.active_exchange == exchange.get('code'):
                item.set_active(True)

        return exchange_list_menu

    # this eliminates the strange side-effect that an item stays active
    # when you hover over it and then mouse out
    def _handle_toggle(self, widget, exchange_code):
        if self.active_exchange != exchange_code:
            widget.set_active(False)
        else:
            widget.set_active(True)

    def _menu_asset_pairs(self, exchange, subgroup):
        asset_pairs_menu = Gtk.Menu()
        for asset in self.CURRENCIES[exchange.get('code')]:
            item = Gtk.RadioMenuItem.new_with_label(subgroup, asset['name'])
            subgroup.append(item)
            asset_pairs_menu.append(item)

            if self.active_asset_pair == asset['isocode'] and self.active_exchange == exchange.get('code'):
                item.set_active(True)

            item.connect('activate', self._menu_asset_pairs_change, asset['isocode'], exchange)

        return asset_pairs_menu

    # if the asset pairs change
    def _menu_asset_pairs_change(self, widget, asset_pair, exchange):
        if widget.get_active():
            self.active_exchange = exchange.get('code')
            tentative_asset_pair = [item.get('isocode') for item in self.CURRENCIES[exchange.get('code')] if item.get('isocode') == self.active_asset_pair]
            if len(tentative_asset_pair) == 0:
                self.active_asset_pair = self.CURRENCIES[exchange.get('code')][0]['isocode']
            else:
                self.active_asset_pair = tentative_asset_pair[0]

            self.active_asset_pair = asset_pair
            self.settings.set_exchange(self.active_exchange)
            self.settings.set_asset_pair(self.active_asset_pair)

            # set parent (exchange) menu item to active
            for exchange_menu_item in self.exchange_group:
                if self.active_exchange == exchange_menu_item.get_label().lower():
                    exchange_menu_item.set_active(True)

            self._start_exchange()

    def _remove(self, widget):
        if len(self.coin.instances) == 1: # is this the last ticker?
            Gtk.main_quit() # then quit entirely
        else: # otherwise just remove this one
            self.coin.instances.remove(self)
            self.exchange_instance.stop()
            del self.indicator

    def _alarm_settings(self, widget):
        AlarmSettingsWindow(self)
