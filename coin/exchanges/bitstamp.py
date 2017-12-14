# -*- coding: utf-8 -*-

# Bitstamp
# https://www.bitstamp.net/api/

__author__ = "nil.gradisnik@gmail.com"

from gi.repository import GLib
import logging
from error import Error
from exchange import Exchange, CURRENCY, CATEGORY


CONFIG = {
  'ticker': 'https://www.bitstamp.net/api/ticker/',
  'asset_pairs': [
    {
      'isocode': 'XXBTZUSD',
      'pair': 'XXBTZUSD',
      'name': 'BTC to USD',
      'currency': CURRENCY['usd']
    }
  ]
}

class Bitstamp(Exchange):
  pass

  def get_ticker(self):
    return self.config['ticker']

  def _parse_result(self, data):
    if data.status_code == 200:
      self.error.clear()
      asset = data.json()
    else:
      self.error.increment()
      return

    currency = CURRENCY['usd']
    label = currency + self.decimal_auto(asset['last'])

    bid = CATEGORY['bid'] + currency + self.decimal_auto(asset['bid'])
    high = CATEGORY['high'] + currency + self.decimal_auto(asset['high'])
    low = CATEGORY['low'] + currency + self.decimal_auto(asset['low'])
    ask = CATEGORY['ask'] + currency + self.decimal_auto(asset['ask'])
    volume = CATEGORY['volume'] + self.decimal_auto(asset['volume'])

    GLib.idle_add(self.indicator.set_data, label, bid, high, low, ask, volume)