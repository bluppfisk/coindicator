# -*- coding: utf-8 -*-

# GSettings

from gi.repository import Gio
import logging

__author__ = "nil.gradisnik@gmail.com"

SCHEMA_ID = 'org.nil.indicator.coinprice'

DEFAULTS = {
    'refresh': 30,
    'exchange': 'kraken',
    'asset-pair': 'XXBTZUSD', # hyphen because of how GSettings handles names
}

class Settings(object):
    def __init__(self, manual_settings=None):
        if manual_settings == 'DEFAULTS':
            self.manual_settings = [DEFAULTS['exchange'], DEFAULTS['asset-pair'], DEFAULTS['refresh']]
            return
        
        self.settings = None
        self.manual_settings = None

        if manual_settings:
            self.manual_settings = manual_settings.split(':')
        else:
            source = Gio.SettingsSchemaSource.get_default()
            if source.lookup(SCHEMA_ID, True):
                self.settings = Gio.Settings(SCHEMA_ID)
            else:
                self.settings = None
                logging.info("GSettings: schema [" + SCHEMA_ID + "] not installed. Using defaults.")

    def get_refresh(self):
        if self.manual_settings:
            return int(self.manual_settings[2])
        elif self.settings:
            return self.settings.get_int('refresh')
        else:
            return DEFAULTS['refresh']

    def set_refresh(self, val):
        if not self.manual_settings:
            self.settings.set_int('refresh', val)
            return True

    def get_exchange(self):
        if self.manual_settings:
            return self.manual_settings[0].lower()
        elif self.settings:
            return self.settings.get_string('exchange')
        else:
            return DEFAULTS['exchange']

    def set_exchange(self, val):
        if not self.manual_settings:
            self.settings.set_string('exchange', val)
            return True

    def get_asset_pair(self):
        if self.manual_settings:
            return self.manual_settings[1].upper()
        elif self.settings:
            return self.settings.get_string('asset-pair')
        else:
            return DEFAULTS['asset-pair']

    def set_asset_pair(self, val):
        if not self.manual_settings:
            self.settings.set_string('asset-pair', val.upper())
            return True