#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Coin Price indicator
# 
# Nil Gradisnik <nil.gradisnik@gmail.com>
# Sander Van de Moortel <sander.vandemoortel@gmail.com>
# 

from os.path import abspath, dirname, isfile, basename
import signal, yaml, sys, logging, gi, glob, dbus, importlib
from dbus.mainloop.glib import DBusGMainLoop
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, GdkPixbuf, GObject
try:
    from gi.repository import AppIndicator3 as AppIndicator
except ImportError:
    from gi.repository import AppIndicator
from indicator import Indicator

PROJECT_ROOT = abspath(dirname(dirname(__file__)))

signal.signal(signal.SIGINT, signal.SIG_DFL)  # ctrl+c exit

class Coin(object):
    config = yaml.load(open(PROJECT_ROOT + '/config.yaml', 'r'))
    config['project_root'] = PROJECT_ROOT

    def __init__(self):
        self._load_exchanges()
        self._load_assets()
        self._start_main()

        self.instances = []
        print(self.config.get('app').get('name') + ' v' + self.config['app']['version'] + " running!")
        usage_error = '\nUsage: coin.py [arguments]\n* asset=exchange:asset_pair:refresh_rate\tLoad a specific asset\n* file=file_to_load.yaml\t\t\tLoad several tickers defined in a YAML file.\n'

        # parse commandline arguments
        if len(sys.argv) > 2:
            quit('Too many parameters\n' + usage_error)

        if len(sys.argv) == 2:
            if '=' in sys.argv[1]:
                args = sys.argv[1].split('=')
                if args[0] == 'file':
                    try:
                        cp_instances = yaml.load(open(PROJECT_ROOT + '/coin/' + args[1], 'r'))
                    except:
                        quit('Error opening assets file')
                    
                    self._add_many_indicators(cp_instances)

                elif args[0] == 'asset':
                    self._add_indicator(args[1])

                else:
                    quit('Invalid parameter\n' + usage_error)

            else:
                quit('Invalid parameter\n' + usage_error)

        else:
            self._add_indicator()

    # Load exchange 'plug-ins' from exchanges dir
    def _load_exchanges(self):
        dirfiles = glob.glob(dirname(__file__) + "/exchanges/*.py")
        plugins = [ basename(f)[:-3] for f in dirfiles if isfile(f) and not f.endswith('__init__.py')]
        plugins.sort()

        self.EXCHANGES = []
        for plugin in plugins:
            class_name = plugin.capitalize()
            class_ = getattr(importlib.import_module('exchanges.' + plugin), class_name)

            self.EXCHANGES.append({
                'code': plugin,
                'name': class_name,
                'class': class_,
                'default_label': class_.CONFIG.get('default_label') or 'cur'
            })

    # Creates a structure of available assets (from_currency > to_currency > exchange)
    def _load_assets(self):
        self.CURRENCIES = {}
        for exchange in self.EXCHANGES:
            self.CURRENCIES[exchange.get('code')] = exchange.get('class').CONFIG.get('asset_pairs')

    # Start the main indicator icon and its menu
    def _start_main(self):
        icon = self.config['project_root'] + '/resources/icon_32px.png'
        self.logo_124px = GdkPixbuf.Pixbuf.new_from_file(self.config['project_root'] + '/resources/icon_32px.png')
        self.main_item = AppIndicator.Indicator.new(self.config['app']['name'], icon, AppIndicator.IndicatorCategory.APPLICATION_STATUS)
        self.main_item.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.main_item.set_menu(self._menu())

    # Program main menu
    def _menu(self):
        menu = Gtk.Menu()

        self.add_item = Gtk.MenuItem("Add Ticker")
        self.discover_item = Gtk.MenuItem("Update Assets")
        self.about_item = Gtk.MenuItem("About")
        self.quit_item = Gtk.MenuItem("Quit")
        
        self.add_item.connect("activate", self._add_ticker)
        self.discover_item.connect("activate", self._discover_assets)
        self.about_item.connect("activate", self._about)
        self.quit_item.connect("activate", self._quit_all)

        menu.append(self.add_item)
        menu.append(self.discover_item)
        menu.append(self.about_item)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(self.quit_item)
        menu.show_all()

        return menu

    # Adds a ticker and starts it
    def _add_indicator(self, settings=None):
        indicator = Indicator(self, settings)
        self.instances.append(indicator)
        indicator.start()

    # adds many tickers
    def _add_many_indicators(self, cp_instances):
        for cp_instance in cp_instances:
            settings = cp_instance.get('exchange') + ':' + cp_instance.get('asset_pair') + ':' + str(cp_instance.get('refresh'))
            self._add_indicator(settings)

    # Menu item to add a ticker
    def _add_ticker(self, widget):
        self._add_indicator('DEFAULTS')

    # Menu item to download any new assets from the exchanges
    def _discover_assets(self, widget):
        for exchange in self.EXCHANGES:
            exchange.get('class')(None, self).discover_assets()

    # When discovery completes, reload currencies and rebuild menus of all instances
    def update_assets(self):
        self._load_assets()
        for instance in self.instances:
            # instance.load_asset_pairs()
            instance.rebuild_asset_menu()

    # Handle system resume by refreshing all tickers
    def handle_resume(self, sleeping, *args):
        if not sleeping:
            for instance in self.instances:
                instance.exchange_instance.stop().start()

    # Shows an About dialog
    def _about(self, widget):
        about = Gtk.AboutDialog()
        about.set_program_name(self.config['app']['name'])
        about.set_comments(self.config['app']['description'])
        about.set_version(self.config['app']['version'])
        about.set_website(self.config['app']['url'])
        authors = []
        for author in self.config['authors']:
            authors.append(author['name'] + ' <' + author['email'] + '>')
        about.set_authors(authors)
        contributors = []
        for contributor in self.config['contributors']:
            contributors.append(contributor['name'] + ' <' + contributor['email'] + '>')
        about.add_credit_section('Exchange plugins', contributors)
        about.set_artists([self.config['artist']['name'] + ' <' + self.config['artist']['email'] + '>'])
        about.set_license_type(Gtk.License.MIT_X11)
        about.set_logo(self.logo_124px)
        about.set_keep_above(True)
        res = about.run()
        if res == -4 or -6:  # close events
            about.destroy()

    # Menu item to remove all tickers and quits the application
    def _quit_all(self, widget):
        Gtk.main_quit()

coin = Coin()
DBusGMainLoop(set_as_default = True)
bus = dbus.SystemBus()
bus.add_signal_receiver(
    coin.handle_resume,
    None,
    'org.freedesktop.login1.Manager',
    'org.freedesktop.login1'
)
Gtk.main()
