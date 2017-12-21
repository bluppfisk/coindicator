# -*- coding: utf-8 -*-

# Bitstamp
# https://www.bitstamp.net/api/

__author__ = "nil.gradisnik@gmail.com"

from exchange import Exchange, CURRENCY

class Bitstamp(Exchange):
  CONFIG = {
    'name': 'Bitstamp',
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

  def get_ticker(self):
    return self.config['ticker']

  def _parse_result(self, asset):
    label = asset.get('last')
    bid = asset.get('bid')
    ask = asset.get('ask')
    vol = asset.get('volume')
    high = asset.get('high')
    low = asset.get('low')

    return {
      'label': label,
      'bid': bid,
      'high': high,
      'low': low,
      'ask': ask,
      'vol': vol
    }