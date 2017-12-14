# -*- coding: utf-8 -*-

# Kraken
# https://www.kraken.com/help/api#public-market-data

__author__ = "nil.gradisnik@gmail.com"

from exchange import Exchange, CURRENCY

class Kraken(Exchange):
  CONFIG = {
    'name': 'Kraken',
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

  def get_ticker(self):
    return self.config['ticker'] + '?pair=' + self.pair

  def _parse_result(self, asset):
    asset = asset['result'][self.pair]

    label = asset['c'][0]
    bid = asset['b'][0]
    high = asset['h'][1]
    low = asset['l'][1]
    ask = asset['a'][0]
    vol = asset['v'][1]
    
    return {
      'label': label,
      'bid': bid,
      'high': high,
      'low': low,
      'ask': ask,
      'vol': vol
    }