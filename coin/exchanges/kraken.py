# -*- coding: utf-8 -*-

# Kraken
# https://www.kraken.com/help/api#public-market-data

__author__ = "nil.gradisnik@gmail.com"

from exchange import Exchange, CURRENCY

class Kraken(Exchange):
  CONFIG = {
    'name': 'Kraken',
    'default_label': 'cur',
    'ticker': 'https://api.kraken.com/0/public/Ticker',
    'discovery': 'https://api.kraken.com/0/public/AssetPairs',
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

  def get_discovery_url(self):
    return self.config['discovery']

  def _parse_discovery(self, result):
    asset_pairs = []
    assets = result.get('result')
    for asset in assets:
      asset_data = assets.get(asset)
      asset_pair = {
        'isocode': asset,
        'pair': asset,
        'name': asset_data.get('base') + ' to ' + asset_data.get('quote'),
        'currency': CURRENCY[asset_data.get('quote')[-3:].lower()]
      }
      asset_pairs.append(asset_pair)
    
    self.config['asset_pairs'] = asset_pairs
    self._update_indicator_currencies()

  def get_ticker(self):
    return self.config['ticker'] + '?pair=' + self.pair

  def _parse_result(self, asset):
    asset = asset.get('result').get(self.pair)

    cur = asset.get('c')[0]
    bid = asset.get('b')[0]
    high = asset.get('h')[1]
    low = asset.get('l')[1]
    ask = asset.get('a')[0]
    vol = asset.get('v')[1]
    
    return {
      'cur': cur,
      'bid': bid,
      'high': high,
      'low': low,
      'ask': ask,
      'vol': vol
    }