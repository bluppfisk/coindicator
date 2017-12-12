# -*- coding: utf-8 -*-

# Bitfinex
# https://docs.bitfinex.com/

__author__ = "eliezer.aquino@gmail.com"

from gi.repository import GLib
import logging, utils
from exchange.error import Error
from exchange.exchange import Exchange

CONFIG = {
  'ticker': 'https://api.bitfinex.com/v1/pubticker/',
  'asset_pairs': [
    {
       'isocode': 'XXBTZUSD',
      'pair': 'btcusd',
      'name': 'BTC to USD',
      'currency': utils.currency['usd']
    },
    {
      'isocode': 'XIOTZUSD',
      'pair': 'iotusd',
      'name': 'IOTA to USD',
      'currency': utils.currency['usd']
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
    
    currency = utils.currency['usd']

    label = currency + utils.decimal_round(asset['last_price'])
    
    bid = utils.category['bid'] + currency + utils.decimal_round(asset['bid'])
    high = utils.category['high'] + currency + utils.decimal_round(asset['high'])
    low = utils.category['low'] + currency + utils.decimal_round(asset['low'])
    ask = utils.category['ask'] + currency + utils.decimal_round(asset['ask'])
    volume = utils.category['volume'] + utils.decimal_round(asset['volume'])

    GLib.idle_add(self.indicator.set_data, label, bid, high, low, ask, volume)