# -*- coding: utf-8 -*-

# Ubuntu App indicator
# https://unity.ubuntu.com/projects/appindicators/

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk, GdkPixbuf

try:
    from gi.repository import AppIndicator3 as AppIndicator
except ImportError:
    from gi.repository import AppIndicator

import utils
import threading

from settings import Settings
from exchange.kraken import CONFIG as KrakenConfig

__author__ = "nil.gradisnik@gmail.com"

REFRESH_TIMES = [  # seconds
    '3',
    '5',
    '10',
    '30',
    '60'
]

CURRENCY_SHOW = [
    'kraken'
]

CURRENCIES = {
    'kraken': KrakenConfig['asset_pairs']
}


class Indicator(threading.Thread):
    def __init__(self, counter, config, settings=None):
        threading.Thread.__init__(self)
        # self.threadID = threadID
        # self.name = name
        self.counter = counter

        self.config = config
        self.settings = Settings(settings)
        self.refresh_frequency = self.settings.refresh()
        self.active_exchange = self.settings.exchange()

        icon = self.config['project_root'] + '/resources/icon_32px.png'
        self.indicator = AppIndicator.Indicator.new(self.config['app']['name'] + "_" + str(counter), icon,
                                                    AppIndicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.indicator.set_label("syncing", "$888.88")

        self.logo_124px = GdkPixbuf.Pixbuf.new_from_file(self.config['project_root'] + '/resources/icon_32px.png')
        # self.logo_124px.saturate_and_pixelate(self.logo_124px, 1, True)

        self.exchanges = None

    def set_exchanges(self, exchanges):
        self.exchanges = exchanges

    def run(self):
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
            ap = "Asset pair: " + self.active_asset_pair

        print("Using [" + self.active_exchange + "] exchange. (" + str(self.refresh_frequency) + "s refresh) " + ap)

        self._stop_exchanges()

        exchange = [e['instance'] for e in self.exchanges if self.active_exchange == e['code']]
        if len(exchange) == 1:
            exchange[0].check_price()
            exchange[0].start()
        else:
            print("Error starting instance [" + self.active_exchange + "]")

    def _stop_exchanges(self):
        for exchange in self.exchanges:
            exchange['instance'].stop()

    # UI stuff
    def _menu(self):
        menu = Gtk.Menu()

        self.bid_item = Gtk.MenuItem(utils.category['bid'])
        self.high_item = Gtk.MenuItem(utils.category['high'])
        self.low_item = Gtk.MenuItem(utils.category['low'])
        self.ask_item = Gtk.MenuItem(utils.category['ask'])
        self.volume_item = Gtk.MenuItem(utils.category['volume'])

        about_item = Gtk.MenuItem("About")
        about_item.connect("activate", self._about)

        quit_item = Gtk.MenuItem("Quit")
        quit_item.connect("activate", self._quit)

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
        menu.append(about_item)
        menu.append(quit_item)

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
            self.settings.exchange(self.active_exchange)

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
            item.set_name(asset['code'])
            group.append(item)
            asset_pairs.append(item)

            if self.active_asset_pair == asset['code']:
                item.set_active(True)

            item.connect('activate', self._menu_asset_pairs_change)

        return asset_pairs

    def _menu_asset_pairs_change(self, widget):
        if widget.get_active():
            self.active_asset_pair = widget.get_name()
            self.settings.assetpair(self.active_exchange, self.active_asset_pair)

            self._start_exchange()

    def _menu_currency_visible(self):
        if self.active_exchange in CURRENCY_SHOW:
            self.currency_separator.show()
            self.currency_menu.set_submenu(self._menu_asset_pairs())
            self.currency_menu.show_all()
        else:
            self.currency_separator.hide()
            self.currency_menu.hide()

    def _about(self, widget):
        about = Gtk.AboutDialog()
        about.set_program_name(self.config['app']['name'])
        about.set_comments(self.config['app']['description'])
        about.set_copyright(self.config['author']['copyright'])
        about.set_version(self.config['app']['version'])
        about.set_website(self.config['app']['url'])
        about.set_authors([self.config['author']['name'] + ' <' + self.config['author']['email'] + '>'])
        about.set_artists([self.config['artist']['name'] + ' <' + self.config['artist']['email'] + '>'])
        about.set_license_type(Gtk.License.MIT_X11)
        about.set_logo(self.logo_124px)
        res = about.run()
        if res == -4 or -6:  # close events
            about.destroy()

    def _quit(self, widget):
        Gtk.main_quit()
