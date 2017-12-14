# -*- coding: utf-8 -*-

# Gemini
# https://docs.gemini.com/rest-api/

__author__ = "rick@anteaterllc.com"

from exchange import Exchange, CURRENCY

class Gemini(Exchange):
  CONFIG = {
    'ticker': 'https://api.gemini.com/v1/pubticker/',
    'asset_pairs': [
      {
        'isocode': 'XXBTZUSD',
        'pair': 'btcusd',
        'name': 'BTC to USD',
        'currency': CURRENCY['usd'],
        'volumelabel' : 'BTC'
      },
      {
        'isocode': 'XXETZUSD',
        'pair': 'ethusd',
        'name': 'ETH to USD',
        'currency': CURRENCY['usd'],
        'volumelabel' : 'ETH'
      },
      {
        'isocode': 'XXETZXBT',
        'pair': 'ethbtc',
        'name': 'ETH to BTC',
        'currency': CURRENCY['btc'],
        'volumelabel' : 'ETH'
      }
    ]
  }

  def get_ticker(self):
    return self.config['ticker'] + self.pair

  def _parse_result(self, asset):
    volumelabel = [item for item in self.config['asset_pairs'] if item['pair'] == self.pair][0]['volumelabel']
    label = asset['last']
    bid = asset['bid']
    ask = asset['ask']
    vol = asset['volume'][volumelabel]

    return {
      'label': label,
      'bid': bid,
      'high': None,
      'low': None,
      'ask': ask,
      'vol': vol
    }