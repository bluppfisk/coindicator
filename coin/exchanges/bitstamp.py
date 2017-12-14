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
    label = asset['last']
    bid = asset['bid']
    ask = asset['ask']
    vol = asset['volume']
    high = asset['high']
    low = asset['low']

    return {
      'label': label,
      'bid': bid,
      'high': high,
      'low': low,
      'ask': ask,
      'vol': vol
    }