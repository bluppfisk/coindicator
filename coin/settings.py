# -*- coding: utf-8 -*-

# GSettings

__author__ = "nil.gradisnik@gmail.com"

from gi.repository import Gio

SCHEMA_ID = 'org.nil.indicator.coinprice'

DEFAULTS = {
  'refresh': 30,
  'exchange': 'kraken',
  'assetpair': 'XXBTZUSD'
}

class Settings():

  def __init__(self):
    self.settings = None

    source = Gio.SettingsSchemaSource.get_default()
    if (source.lookup(SCHEMA_ID, True)):
      self.settings = Gio.Settings(SCHEMA_ID)
    else:
      print("GSettings: schama [" + SCHEMA_ID + "] not installed. Using defaults.")

  def refresh(self, val=None):
    if (self.settings):
      return self.settings.get_int('refresh') if val is None else self.settings.set_int('refresh', val)
    else:
      return DEFAULTS['refresh']

  def exchange(self, val=None):
    if (self.settings):
      return self.settings.get_string('exchange') if val is None else self.settings.set_string('exchange', val)
    else:
      return DEFAULTS['exchange']

  def assetpair(self, val=None):
    if (self.settings):
      return self.settings.get_string('assetpair') if val is None else self.settings.set_string('assetpair', val)
    else:
      return DEFAULTS['assetpair']
