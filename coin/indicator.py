# -*- coding: utf-8 -*-

# Ubuntu App indicator
# https://unity.ubuntu.com/projects/appindicators/

__author__ = "nil.gradisnik@gmail.com"

from gi.repository import Gtk, GdkPixbuf
try:
  from gi.repository import AppIndicator3 as AppIndicator
except:
  from gi.repository import AppIndicator

import utils
from settings import Settings
from exchange.kraken import CONFIG as KrakenConfig

ICON_NAME = "gtk-info"

class Indicator:

  def __init__(self, config):
    self.config = config
    self.settings = Settings()

    self.indicator = AppIndicator.Indicator.new(self.config['app']['name'], ICON_NAME, AppIndicator.IndicatorCategory.APPLICATION_STATUS)
    self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
    self.indicator.set_label("syncing", "$888.88")

    self.indicator.set_menu(self._menu())

    self.logo_124px = GdkPixbuf.Pixbuf.new_from_file('resources/logo_124px.png')
    # self.logo_124px.saturate_and_pixelate(self.logo_124px, 1, True)

  def init(self, exchanges):
    self.exchanges = exchanges

    self.refresh_frequency = self.settings.refresh()
    self.active_exchange = self.settings.exchange()
    self.active_asset_pair = self.settings.assetpair()

    self._start_exchange()
    # self._preferences(None)

    Gtk.main()

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
    ap = "Asset pair: " + self.active_asset_pair if self.active_exchange == 'kraken' else ''
    print("Using [" + self.active_exchange + "] exchange. (" + str(self.refresh_frequency) + "s refresh) " + ap)

    self._stop_exchanges()

    exchange = [e['instance'] for e in self.exchanges if self.active_exchange == e['code']]
    if len(exchange) == 1:
      exchange[0].start()
    else:
      print("Error starting instance [" + self.active_exchange + "]")

  def _stop_exchanges(self):
    for exchange in self.exchanges:
      exchange['instance'].stop()

  def _menu(self):
    menu = Gtk.Menu()

    self.bid_item = Gtk.MenuItem(utils.category['bid'])
    self.bid_item.show()

    self.high_item = Gtk.MenuItem(utils.category['high'])
    self.high_item.show()

    self.low_item = Gtk.MenuItem(utils.category['low'])
    self.low_item.show()

    self.ask_item = Gtk.MenuItem(utils.category['ask'])
    self.ask_item.show()

    self.volume_item = Gtk.MenuItem(utils.category['volume'])
    self.volume_item.show()

    separator_item = Gtk.SeparatorMenuItem()
    separator_item.show()

    preferences_item = Gtk.MenuItem("Preferences")
    preferences_item.connect("activate", self._preferences)
    preferences_item.show()

    about_item = Gtk.MenuItem("About")
    about_item.connect("activate", self._about)
    about_item.show()

    quit_item = Gtk.MenuItem("Quit")
    quit_item.connect("activate", self._quit)
    quit_item.show()

    menu.append(self.bid_item)
    menu.append(self.high_item)
    menu.append(self.low_item)
    menu.append(self.ask_item)
    menu.append(self.volume_item)
    menu.append(separator_item)
    menu.append(preferences_item)
    menu.append(about_item)
    menu.append(quit_item)

    return menu

  def _about(self, widget):
    about = Gtk.AboutDialog()
    about.set_program_name(self.config['app']['name'])
    about.set_comments(self.config['app']['description'])
    about.set_copyright(self.config['author']['copyright'])
    about.set_version(str(self.config['app']['version']))
    about.set_website(self.config['app']['url'])
    about.set_authors([self.config['author']['name'] + ' <' + self.config['author']['email'] + '>'])
    about.set_artists([self.config['artist']['name'] + ' <' + self.config['artist']['email'] + '>'])
    about.set_license_type(Gtk.License.MIT_X11)
    about.set_logo(self.logo_124px)
    res = about.run()
    if res == -4 or -6:  # close events
      about.destroy()

  def _preferences(self, widget):
    p_dialog = Gtk.Dialog(self.config['app']['name'] + " - Preferences")
    p_dialog.add_button("Close", 1)

    p_dialog.vbox.add(self._p_refresh())
    p_dialog.vbox.add(Gtk.HSeparator())
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
    label_refresh = Gtk.Label("Refresh every")
    label_refresh.set_alignment(.9, .5)
    label_seconds = Gtk.Label("seconds")

    spin = Gtk.SpinButton()
    spin.set_increments(1, 1)
    spin.set_range(5, 120)
    spin.set_value(self.refresh_frequency)
    spin.connect('value-changed', self._refresh_change)

    hbox = Gtk.HBox()
    hbox.add(label_refresh)
    hbox.add(spin)
    hbox.add(label_seconds)
    hbox.set_spacing(10)
    hbox.set_border_width(20)

    return hbox

  def _refresh_change(self, widget):
    self.refresh_frequency = widget.get_value_as_int()
    self.settings.refresh(self.refresh_frequency)

  # exchange section
  def _p_exchange(self):
    label = Gtk.Label("Exchange")
    label.set_alignment(.9, .5)

    combo = Gtk.ComboBoxText()
    for exchange in self.exchanges:
      combo.append(exchange['code'], exchange['name'])
    combo.set_entry_text_column(1)
    combo.set_active_id(self.active_exchange)
    combo.connect('changed', self._change_exchange)

    hbox = Gtk.HBox()
    hbox.add(label)
    hbox.add(combo)
    hbox.set_border_width(10)

    return hbox

  def _change_exchange(self, combo):
    self.active_exchange = combo.get_active_id()
    self.settings.exchange(self.active_exchange)

    self.p_kraken_extra.hide()
    if (self.active_exchange == 'kraken'):
      self.p_kraken_extra.show()

  def _p_kraken_extra(self):
    label = Gtk.Label("Currency")
    label.set_alignment(.9, .5)
    label.set_size_request(76, 20)

    combo = Gtk.ComboBoxText()
    for asset in KrakenConfig['asset_pairs']:
      combo.append(asset['code'], asset['name'])
    combo.set_entry_text_column(1)
    combo.set_active_id(self.active_asset_pair)
    combo.connect('changed', self._change_assetpair)

    self.p_kraken_extra = Gtk.HBox()
    self.p_kraken_extra.add(label)
    self.p_kraken_extra.add(combo)
    self.p_kraken_extra.set_border_width(10)

    alignment = Gtk.Alignment()
    alignment.set_size_request(200, 50)
    alignment.add(self.p_kraken_extra)

    return alignment

  def _change_assetpair(self, combo):
    self.active_asset_pair = combo.get_active_id()
    self.settings.assetpair(self.active_asset_pair)

  def _quit(self, widget):
    Gtk.main_quit()
