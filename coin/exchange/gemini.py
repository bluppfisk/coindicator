# -*- coding: utf-8 -*-

# Gemini
# https://docs.gemini.com/rest-api/

__author__ = "rick@anteaterllc.com"

from gi.repository import GLib

import logging
import utils

from exchange.error import Error
from exchange.exchange import Exchange

CONFIG = {
  'ticker': 'https://api.gemini.com/v1/pubticker/',
  'asset_pairs': [
    {
      'isocode': 'XXBTZUSD',
      'pair': 'btcusd',
      'name': 'BTC to USD',
      'currency': utils.currency['usd'],
      'srccurrency' : utils.currency['btc'],
      'volumelabel' : 'BTC',
      'precision' : 2
    },
    {
      'isocode': 'XXETZUSD',
      'pair': 'ethusd',
      'name': 'ETH to USD',
      'currency': utils.currency['usd'],
      'srccurrency' : utils.currency['eth'],
      'volumelabel' : 'ETH', 
      'precision' : 2
    },
    {
      'isocode': 'XXETZXBT',
      'pair': 'ethbtc',
      'name': 'ETH to BTC',
      'currency': utils.currency['btc'],
      'srccurrency' : utils.currency['eth'],
      'volumelabel' : 'ETH',
      'precision' : 8
    },

  ]
}

class Gemini(Exchange):
  pass

  def get_ticker(self):
    return self.config['ticker'] + self.pair

  def _parse_result(self, data):
    if data.status_code == 200:
      self.error.clear()
    else:
      self.error.increment()
      return
    
    asset = data.json()

    config = [item for item in CONFIG['asset_pairs'] if item['isocode'] == self.asset_pair][0]

    currency = config['currency']
    srccurrency = config['srccurrency']
    coin = config['name']
    volumelabel = config['volumelabel']
    precision = config['precision']

    label = currency + utils.decimal_round(asset['last'], precision)
    bid = utils.category['bid'] + currency + utils.decimal_round(asset['bid'], precision)
    ask = utils.category['ask'] + currency + utils.decimal_round(asset['ask'], precision)

    volume = utils.category['volume'] + srccurrency + utils.decimal_round(asset['volume'][volumelabel], 2)

    GLib.idle_add(self.indicator.set_data, label, bid, ask, volume, 'no further data')

  def _handle_error(self, error):
    logging.info("Gemini API error: " + str(error))
