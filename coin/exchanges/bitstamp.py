# -*- coding: utf-8 -*-

# Bitstamp
# https://www.bitstamp.net/api/

__author__ = "nil.gradisnik@gmail.com"

from gi.repository import GLib
import logging, utils
from error import Error
from exchange import Exchange

CONFIG = {
  'ticker': 'https://www.bitstamp.net/api/ticker/',
  'asset_pairs': [
    {
      'isocode': 'XXBTZUSD',
      'pair': 'XXBTZUSD',
      'name': 'BTC to USD',
      'currency': utils.currency['usd']
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

    currency = utils.currency['usd']
    label = currency + utils.decimal_auto(asset['last'])

    bid = utils.category['bid'] + currency + utils.decimal_auto(asset['bid'])
    high = utils.category['high'] + currency + utils.decimal_auto(asset['high'])
    low = utils.category['low'] + currency + utils.decimal_auto(asset['low'])
    ask = utils.category['ask'] + currency + utils.decimal_auto(asset['ask'])
    volume = utils.category['volume'] + utils.decimal_auto(asset['volume'])

    GLib.idle_add(self.indicator.set_data, label, bid, high, low, ask, volume)