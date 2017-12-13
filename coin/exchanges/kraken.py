# -*- coding: utf-8 -*-

# Kraken
# https://www.kraken.com/help/api#public-market-data

__author__ = "nil.gradisnik@gmail.com"

from gi.repository import GLib
import logging, utils
from error import Error
from exchange import Exchange

CONFIG = {
  'ticker': 'https://api.kraken.com/0/public/Ticker',
  'asset_pairs': [
    {
      'isocode': 'XXBTZUSD',
      'pair': 'XXBTZUSD',
      'name': 'BTC to USD',
      'currency': utils.currency['usd']
    },
    {
      'isocode': 'XXBTZEUR',
      'pair': 'XXBTZEUR',
      'name': 'BTC to EUR',
      'currency': utils.currency['eur']
    },
    {
      'isocode': 'XXLTZUSD',
      'pair': 'XLTCZUSD',
      'name': 'LTC to USD',
      'currency': utils.currency['usd']
    },
    {
      'isocode': 'XXLTZEUR',
      'pair': 'XLTCZEUR',
      'name': 'LTC to EUR',
      'currency': utils.currency['eur']
    },
    {
      'isocode': 'XXETZUSD',
      'pair': 'XETHZUSD',
      'name': 'ETH to USD',
      'currency': utils.currency['usd']
    },
    {
      'isocode': 'XXETZEUR',
      'pair': 'XETHZEUR',
      'name': 'ETH to EUR',
      'currency': utils.currency['eur']
    },
    {
      'isocode': 'XXBCZEUR',
      'pair': 'BCHEUR',
      'name': 'BCH to EUR',
      'currency': utils.currency['eur']
    },
    {
      'isocode': 'XXRPZEUR',
      'pair': 'XXRPZEUR',
      'name': 'XRP to EUR',
      'currency': utils.currency['eur']
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

    label = currency + utils.decimal_round(asset['c'][0])

    bid = utils.category['bid'] + currency + utils.decimal_round(asset['b'][0])
    high = utils.category['high'] + currency + utils.decimal_round(asset['h'][0])
    low = utils.category['low'] + currency + utils.decimal_round(asset['l'][0])
    ask = utils.category['ask'] + currency + utils.decimal_round(asset['a'][0])
    vol = utils.category['volume'] + utils.decimal_round(asset['v'][0])

    GLib.idle_add(self.indicator.set_data, label, bid, high, low, ask, vol)