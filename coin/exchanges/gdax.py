# -*- coding: utf-8 -*-

# Gdax
# https://api.gdax.com/

__author__ = "sander.vandemoortel@gmail.com"

from exchange import Exchange, CURRENCY

class Gdax(Exchange):
  CONFIG = {
    'name': 'Gdax',
    'ticker': 'https://api.gdax.com/products/',
    'asset_pairs': [
      {
        'isocode': 'XXBTZUSD',
        'pair': 'BTC-USD',
        'name': 'BTC to USD',
        'currency': CURRENCY['usd']
      },
      {
        'isocode': 'XXBTZEUR',
        'pair': 'BTC-EUR',
        'name': 'BTC to EUR',
        'currency': CURRENCY['eur']
      },
      {
        'isocode': 'XXBTZGBP',
        'pair': 'BTC-GBP',
        'name': 'BTC to GBP',
        'currency': CURRENCY['gbp']
      },
      {
        'isocode': 'XXETZUSD',
        'pair': 'ETH-USD',
        'name': 'ETH to USD',
        'currency': CURRENCY['usd']
      },
      {
        'isocode': 'XXETZEUR',
        'pair': 'ETH-EUR',
        'name': 'ETH to EUR',
        'currency': CURRENCY['eur']
      },
      {
        'isocode': 'XXLTZUSD',
        'pair': 'LTC-USD',
        'name': 'LTC to USD',
        'currency': CURRENCY['usd']
      },
      {
        'isocode': 'XXLTZEUR',
        'pair': 'LTC-EUR',
        'name': 'LTC to EUR',
        'currency': CURRENCY['eur']
      },
      {
        'isocode': 'XXBCZEUR',
        'pair': 'BCH-EUR',
        'name': 'BCH to EUR',
        'currency': CURRENCY['eur']
      },
      {
        'isocode': 'XXBCZUSD',
        'pair': 'BCH-USD',
        'name': 'BCH to USD',
        'currency': CURRENCY['usd']
      },
    ]
  }

  def get_ticker(self):
    return self.config['ticker'] + self.pair + '/ticker'

  def _parse_result(self, asset):
    label = asset['price']
    bid = asset['bid']
    ask = asset['ask']
    vol = asset['volume']

    return {
      'label': label,
      'bid': bid,
      'high': None,
      'low': None,
      'ask': ask,
      'vol': vol
    }