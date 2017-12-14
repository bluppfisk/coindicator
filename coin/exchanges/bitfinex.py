# -*- coding: utf-8 -*-

# Bitfinex
# https://docs.bitfinex.com/

__author__ = "eliezer.aquino@gmail.com"

from gi.repository import GLib
import logging
from error import Error
from exchange import Exchange, CURRENCY, CATEGORY


CONFIG = {
  'ticker': 'https://api.bitfinex.com/v1/pubticker/',
  'asset_pairs': [
    {
       'isocode': 'XXBTZUSD',
      'pair': 'btcusd',
      'name': 'BTC to USD',
      'currency': CURRENCY['usd']
    },
    {
      'isocode': 'XIOTZUSD',
      'pair': 'iotusd',
      'name': 'IOTA to USD',
      'currency': CURRENCY['usd']
    }
  ]
}

class Bitfinex(Exchange):
  pass

  def get_ticker(self):
    return self.config['ticker'] + self.pair

  def _parse_result(self, data):
    if data.status_code == 200:
      self.error.clear()
      asset = data.json()
    else:
      self.error.increment()
      return
    
    currency = CURRENCY['usd']

    label = currency + self.decimal_auto(asset['last_price'])

    bid = CATEGORY['bid'] + currency + self.decimal_auto(asset['bid'])
    high = CATEGORY['high'] + currency + self.decimal_auto(asset['high'])
    low = CATEGORY['low'] + currency + self.decimal_auto(asset['low'])
    ask = CATEGORY['ask'] + currency + self.decimal_auto(asset['ask'])
    volume = CATEGORY['volume'] + self.decimal_auto(asset['volume'])

    GLib.idle_add(self.indicator.set_data, label, bid, high, low, ask, volume)