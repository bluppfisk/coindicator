# -*- coding: utf-8 -*-
# Coin Price indicator
# Nil Gradisnik <nil.gradisnik@gmail.com>

import os, signal, yaml, sys, logging, gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk, GdkPixbuf, GObject, GLib

try:
    from gi.repository import AppIndicator3 as AppIndicator
except ImportError:
    from gi.repository import AppIndicator

from indicator import Indicator
from exchange.kraken import Kraken
from exchange.bitstamp import Bitstamp
from exchange.bityep import BitYep
from exchange.gdax import Gdax

import threading


PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

signal.signal(signal.SIGINT, signal.SIG_DFL)  # ctrl+c exit

class Coin(object):
    config = yaml.load(open(PROJECT_ROOT + '/config.yaml', 'r'))
    config['project_root'] = PROJECT_ROOT

    def __init__(self):
        self.gui_ready = threading.Event()
        self.start_main()
        self.instances = []
        logging.info("Coin Price indicator v" + self.config['app']['version'])
        usage_error = 'Usage: coin.py [flags]\nasset\texchange:asset_pair:refresh_rate\nfile\tLoads various asset pairs from YAML file in ./coin directory'
        if len(sys.argv) > 2:
            quit('Too many parameters\n' + usage_error)

        self.start_main()
        if len(sys.argv) == 2:
            if '=' in sys.argv[1]:
                args = sys.argv[1].split('=')
                if args[0] == 'file':
                    try:
                        cp_instances = yaml.load(open(PROJECT_ROOT + '/coin/' + args[1], 'r'))
                    except:
                        quit('Error opening assets file')
                    
                    self.add_many_indicators(cp_instances)

                elif args[0] == 'asset':
                    self.add_indicator(args[1])

                else:
                    quit('Invalid parameter\n' + usage_error)

            else:
                quit('Invalid parameter\n' + usage_error)

        else:
            self.add_indicator()

    # Start the main indicator icon and its menu
    def start_main(self):
        icon = self.config['project_root'] + '/resources/icon_32px.png'
        self.logo_124px = GdkPixbuf.Pixbuf.new_from_file(self.config['project_root'] + '/resources/icon_32px.png')
        self.main_item = AppIndicator.Indicator.new(self.config['app']['name'], icon, AppIndicator.IndicatorCategory.APPLICATION_STATUS)
        self.main_item.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.main_item.set_menu(self._menu())

        def start_gui_thread():
            self.gui_ready.wait()
            Gtk.main()

        self.gui_thread = threading.Thread(target=start_gui_thread)
        self.gui_thread.start()


    # Program main menu
    def _menu(self):
        menu = Gtk.Menu()

        self.add_item = Gtk.MenuItem("Add Ticker")
        self.about_item = Gtk.MenuItem("About")
        self.quit_item = Gtk.MenuItem("Quit")
        
        self.add_item.connect("activate", self._add_ticker)
        self.about_item.connect("activate", self._about)
        self.quit_item.connect("activate", self._quit_all)

        menu.append(self.add_item)
        menu.append(self.about_item)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(self.quit_item)
        menu.show_all()

        return menu

    # Adds a ticker and starts it
    def add_indicator(self, settings=None):
        indicator = Indicator(self, len(self.instances), self.config, settings)
        self.instances.append(indicator)
        indicator.start()
        self.gui_ready.set()

    # adds many tickers
    def add_many_indicators(self, cp_instances):
        for cp_instance in cp_instances:
            settings = cp_instance['exchange'] + ':' + cp_instance['asset_pair'] + ':' + str(cp_instance['refresh'])
            nt = threading.Thread(target=self.add_indicator(settings))

    # Menu item to add a ticker
    def _add_ticker(self, widget):
        self.add_indicator()

    # Shows an About dialog
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

    # Menu item to remove all tickers and quits the application
    def _quit_all(self, widget):
        logging.info("Exiting")
        Gtk.main_quit()

coin = Coin()
