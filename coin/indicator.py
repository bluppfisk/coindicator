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

REFRESH_TIMES = [ # seconds
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
        #self.currency = ''
        #self.volumecurrency = ''
        
        self.latest_response = 0 # helps with discarding outdated responses
        
        self.settings = Settings(settings) # override pre-set values if settings is set

        # get the various settings for this indicator
        self.refresh_frequency = self.settings.get_refresh()
        exchange_class = self.coin.find_exchange_by_code(self.settings.get_exchange()).get('class')
        self.exchange = exchange_class(self)
        self.exchange.set_asset_pair_from_isocode(self.settings.get_asset_pair())
        self.default_label = self.exchange.get_default_label()

    # initialisation and start of indicator and exchanges
    def start(self):
        icon = self.coin.config['project_root'] + '/resources/icon_32px.png'
        self.indicator_widget = AppIndicator.Indicator.new("CoinPriceIndicator_" + str(len(self.coin.instances)), icon, AppIndicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator_widget.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.indicator_widget.set_menu(self._menu())
        self._start_exchange()

    # updates GUI menus with data stored in the object
    def update_gui(self):
        logging.debug('Updating GUI, last response was: ' + str(self.latest_response))

        self.currency = self.exchange.get_currency()
        self.volumecurrency = self.exchange.get_volume_currency()

        if self.prices.get(self.default_label):
            label = self.currency + self.prices.get(self.default_label)
        else:
            label = 'select default label'

        self.indicator_widget.set_label(label, label)
        
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
        logging.info("Loading " + self.exchange.asset_pair.get('isocode') + " from " + self.exchange.get_name() + " (" + str(self.refresh_frequency) + "s)")

        # don't show any data until first response is in
        self.indicator_widget.set_label('loading', 'loading')
        for item in self.price_group:
            item.set_active(False)
            item.set_label('loading')

        self.volume_item.set_label('loading')

        # set icon for asset if it exists
        asset_name = self.exchange.asset_pair.get('currency')

        if isfile(self.coin.config.get('project_root') + '/resources/' + asset_name + '.png'):
            self.indicator_widget.set_icon(self.coin.config.get('project_root') + '/resources/' + asset_name + '.png')
        else:
            self.indicator_widget.set_icon(self.coin.config.get('project_root') + '/resources/unknown-coin.png')

        # load new exchange instance
        self.default_label = self.exchange.get_default_label()

        # start the timers and logic
        self.exchange.start()

    # promotes a price value to the main label position
    def _make_label(self, widget, label):
        if widget.get_active():
            self.default_label = label
            if self.price_menu_items.get(self.default_label):
                new_label = self.prices.get(label)
                if new_label:
                    self.indicator_widget.set_label(self.currency + new_label, new_label)

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

        # asset choice menu
        self.asset_menu = Gtk.MenuItem("Assets")
        self.asset_menu.set_submenu(self._menu_assets())
        menu.append(self.asset_menu)

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

    ##
    # Gets called by exchange instance when new asset pairs are discovered
    # 
    def rebuild_asset_menu(self):
        self.exchange_menu.set_submenu(self._menu_exchange())
        self.exchange_menu.show_all()

        self.asset_menu.set_submenu(self._menu_assets())
        self.asset_menu.show_all()

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

    def _menu_assets(self):
        base_list_menu = Gtk.Menu()
        self.base_group = []
        subgroup = []

        # sorting magic
        bases = []
        for base in self.coin.bases:
            bases.append(base)
        bases.sort()

        for base in bases:
            base_item = Gtk.RadioMenuItem.new_with_label(self.base_group, base)
            base_item.set_submenu(self._menu_assets_quotes(base, subgroup))
            base_item.connect('toggled', self._handle_toggle, base)
            self.base_group.append(base_item)
            base_list_menu.append(base_item)

            if self.exchange.asset_pair.get('base') == base:
                base_item.set_active(True)

        return base_list_menu

    def _menu_assets_quotes(self, base, subgroup):
        quote_list_menu = Gtk.Menu()
        self.quote_group = []

        # sorting magic
        quotes = []
        for quote in self.coin.bases[base]:
            quotes.append(quote)
        quotes.sort()

        for quote in quotes:
            quote_item = Gtk.RadioMenuItem.new_with_label(subgroup, quote)
            quote_item.set_submenu(self._menu_assets_quotes_exchanges(base, quote, subgroup))
            quote_item.connect('toggled', self._handle_toggle, base, quote)
            self.quote_group.append(quote_item)
            subgroup.append(quote_item)
            quote_list_menu.append(quote_item)

            if self.exchange.asset_pair.get('quote') == quote:
                quote_item.set_active(True)

        return quote_list_menu

    def _menu_assets_quotes_exchanges(self, base, quote, subgroup):
        exchange_list_menu = Gtk.Menu()
        self.exchange_group = []

        # some sorting magic
        exchanges = []
        for exchange in self.coin.bases[base][quote]:
            exchanges.append(exchange)        
        exchanges = sorted(exchanges, key=lambda k: k['name'])

        for exchange in exchanges:
            exchange_item = Gtk.RadioMenuItem.new_with_label(subgroup, exchange.get('name'))
            #exchange_item.connect('activate', self._menu_asset_pairs_change, base, quote, exchange.get('code'))
            exchange_item.connect('toggled', self._handle_toggle, base, quote, exchange.get('code'))
            exchange_item.connect('activate', self._menu_asset_pairs_change, base, quote, exchange.get('code'))
            self.exchange_group.append(exchange_item)
            subgroup.append(exchange_item)
            exchange_list_menu.append(exchange_item)

            if (self.exchange.asset_pair.get('base') == base) and (self.exchange.asset_pair.get('quote') == quote) and (self.exchange.get_code() == exchange):
                exchange_item.set_active(True)

        return exchange_list_menu

    # this eliminates the strange side-effect that an item stays active
    # when you hover over it and then mouse out
    def _handle_toggle(self, widget, base=None, quote=None, exchange=None):
        if base == None:
            base = self.exchange.asset_pair.get('base')
        if quote == None:
            quote = self.exchange.asset_pair.get('quote')
        if exchange == None:
            exchange = self.exchange.get_code()
        if (self.exchange.get_code() == exchange) and (self.exchange.asset_pair.get('quote') == quote) and (self.exchange.asset_pair.get('base') == base):
            widget.set_active(True)
        else:
            widget.set_active(False)

    # if the asset pairs change
    def _menu_asset_pairs_change(self, widget, base, quote, exchange):
        if widget.get_active():
            self.exchange.stop()

            exchange_class = self.coin.find_exchange_by_code(exchange).get('class')
            self.exchange = exchange_class(self)
            self.exchange.set_asset_pair(base, quote)
            self.settings.update_from_indicator(self)

            self._set_active_toggles()
            self._start_exchange()

    def _set_active_toggles(self):
        # set parent (exchange) menu item to active
        print('hi')
        for exchange_menu_item in self.exchange_group:
            print(self.exchange.get_code() + ' ' + exchange_menu_item.get_label().lower())
            if self.exchange.get_code() == exchange_menu_item.get_label().lower():
                exchange_menu_item.set_active(True)

        for base_menu_item in self.base_group:
            if self.exchange.asset_pair.get('base').lower() == base_menu_item.get_label().lower():
                base_menu_item.set_active(True)

        for quote_menu_item in self.quote_group:
            if self.exchange.asset_pair.get('quote').lower() == quote_menu_item.get_label().lower():
                quote_menu_item.set_active(True)

    def _remove(self, widget):
        if len(self.coin.instances) == 1: # is this the last ticker?
            Gtk.main_quit() # then quit entirely
        else: # otherwise just remove this one
            self.coin.instances.remove(self)
            self.exchange.stop()
            del self.indicator_widget

    def _alarm_settings(self, widget):
        AlarmSettingsWindow(self)
