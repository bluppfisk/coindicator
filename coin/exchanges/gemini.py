# -*- coding: utf-8 -*-

# Gemini
# https://docs.gemini.com/rest-api/

__author__ = "rick@anteaterllc.com"

from gi.repository import GLib
import logging
from error import Error
from exchange import Exchange, CURRENCY, CATEGORY


CONFIG = {
  'ticker': 'https://api.gemini.com/v1/pubticker/',
  'asset_pairs': [
    {
      'isocode': 'XXBTZUSD',
      'pair': 'btcusd',
      'name': 'BTC to USD',
      'currency': CURRENCY['usd'],
      'srccurrency' : CURRENCY['btc'],
      'volumelabel' : 'BTC'
    },
    {
      'isocode': 'XXETZUSD',
      'pair': 'ethusd',
      'name': 'ETH to USD',
      'currency': CURRENCY['usd'],
      'srccurrency' : CURRENCY['eth'],
      'volumelabel' : 'ETH'
    },
    {
      'isocode': 'XXETZXBT',
      'pair': 'ethbtc',
      'name': 'ETH to BTC',
      'currency': CURRENCY['btc'],
      'srccurrency' : CURRENCY['eth'],
      'volumelabel' : 'ETH'
    }
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

    label = currency + self.decimal_auto(asset['last'])
    bid = CATEGORY['bid'] + currency + self.decimal_auto(asset['bid'])
    ask = CATEGORY['ask'] + currency + self.decimal_auto(asset['ask'])

    volume = CATEGORY['volume'] + srccurrency + self.decimal_auto(asset['volume'][volumelabel])

    GLib.idle_add(self.indicator.set_data, label, bid, ask, volume, 'no further data')