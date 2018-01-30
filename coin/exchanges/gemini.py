# -*- coding: utf-8 -*-

# Gemini
# https://docs.gemini.com/rest-api/
# By Rick Ramstetter <rick@anteaterllc.com>

from exchange import Exchange, CURRENCY

class Gemini(Exchange):
  CONFIG = {
    'name': 'Gemini',
    'ticker': 'https://api.gemini.com/v1/pubticker/',
    'discovery': 'https://api.gemini.com/v1/symbols',
    'asset_pairs': [
      {
        'isocode': 'XXBTZUSD',
        'pair': 'btcusd',
        'name': 'BTC to USD',
        'currency': CURRENCY['usd'],
        'volumelabel': 'BTC'
      },
      {
        'isocode': 'XXETZUSD',
        'pair': 'ethusd',
        'name': 'ETH to USD',
        'currency': CURRENCY['usd'],
        'volumelabel': 'ETH'
      },
      {
        'isocode': 'XXETZXBT',
        'pair': 'ethbtc',
        'name': 'ETH to BTC',
        'currency': CURRENCY['btc'],
        'volumelabel': 'ETH'
      }
    ]
  }

  def get_discovery_url(self):
    return self.config.get('discovery')

  def _parse_discovery(self, result):
    asset_pairs = []
    for asset in result:
      base = asset[0:3].upper()
      quote = asset[-3:].upper()

      asset_pair = {
        'pair': asset,
        'base': base,
        'quote': quote,
        'name': base + ' to ' + quote,
        'currency': quote.lower(),
        'volumecurrency': base
      }

      asset_pairs.append(asset_pair)

    return asset_pairs

  def get_ticker(self):
    return self.config['ticker'] + self.pair

  def _parse_result(self, asset):
    volumelabel = [item for item in self.config['asset_pairs'] if item['pair'] == self.pair][0]['volumelabel']
    cur = asset.get('last')
    bid = asset.get('bid')
    ask = asset.get('ask')
    vol = asset.get('volume').get(volumelabel)

    return {
      'cur': cur,
      'bid': bid,
      'high': None,
      'low': None,
      'ask': ask,
      'vol': vol
    }