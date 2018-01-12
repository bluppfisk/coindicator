# -*- coding: utf-8 -*-

# GSettings

from gi.repository import Gio
import logging

__author__ = "nil.gradisnik@gmail.com"

SCHEMA_ID = 'org.nil.indicator.coinprice'

DEFAULTS = {
    'refresh': 30,
    'exchange': 'bxinth',
    'assetpair': 'XXBTCZTHB',
}

class Settings(object):
    def __init__(self, manual_settings=None):
        if manual_settings == 'DEFAULTS':
            self.manual_settings = [DEFAULTS['exchange'], DEFAULTS['assetpair'], DEFAULTS['refresh']]
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

    def getRefresh(self):
        if self.manual_settings:
            return int(self.manual_settings[2])
        elif self.settings:
            return self.settings.get_int('refresh')
        else:
            return DEFAULTS['refresh']

    def setRefresh(self, val):
        if not self.manual_settings:
            self.settings.set_int('refresh', val)
            return True

    def getExchange(self):
        if self.manual_settings:
            return self.manual_settings[0].lower()
        elif self.settings:
            return self.settings.get_string('exchange')
        else:
            return DEFAULTS['exchange']

    def setExchange(self, val):
        if not self.manual_settings:
            self.settings.set_string('exchange', val)
            return True

    def getAssetpair(self):
        if self.manual_settings:
            return self.manual_settings[1].upper()
        elif self.settings:
            return self.settings.get_string('assetpair')
        else:
            return DEFAULTS['assetpair']

    def setAssetpair(self, val):
        if not self.manual_settings:
            self.settings.set_string('assetpair', val.upper())
            return True