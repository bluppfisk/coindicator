# -*- coding: utf-8 -*-

# Bitfinex
# https://docs.bitfinex.com/

__author__ = "eliezer.aquino@gmail.com"

from exchange import Exchange, CURRENCY


class Bitfinex(Exchange):
  CONFIG = {
    'name': 'Bitfinex',
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

  def get_ticker(self):
    return self.config['ticker'] + self.pair

  def _parse_result(self, asset):
    label = asset['last_price']
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