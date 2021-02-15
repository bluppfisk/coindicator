#!/usr/bin/env python3
# Coin Price Indicator
#
# Nil Gradisnik <nil.gradisnik@gmail.com>
# Sander Van de Moortel <sander.vandemoortel@gmail.com>
#


import signal
import yaml
import logging
import glob
import dbus
import importlib
import notify2
import gi
import os
import shutil
from indicator import Indicator
from about import AboutWindow
from plugin_selection import PluginSelectionWindow
from requests import get
from downloader import DownloadCommand, DownloadService, AsyncDownloadService

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"


from os.path import abspath, dirname, isfile, basename
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import Gtk

try:
    from gi.repository import AppIndicator3 as AppIndicator
except ImportError:
    from gi.repository import AppIndicator

PROJECT_ROOT = abspath(dirname(dirname(__file__)))
SETTINGS_FILE = PROJECT_ROOT + '/user.conf'
if isfile("./LOGLEVEL"):
    with open("LOGLEVEL", "r") as f: logging.basicConfig(level=int(f.read()))


class Coin():
    config = yaml.load(open(PROJECT_ROOT + '/config.yaml', 'r'), Loader=yaml.SafeLoader)
    config['project_root'] = PROJECT_ROOT

    def __init__(self):
        self.downloader = AsyncDownloadService()
        self.unique_id = 0
        self.assets = {}
        self.coingecko_list = []

        self._load_coingecko_list()
        self._load_exchanges()
        self._load_assets()
        self._load_settings()
        self._start_main()

        self.instances = []
        self.discoveries = 0
        self._add_many_indicators(self.settings.get('tickers'))
        self._start_gui()

    # Load exchange 'plug-ins' from exchanges dir
    def _load_exchanges(self):
        dirfiles = glob.glob(dirname(__file__) + "/exchanges/*.py")
        plugins = [basename(f)[:-3] for f in dirfiles if isfile(f) and not f.endswith('__init__.py')]
        plugins.sort()

        self.EXCHANGES = []
        for plugin in plugins:
            class_name = plugin.capitalize()
            class_ = getattr(importlib.import_module('exchanges.' + plugin), class_name)
            self.EXCHANGES.append(class_)

    # Find an exchange
    def find_exchange_by_code(self, code):
        for exchange in self.EXCHANGES:
            if exchange.get_code() == code.lower():
                return exchange

    def _load_coingecko_list(self):
        command = DownloadCommand('https://api.coingecko.com/api/v3/coins/list', lambda *args: None)
        DownloadService().execute(command, self.handle_coingecko_data)

    def handle_coingecko_data(self, command):
        data = command.response       
        if data.status_code == 200:
            self.coingecko_list = data.json()
        else:
            logging.warn("CoinGecko API: " + data.status_code + " " + command.error)

    # Fetch icon from CoinGecko
    def coingecko_coin_api(self, icons_root, asset):
        img_file = icons_root + asset + '.png'
        for coin in self.coingecko_list:
            if asset == coin.get('symbol'):
                command = DownloadCommand('https://api.coingecko.com/api/v3/coins/' + coin.get('id')
                    , {'icons_root': icons_root, 'symbol': asset })
                DownloadService().execute(command, self.handle_coingecko_icon)
                if os.path.isfile(img_file):
                    return img_file
        return None

    def handle_coingecko_icon(self, command):
        icons_root = command.callback['icons_root']
        symbol = command.callback['symbol']
        img_file = icons_root + symbol + '.png'

        data = command.response
        img_url = data.json().get('image').get('small')
        img = get(img_url, stream = True)

        if img.status_code == 200:

            with open(img_file, "wb") as f:
                img.raw.decode_content = True
                shutil.copyfileobj(img.raw, f)
        else:
            logging.error('Could not write icon file')
    # Creates a structure of available assets (from_currency > to_currency > exchange)
    def _load_assets(self):
        self.assets = {}

        for exchange in self.EXCHANGES:
            if exchange.active:
                if not exchange.get_asset_pairs():
                    exchange.discover_assets(DownloadService(), lambda *args: None)
                self.assets[exchange.get_code()] = exchange.get_asset_pairs()

        # inverse the hierarchy for easier asset selection
        bases = {}
        for exchange in self.assets.keys():
            asset_pair = self.assets.get(exchange)
            for asset_pair in self.assets.get(exchange):
                base = asset_pair.get('base')
                quote = asset_pair.get('quote')

                if base not in bases:
                    bases[base] = {}

                if quote not in bases[base]:
                    bases[base][quote] = []

                bases[base][quote].append(self.find_exchange_by_code(exchange))

        self.bases = bases

    # load instances
    def _load_settings(self):
        self.settings = {}
        # load from file
        if isfile(SETTINGS_FILE):
            self.settings = yaml.load(open(SETTINGS_FILE, 'r'), Loader=yaml.SafeLoader)

        for plugin in self.settings.get('plugins', {}):
            for code, active in plugin.items():
                e = self.find_exchange_by_code(code)
                if e: e.active = active

        # set defaults if settings not defined
        if not self.settings.get('tickers'):
            # TODO work without defining a default
            self.settings['tickers'] = [{
                'exchange': self.EXCHANGES[0].get_code(),
                'asset_pair': self.assets[self.EXCHANGES[0].get_code()][0].get('pair'),
                'refresh': 3,
                'default_label': self.EXCHANGES[0].get_default_label()
            }]

        if not self.settings.get('recent'):
            self.settings['recent'] = []

    # saves settings for each ticker
    def save_settings(self):
        tickers = []
        for instance in self.instances:
            ticker = {
                'exchange': instance.exchange.get_code(),
                'asset_pair': instance.exchange.asset_pair.get('pair'),
                'refresh': instance.refresh_frequency,
                'default_label': instance.default_label
            }
            tickers.append(ticker)
            self.settings['tickers'] = tickers

        plugins = []
        for exchange in self.EXCHANGES:
            plugin = {exchange.get_code(): exchange.active}
            plugins.append(plugin)

        self.settings['plugins'] = plugins

        try:
            with open(SETTINGS_FILE, 'w') as handle:
                yaml.dump(self.settings, handle, default_flow_style=False)
        except IOError:
            logging.error('Settings file not writable')

    # Add a new base to the recents settings, and push the last one off the edge
    def add_new_recent(self, asset_pair, exchange_code):
        for recent in self.settings['recent']:
            if recent.get('asset_pair') == asset_pair and recent.get('exchange') == exchange_code:
                self.settings['recent'].remove(recent)

        self.settings['recent'] = self.settings['recent'][0:4]

        new_recent = {
            'asset_pair': asset_pair,
            'exchange': exchange_code
        }

        self.settings['recent'].insert(0, new_recent)

        for instance in self.instances:
            instance.rebuild_recents_menu()

    # Start the main indicator icon and its menu
    def _start_main(self):
        print("{} v{} running!".format(
            self.config.get('app').get('name'),
            self.config.get('app').get('version')))

        self.icon = "{}/resources/icon_32px.png".format(
            self.config.get('project_root'))
        self.main_item = AppIndicator.Indicator.new(
            self.config.get('app').get('name'),
            self.icon,
            AppIndicator.IndicatorCategory.APPLICATION_STATUS)
        self.main_item.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.main_item.set_ordering_index(0)
        self.main_item.set_menu(self._menu())

    def _start_gui(self):
        signal.signal(signal.SIGINT, Gtk.main_quit)  # ctrl+c exit
        DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
        bus.add_signal_receiver(
            self.handle_resume,
            None,
            'org.freedesktop.login1.Manager',
            'org.freedesktop.login1'
        )
        Gtk.main()

    # Program main menu
    def _menu(self):
        menu = Gtk.Menu()

        self.add_item = Gtk.MenuItem.new_with_label("Add Ticker")
        self.discover_item = Gtk.MenuItem.new_with_label("Discover Assets")
        self.plugin_item = Gtk.MenuItem.new_with_label("Plugins" + u"\u2026")
        self.about_item = Gtk.MenuItem.new_with_label("About")
        self.quit_item = Gtk.MenuItem.new_with_label("Quit")

        self.add_item.connect("activate", self._add_ticker)
        self.discover_item.connect("activate", self._discover_assets)
        self.plugin_item.connect("activate", self._select_plugins)
        self.about_item.connect("activate", self._about)
        self.quit_item.connect("activate", self._quit_all)

        menu.append(self.add_item)
        menu.append(self.discover_item)
        menu.append(self.plugin_item)
        menu.append(self.about_item)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(self.quit_item)
        menu.show_all()

        return menu

    # Adds a ticker and starts it
    def _add_indicator(self, settings):
        exchange = settings.get('exchange')
        refresh = settings.get('refresh')
        asset_pair = settings.get('asset_pair')
        default_label = settings.get('default_label')
        self.unique_id += 1
        indicator = Indicator(
            self,
            self.unique_id,
            exchange,
            asset_pair,
            refresh,
            default_label)
        self.instances.append(indicator)
        indicator.start()
        return indicator

    # adds many tickers
    def _add_many_indicators(self, tickers):
        for ticker in tickers:
            self._add_indicator(ticker)

    # Menu item to add a ticker
    def _add_ticker(self, widget):
        i = self._add_indicator(self.settings.get('tickers')[len(self.settings.get('tickers')) - 1])
        i._settings(widget)
        self.save_settings()

    # Remove ticker
    def remove_ticker(self, indicator):
        if len(self.instances) == 1:  # is it the last ticker?
            Gtk.main_quit()  # then quit entirely
        else:  # otherwise just remove this one
            indicator.exchange.stop()
            indicator.indicator_widget.set_status(AppIndicator.IndicatorStatus.PASSIVE)
            self.instances.remove(indicator)
            self.save_settings()

    # Menu item to download any new assets from the exchanges
    def _discover_assets(self, widget):
        # Don't do anything if there are no active exchanges with discovery
        if len([ex for ex in self.EXCHANGES if ex.active and ex.discovery]) == 0:
            return

        self.main_item.set_icon_full(self.config.get('project_root') + '/resources/loading.png', 'Discovering assets')

        for indicator in self.instances:
            if indicator.asset_selection_window:
                indicator.asset_selection_window.destroy()

        for exchange in self.EXCHANGES:
            if exchange.active and exchange.discovery:
                exchange.discover_assets(self.downloader, self.update_assets)

    # When discovery completes, reload currencies and rebuild menus of all instances
    def update_assets(self):
        self.discoveries += 1
        if self.discoveries < len([ex for ex in self.EXCHANGES if ex.active and ex.discovery]):
            return  # wait until all active exchanges with discovery finish discovery

        self.discoveries = 0
        self._load_assets()

        if notify2.init(self.config.get('app').get('name')):
            n = notify2.Notification(
                self.config.get('app').get('name'),
                "Finished discovering new assets",
                self.icon)
            n.set_urgency(1)
            n.timeout = 2000
            n.show()

        self.main_item.set_icon_full(self.icon, "App icon")

    # Handle system resume by refreshing all tickers
    def handle_resume(self, sleeping, *args):
        if not sleeping:
            for instance in self.instances:
                instance.exchange.stop().start()

    def _select_plugins(self, widget):
        PluginSelectionWindow(self)

    # Menu item to remove all tickers and quits the application
    def _quit_all(self, widget):
        Gtk.main_quit()

    def plugins_updated(self):
        self._load_assets()
        for instance in self.instances:
            instance.start()  # will stop exchange if inactive

        self.save_settings()

    def _about(self, widget):
        AboutWindow(self.config).show()


coin = Coin()
