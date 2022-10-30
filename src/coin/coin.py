#!/usr/bin/env python3
# Coin Price Indicator
#
# Nil Gradisnik <nil.gradisnik@gmail.com>
# Sander Van de Moortel <sander.vandemoortel@gmail.com>
#

from functools import cache
import os

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
gi.require_version("AppIndicator3", "0.1")
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import importlib
import logging
import signal
from pathlib import Path

import dbus
import notify2
import yaml
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import Gtk

from coin.about import AboutWindow
from coin.downloader import AsyncDownloadService, DownloadService
from coin.indicator import Indicator
from coin.plugin_selection import PluginSelectionWindow
from coin.coingecko_client import CoinGeckoClient
from coin.config import Config

try:
    from gi.repository import AppIndicator3 as AppIndicator
except ImportError:
    from gi.repository import AppIndicator


log_level = getattr(logging, os.environ.get("COIN_LOGLEVEL", "ERROR"))
logging.basicConfig(
    datefmt="%H:%M:%S",
    level=log_level,
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
)
logging.getLogger("urllib3").setLevel(logging.ERROR)


class Coin:
    def __init__(self, config: Config):
        self.config = config
        self.downloader = AsyncDownloadService()
        self.assets = {}
        self.coingecko_client = CoinGeckoClient()
        self.coingecko_client.load_list()
        self._load_exchanges()
        self._load_assets()
        self._load_settings()
        self._start_main()

        self.instances = []
        self.discoveries = 0
        self._add_many_indicators(self.config["settings"].get("tickers"))
        self._start_gui()

    # Load exchange 'plug-ins' from exchanges dir
    def _load_exchanges(self):
        dirfiles = (Path(__file__).parent / "exchanges").glob("*.py")
        plugins = [
            f.name[:-3] for f in dirfiles if f.exists() and f.name != "__init__.py"
        ]
        plugins.sort()

        self.exchanges = {}
        for plugin in plugins:
            class_name = plugin.capitalize()
            exchange_class = getattr(
                importlib.import_module("coin.exchanges." + plugin), class_name
            )
            self.exchanges[exchange_class.code] = exchange_class

    # Creates a structure of available assets (from_currency > to_currency > exchange)
    def _load_assets(self):
        self.assets = {}

        for exchange in self.exchanges.values():
            if exchange.active:
                if not exchange.asset_pairs:
                    exchange.discover_assets(DownloadService(), lambda *args: None)
                self.assets[exchange.code] = exchange.asset_pairs

        # inverse the hierarchy for easier asset selection
        bases = {}
        for exchange in self.assets.keys():
            asset_pair = self.assets.get(exchange)
            for asset_pair in self.assets.get(exchange):
                base = asset_pair.get("base")
                quote = asset_pair.get("quote")

                if base not in bases:
                    bases[base] = {}

                if quote not in bases[base]:
                    bases[base][quote] = []

                bases[base][quote].append(self.exchanges[exchange])

        self.bases = bases

    # load instances
    def _load_settings(self):
        for plugin in self.config["settings"].get("plugins", {}):
            for code, active in plugin.items():
                exchange = self.exchanges.get(code)
                if exchange is not None:
                    exchange.active = active

        # set defaults if settings not defined
        if not self.config["settings"].get("tickers"):
            first_exchange = next(iter(self.exchanges.values()))
            first_code = first_exchange.code

            # TODO work without defining a default
            self.config["settings"]["tickers"] = [
                {
                    "exchange": first_code,
                    "asset_pair": self.assets[first_code][0].get("pair"),
                    "refresh": 3,
                    "default_label": first_exchange.default_label,
                }
            ]

        if not self.config["settings"].get("recent"):
            self.config["settings"]["recent"] = []

    # saves settings for each ticker
    def save_settings(self):
        tickers = []
        for instance in self.instances:
            ticker = {
                "exchange": instance.exchange.code,
                "asset_pair": instance.exchange.asset_pair.get("pair"),
                "refresh": instance.refresh_frequency,
                "default_label": instance.default_label,
            }
            tickers.append(ticker)
            self.config["settings"]["tickers"] = tickers

        plugins = []
        for exchange in self.exchanges.values():
            plugin = {exchange.code: exchange.active}
            plugins.append(plugin)

        self.config["settings"]["plugins"] = plugins

        try:
            with open(self.config["user_settings_file"], "w") as handle:
                yaml.dump(self.config["settings"], handle, default_flow_style=False)
        except IOError:
            logging.error("Settings file not writable")

    # Add a new base to the recents settings, and push the last one off the edge
    def add_new_recent(self, asset_pair, exchange_code):
        for recent in self.config["settings"]["recent"]:
            if (
                recent.get("asset_pair") == asset_pair
                and recent.get("exchange") == exchange_code
            ):
                self.config["settings"]["recent"].remove(recent)

        self.config["settings"]["recent"] = self.config["settings"]["recent"][0:4]

        new_recent = {"asset_pair": asset_pair, "exchange": exchange_code}

        self.config["settings"]["recent"].insert(0, new_recent)

        for instance in self.instances:
            instance.rebuild_recents_menu()

    # Start the main indicator icon and its menu
    def _start_main(self):
        logging.info(
            "%s v%s running!"
            % (
                self.config.get("app").get("name"),
                self.config.get("app").get("version"),
            )
        )

        self.icon = self.config["project_root"] / "resources/icon_32px.png"
        self.main_item = AppIndicator.Indicator.new(
            self.config.get("app").get("name"),
            str(self.icon),
            AppIndicator.IndicatorCategory.APPLICATION_STATUS,
        )
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
            "org.freedesktop.login1.Manager",
            "org.freedesktop.login1",
        )
        Gtk.main()

    # Program main menu
    def _menu(self):
        menu = Gtk.Menu()

        self.add_item = Gtk.MenuItem.new_with_label("Add Ticker")
        self.discover_item = Gtk.MenuItem.new_with_label("Discover Assets")
        self.plugin_item = Gtk.MenuItem.new_with_label("Plugins" + "\u2026")
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
        exchange = settings.get("exchange")
        refresh = settings.get("refresh")
        asset_pair = settings.get("asset_pair")
        default_label = settings.get("default_label")
        indicator = Indicator(self, exchange, asset_pair, refresh, default_label)
        self.instances.append(indicator)
        indicator.start()
        return indicator

    # adds many tickers
    def _add_many_indicators(self, tickers):
        for ticker in tickers:
            self._add_indicator(ticker)

    # Menu item to add a ticker
    def _add_ticker(self, widget):
        i = self._add_indicator(
            self.config["settings"].get("tickers")[
                len(self.config["settings"].get("tickers")) - 1
            ]
        )
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
    def _discover_assets(self, _widget):
        # Don't do anything if there are no active exchanges with discovery
        if (
            len([ex for ex in self.exchanges.values() if ex.active and ex.discovery])
            == 0
        ):
            return

        self.main_item.set_icon_full(
            str(self.config.get("project_root") / "resources/loading.png"),
            "Discovering assets",
        )

        for indicator in self.instances:
            if indicator.asset_selection_window:
                indicator.asset_selection_window.destroy()

        for exchange in self.exchanges.values():
            if exchange.active and exchange.discovery:
                exchange.discover_assets(self.downloader, self.update_assets)

    # When discovery completes, reload currencies and rebuild menus of all instances
    def update_assets(self):
        self.discoveries += 1
        if self.discoveries < len(
            [ex for ex in self.exchanges.values() if ex.active and ex.discovery]
        ):
            return  # wait until all active exchanges with discovery finish discovery

        self.discoveries = 0
        self._load_assets()

        if notify2.init(self.config.get("app").get("name")):
            n = notify2.Notification(
                self.config.get("app").get("name"),
                "Finished discovering new assets",
                str(self.icon),
            )
            n.set_urgency(1)
            n.timeout = 2000
            n.show()

        self.main_item.set_icon_full(str(self.icon), "App icon")

    # Handle system resume by refreshing all tickers
    def handle_resume(self, sleeping, *args):
        if not sleeping:
            for instance in self.instances:
                instance.exchange.stop().start()

    def _select_plugins(self, _widget):
        PluginSelectionWindow(self)

    # Menu item to remove all tickers and quits the application
    def _quit_all(self, _widget):
        Gtk.main_quit()

    def plugins_updated(self):
        self._load_assets()
        for instance in self.instances:
            instance.start()  # will stop exchange if inactive

        self.save_settings()

    def _about(self, _widget):
        AboutWindow(self.config).show()


def main():
    project_root = Path(__file__).parent
    user_data_dir = Path(os.environ["HOME"]) / ".config/coindicator"
    user_data_dir.mkdir(exist_ok=True)

    icon_dir = user_data_dir / "coin-icons"
    icon_dir.mkdir(exist_ok=True)

    cache_dir = user_data_dir / "cache"
    cache_dir.mkdir(exist_ok=True)

    config_file = project_root / "config.yaml"
    config_data = yaml.load(config_file.open(), Loader=yaml.SafeLoader)

    user_settings_file = user_data_dir / "user.conf"
    settings = {}
    if user_settings_file.exists():
        settings = yaml.load(user_settings_file.open(), Loader=yaml.SafeLoader)

    config = Config(config_data)
    config["project_root"] = project_root
    config["user_data_dir"] = user_data_dir
    config["icon_dir"] = icon_dir
    config["cache_dir"] = cache_dir

    config["user_settings_file"] = user_settings_file
    config["settings"] = settings

    Coin(config)


if __name__ == "__main__":
    main()
