# The ticker AppIndicator item that sits in the tray
# https://unity.ubuntu.com/projects/appindicators/

import logging
from math import floor

from gi.repository import GLib, Gtk

from uuid import uuid1

from coin.alarm import Alarm, AlarmSettingsWindow
from coin.config import Config
from coin.asset_selection import AssetSelectionWindow

try:
    from gi.repository import AppIndicator3 as AppIndicator
except ImportError:
    from gi.repository import AppIndicator


REFRESH_TIMES = [3, 5, 10, 30, 60]  # seconds

CATEGORIES = [
    ("cur", "Now"),
    ("bid", "Bid"),
    ("ask", "Ask"),
    ("high", "High"),
    ("low", "Low"),
    ("avg", "Avg"),
]


class Indicator(object):
    def __init__(self, coin, exchange, asset_pair, refresh, default_label):
        self.config = Config()
        self.coin = coin  # reference to main program
        self.alarm = Alarm(self)
        self.exchange = self.coin.exchanges[exchange](self)
        self.exchange.set_asset_pair_from_code(asset_pair)
        self.refresh_frequency = refresh
        self.default_label = default_label
        self.asset_selection_window = None
        self.alarm_settings_window = None

        self.prices = {}
        self.latest_response = 0  # helps with discarding outdated responses

    # initialisation and start of indicator and exchanges
    def start(self):
        self.indicator_widget = AppIndicator.Indicator.new(
            "Coindicator_" + str(uuid1()),
            str(self.exchange.icon),
            AppIndicator.IndicatorCategory.APPLICATION_STATUS,
        )
        self.indicator_widget.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.indicator_widget.set_ordering_index(0)
        self.indicator_widget.set_menu(self._menu())
        if self.exchange.active:
            self._start_exchange()
        else:
            self._stop_exchange()

    # updates GUI menus with data stored in the object
    def update_gui(self):
        logging.debug("Updating GUI, last response was: " + str(self.latest_response))

        self.symbol = self.exchange.symbol
        self.volumecurrency = self.exchange.volume_currency

        if self.prices.get(self.default_label):
            label = self.symbol + self.prices.get(self.default_label)
        else:
            label = "select default label"

        self.indicator_widget.set_label(label, label)

        for item, name in CATEGORIES:
            price_menu_item = self.price_menu_items.get(item)  # get menu item

            # assigns prices to the corresponding menu items
            # if such a price value is returned from the exchange
            if self.prices.get(item):
                if item == self.default_label:
                    price_menu_item.set_active(True)
                    if self.alarm.active:
                        if self.alarm.check(float(self.prices.get(item))):
                            self.alarm.deactivate()

                price_menu_item.set_label(
                    name + ":\t\t" + self.symbol + " " + self.prices.get(item)
                )
                price_menu_item.show()
            # if no such price value is returned, hide the menu item
            else:
                price_menu_item.hide()

        # slightly different behaviour for volume menu item
        if self.prices.get("vol"):
            self.volume_item.set_label(
                "Vol:\t\t" + self.prices.get("vol") + " " + self.volumecurrency
            )
            self.volume_item.show()
        else:
            self.volume_item.hide()

    # (re)starts the exchange logic and its timer
    def _start_exchange(self):
        state_string = (
            self.exchange.name[0:8]
            + ":\t"
            + self.exchange.asset_pair.get("base")
            + " - "
            + self.exchange.asset_pair.get("quote")
        )
        logging.debug(
            "Loading " + state_string + " (" + str(self.refresh_frequency) + "s)"
        )

        # don't show any data until first response is in
        GLib.idle_add(self.indicator_widget.set_label, "loading", "loading")
        GLib.idle_add(self.state_item.set_label, state_string)
        for item in self.price_group:
            GLib.idle_add(item.set_active, False)
            GLib.idle_add(item.set_label, "loading" + "\u2026")

        self.volume_item.set_label("loading" + "\u2026")

        self._make_default_label(self.default_label)

        # start the timers and logic
        self.exchange.start()

    def _stop_exchange(self):
        GLib.idle_add(self.indicator_widget.set_label, "stopped", "stopped")
        self.exchange.stop()

    # promotes a price value to the main label position
    def _menu_make_label(self, widget, label):
        if widget.get_active():
            self._make_default_label(label)
            self.coin.save_settings()

    def _make_default_label(self, label):
        self.default_label = label
        if self.price_menu_items.get(self.default_label):
            new_label = self.prices.get(label)
            if new_label:
                self.indicator_widget.set_label(self.symbol + new_label, new_label)

    def _menu(self):
        menu = Gtk.Menu()
        self.state_item = Gtk.MenuItem("loading" + "\u2026")
        menu.append(self.state_item)

        menu.append(Gtk.SeparatorMenuItem())

        self.price_group = []  # so that a radio button can be set on the active one

        # hacky way to get every price item on the menu and filled
        self.price_menu_items = {}
        for price_type, name in CATEGORIES:
            self.price_menu_items[price_type] = Gtk.RadioMenuItem.new_with_label(
                self.price_group, "loading" + "\u2026"
            )
            self.price_menu_items[price_type].connect(
                "toggled", self._menu_make_label, price_type
            )
            self.price_group.append(self.price_menu_items.get(price_type))
            menu.append(self.price_menu_items.get(price_type))

        # trading volume display
        self.volume_item = Gtk.MenuItem("loading" + "\u2026")
        menu.append(self.volume_item)

        menu.append(Gtk.SeparatorMenuItem())

        # settings menu
        self.config_menu = Gtk.MenuItem("Change Asset" + "\u2026")
        self.config_menu.connect("activate", self._settings)
        menu.append(self.config_menu)

        # recents menu
        self.recents_menu = Gtk.MenuItem("Recents")
        self.recents_menu.set_submenu(self._menu_recents())
        menu.append(self.recents_menu)

        # refresh rate choice menu
        self.refresh_menu = Gtk.MenuItem("Refresh")
        self.refresh_menu.set_submenu(self._menu_refresh())
        menu.append(self.refresh_menu)

        # alert menu
        self.alarm_menu = Gtk.MenuItem("Set Alert" + "\u2026")
        self.alarm_menu.connect("activate", self._alarm_settings)
        menu.append(self.alarm_menu)

        menu.append(Gtk.SeparatorMenuItem())

        # menu to remove current indicator from app
        remove_item = Gtk.MenuItem("Remove Ticker")
        remove_item.connect("activate", self._remove)
        menu.append(remove_item)

        menu.show_all()

        return menu

    def _menu_recents(self):
        recent_menu = Gtk.Menu()

        if len(self.config["settings"].get("recent")) == 0:
            return

        for recent in self.config["settings"].get("recent"):
            exchange = self.coin.exchanges.get(recent.get("exchange"))
            if exchange is None:
                continue
            asset_pair = exchange.find_asset_pair_by_code(
                recent.get("asset_pair", "None")
            )
            base = asset_pair.get("base", "None")
            quote = asset_pair.get("quote", "None")
            tabs = "\t" * (
                floor(abs((len(exchange.name) - 8)) / 4) + 1
            )  # 1 tab for every 4 chars less than 8
            recent_string = exchange.name[0:8] + ":" + tabs + base + " - " + quote
            recent_item = Gtk.MenuItem(recent_string)
            recent_item.connect("activate", self._recent_change, base, quote, exchange)
            recent_menu.append(recent_item)

        recent_menu.show_all()
        return recent_menu

    def _recent_change(self, _widget, base, quote, exchange):
        self.change_assets(base, quote, exchange)

    def rebuild_recents_menu(self):
        if self.recents_menu.get_submenu():
            self.recents_menu.get_submenu().destroy()
        self.recents_menu.set_submenu(self._menu_recents())

    def _menu_refresh(self):
        refresh_menu = Gtk.Menu()

        group = []
        for ri in REFRESH_TIMES:
            item = Gtk.RadioMenuItem.new_with_label(group, str(ri) + " sec")
            group.append(item)
            refresh_menu.append(item)

            if self.refresh_frequency == ri:
                item.set_active(True)
            item.connect("activate", self._menu_refresh_change, ri)

        return refresh_menu

    def _menu_refresh_change(self, widget, ri):
        if widget.get_active():
            self.refresh_frequency = ri
            self.coin.save_settings()
            self.exchange.stop().start()

    def change_assets(self, base, quote, exchange):
        self.exchange.stop()

        if self.exchange is not exchange:
            self.exchange = exchange(self)

        self.exchange.set_asset_pair(base, quote)

        accessible_icon_string = self.exchange.name[0:8] + ":" + base + " to " + quote

        self.indicator_widget.set_icon_full(
            str(self.exchange.icon), accessible_icon_string
        )

        self.coin.add_new_recent(
            self.exchange.asset_pair.get("pair"), self.exchange.code
        )

        self.coin.save_settings()
        self._start_exchange()
        self.prices = {}  # labels and prices may be different
        self.default_label = self.exchange.default_label

    def _remove(self, _widget):
        self.coin.remove_ticker(self)

    def _alarm_settings(self, _widget):
        self.alarm_settings_window = AlarmSettingsWindow(
            self, self.prices.get(self.default_label)
        )

    def _settings(self, _widget):
        for indicator in self.coin.instances:
            if indicator.asset_selection_window:
                indicator.asset_selection_window.destroy()

        self.asset_selection_window = AssetSelectionWindow(self)
