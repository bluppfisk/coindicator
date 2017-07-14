# -*- coding: utf-8 -*-

# GSettings

from gi.repository import Gio

__author__ = "nil.gradisnik@gmail.com"

SCHEMA_ID = 'org.nil.indicator.coinprice'

DEFAULTS = {
    'refresh': 30,
    'exchange': 'kraken',
    'assetpair-kraken': 'XXBTZUSD',
    'assetpair-btce': 'btc_usd'
}


class Settings(object):
    def __init__(self):
        self.settings = None

        source = Gio.SettingsSchemaSource.get_default()
        if source.lookup(SCHEMA_ID, True):
            self.settings = Gio.Settings(SCHEMA_ID)
        else:
            print("GSettings: schama [" + SCHEMA_ID + "] not installed. Using defaults.")

    def refresh(self, val=None):
        if self.settings:
            return self.settings.get_int('refresh') if not val else self.settings.set_int('refresh', val)
        else:
            return DEFAULTS['refresh']

    def exchange(self, val=None):
        if self.settings:
            return self.settings.get_string('exchange') if not val else self.settings.set_string('exchange', val)
        else:
            return DEFAULTS['exchange']

    def assetpair(self, exchange, val=None):
        if self.settings:
            return self.settings.get_string('assetpair-' + exchange) if not val else self.settings.set_string(
                'assetpair-' + exchange, val)
        else:
            return DEFAULTS['assetpair' + exchange]
