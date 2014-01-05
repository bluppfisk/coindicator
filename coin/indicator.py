# -*- coding: utf-8 -*-

# Ubuntu App indicator
# https://unity.ubuntu.com/projects/appindicators/

__author__ = "nil.gradisnik@gmail.com"

import sys
import gtk
import appindicator

import utils
from exchange.kraken import CONFIG as KrakenConfig

ICON_NAME = "gtk-info"

class Indicator:

  def __init__(self, config):
    self.config = config

    self.refresh_frequency = config['default']['refresh']

    self.ind = appindicator.Indicator(self.config['app']['name'], ICON_NAME, appindicator.CATEGORY_APPLICATION_STATUS)
    self.ind.set_status(appindicator.STATUS_ACTIVE)
    self.ind.set_label("syncing", "$888.88")

    self._menu_setup()
    self.ind.set_menu(self.menu)

  def init(self, exchanges):
    self.exchanges = exchanges

    # TODO: set defaults
    self.active_exchange_index = 0
    self.active_exchange = self.exchanges[self.active_exchange_index]['code']

    self.active_asset_pair_index = 0
    self.active_asset_pair = KrakenConfig['asset_pairs'][self.active_asset_pair_index]['code']

    self._start_exchange()
    # self._preferences(None)

  def set_data(self, label, bid, high, low, ask, volume=None):
    self.ind.set_label(label)

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
    ap = "Asset pair: " + self.active_asset_pair if self.active_exchange == 'kraken' else ''
    print "Using [" + self.active_exchange + "] exchange. (" + str(self.refresh_frequency) + "s refresh) " + ap

    self._stop_exchanges()

    exchange = self.exchanges[self.active_exchange_index]
    exchange['instance'].start()

  def _stop_exchanges(self):
    for exchange in self.exchanges:
      exchange['instance'].stop()

  def _menu_setup(self):
    self.menu = gtk.Menu()

    self.bid_item = gtk.MenuItem(utils.category['bid'])
    self.bid_item.show()

    self.high_item = gtk.MenuItem(utils.category['high'])
    self.high_item.show()

    self.low_item = gtk.MenuItem(utils.category['low'])
    self.low_item.show()

    self.ask_item = gtk.MenuItem(utils.category['ask'])
    self.ask_item.show()

    self.volume_item = gtk.MenuItem(utils.category['volume'])
    self.volume_item.show()

    separator_item = gtk.SeparatorMenuItem()
    separator_item.show()

    preferences_item = gtk.MenuItem("Preferences")
    preferences_item.connect("activate", self._preferences)
    preferences_item.show()

    about_item = gtk.MenuItem("About")
    about_item.connect("activate", self._about)
    about_item.show()

    quit_item = gtk.MenuItem("Quit")
    quit_item.connect("activate", self._quit)
    quit_item.show()

    self.menu.append(self.bid_item)
    self.menu.append(self.high_item)
    self.menu.append(self.low_item)
    self.menu.append(self.ask_item)
    self.menu.append(self.volume_item)
    self.menu.append(separator_item)
    self.menu.append(preferences_item)
    self.menu.append(about_item)
    self.menu.append(quit_item)

  def _about(self, widget):
    about = gtk.AboutDialog()
    about.set_name(self.config['app']['name'])
    about.set_comments(self.config['app']['description'])
    about.set_copyright(self.config['author']['copyright'])
    about.set_version(str(self.config['app']['version']))
    about.set_website(self.config['app']['url'])
    about.set_authors([self.config['author']['name'] + ' <' + self.config['author']['email'] + '>'])
    about.set_logo_icon_name(ICON_NAME)
    res = about.run()
    if res == -4 or -6:  # close events
      about.destroy()

  def _preferences(self, widget):
    p_dialog = gtk.Dialog(self.config['app']['name'] + " - Preferences")
    p_dialog.set_has_separator(True)
    p_dialog.add_button("Close", 1)

    p_dialog.vbox.add(self._p_refresh())
    p_dialog.vbox.add(gtk.HSeparator())
    p_dialog.vbox.add(self._p_exchange())
    p_dialog.vbox.add(self._p_kraken_extra())

    p_dialog.set_border_width(10)
    p_dialog.vbox.set_spacing(10)
    p_dialog.show_all()

    if (self.active_exchange != 'kraken'):
      self.p_kraken_extra.hide()

    res = p_dialog.run()
    if res == 1:
      p_dialog.destroy()
      self._start_exchange()

  # refresh section
  def _p_refresh(self):
    label_refresh = gtk.Label("Refresh every")
    label_refresh.set_alignment(.9, .5)
    label_seconds = gtk.Label("seconds")

    spin = gtk.SpinButton()
    spin.set_increments(1, 1)
    spin.set_range(3, 120)
    spin.set_value(self.refresh_frequency)
    spin.connect('value-changed', self._refresh_change)

    hbox = gtk.HBox()
    hbox.add(label_refresh)
    hbox.add(spin)
    hbox.add(label_seconds)
    hbox.set_spacing(10)
    hbox.set_border_width(20)

    return hbox

  def _refresh_change(self, widget):
    self.refresh_frequency = widget.get_value_as_int()

  # exchange section
  def _p_exchange(self):
    label = gtk.Label("Exchange")
    label.set_alignment(.9, .5)
    cell = gtk.CellRendererText()
    liststore = gtk.ListStore(str, str)
    for exchange in self.exchanges:
      liststore.append([exchange['code'], exchange['name']])
    combobox = gtk.ComboBox(liststore)
    combobox.pack_start(cell, True)
    combobox.add_attribute(cell, 'text', 1)
    combobox.set_active(self.active_exchange_index)
    combobox.connect('changed', self._change_exchange)

    hbox = gtk.HBox()
    hbox.add(label)
    hbox.add(combobox)
    hbox.set_border_width(10)

    return hbox

  def _change_exchange(self, widget):
    self.active_exchange_index = widget.get_active()
    self.active_exchange = widget.get_active_text()

    self.p_kraken_extra.hide()
    if (self.active_exchange == 'kraken'):
      self.p_kraken_extra.show()

  def _p_kraken_extra(self):
    label = gtk.Label("Currency")
    label.set_alignment(.9, .5)
    label.set_size_request(102, 20)
    cell = gtk.CellRendererText()
    liststore = gtk.ListStore(str, str)
    for asset in KrakenConfig['asset_pairs']:
      liststore.append([asset['code'], asset['name']])
    combobox = gtk.ComboBox(liststore)
    combobox.pack_start(cell, True)
    combobox.add_attribute(cell, 'text', 1)
    combobox.set_active(self.active_asset_pair_index)
    combobox.connect('changed', self._change_assetpair)

    self.p_kraken_extra = gtk.HBox()
    self.p_kraken_extra.add(label)
    self.p_kraken_extra.add(combobox)
    self.p_kraken_extra.set_border_width(10)

    alignment = gtk.Alignment() 
    alignment.set_size_request(200, 50)
    alignment.add(self.p_kraken_extra)

    return alignment

  def _change_assetpair(self, widget):
    self.active_asset_pair_index = widget.get_active()
    self.active_asset_pair = widget.get_active_text()

  def _quit(self, widget):
    sys.exit(0)
