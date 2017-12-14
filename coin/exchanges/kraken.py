# -*- coding: utf-8 -*-

# Kraken
# https://www.kraken.com/help/api#public-market-data

__author__ = "nil.gradisnik@gmail.com"

from gi.repository import GLib
import logging
from error import Error
from exchange import Exchange, CURRENCY, CATEGORY

CONFIG = {
  'ticker': 'https://api.kraken.com/0/public/Ticker',
  'asset_pairs': [
    {
      'isocode': 'XXBTZUSD',
      'pair': 'XXBTZUSD',
      'name': 'BTC to USD',
      'currency': CURRENCY['usd']
    },
    {
      'isocode': 'XXBTZEUR',
      'pair': 'XXBTZEUR',
      'name': 'BTC to EUR',
      'currency': CURRENCY['eur']
    },
    {
      'isocode': 'XXLTZUSD',
      'pair': 'XLTCZUSD',
      'name': 'LTC to USD',
      'currency': CURRENCY['usd']
    },
    {
      'isocode': 'XXLTZEUR',
      'pair': 'XLTCZEUR',
      'name': 'LTC to EUR',
      'currency': CURRENCY['eur']
    },
    {
      'isocode': 'XXETZUSD',
      'pair': 'XETHZUSD',
      'name': 'ETH to USD',
      'currency': CURRENCY['usd']
    },
    {
      'isocode': 'XXETZEUR',
      'pair': 'XETHZEUR',
      'name': 'ETH to EUR',
      'currency': CURRENCY['eur']
    },
    {
      'isocode': 'XXBCZEUR',
      'pair': 'BCHEUR',
      'name': 'BCH to EUR',
      'currency': CURRENCY['eur']
    },
    {
      'isocode': 'XXRPZEUR',
      'pair': 'XXRPZEUR',
      'name': 'XRP to EUR',
      'currency': CURRENCY['eur']
    }
  ]
}

class Kraken(Exchange):
  pass

  def get_ticker(self):
    return self.config['ticker'] + '?pair=' + self.pair

  def _parse_result(self, data):
    if data.status_code == 200:
      self.error.clear()
      try:
        asset = data.json()['result'][self.pair]
      except Exception as e:
        # Usually a KeyError happens when an asynchronous response comes in
        # for a previously selected asset pair (see upstream issue #27)
        logging.info('invalid response for ' + str(self.pair))

    else:
      self.error.increment()
      return

    config = [item for item in CONFIG['asset_pairs'] if item['isocode'] == self.asset_pair][0]

    currency = config['currency']
    coin = config['name']

    label = currency + self.decimal_auto(asset['c'][0])

    bid = CATEGORY['bid'] + currency + self.decimal_auto(asset['b'][0])
    high = CATEGORY['high'] + currency + self.decimal_auto(asset['h'][1])
    low = CATEGORY['low'] + currency + self.decimal_auto(asset['l'][1])
    ask = CATEGORY['ask'] + currency + self.decimal_auto(asset['a'][0])
    vol = CATEGORY['volume'] + self.decimal_auto(asset['v'][1])

    GLib.idle_add(self.indicator.set_data, label, bid, high, low, ask, vol)