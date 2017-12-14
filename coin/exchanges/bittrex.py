# -*- coding: utf-8 -*-

# Bittrex
# https://bittrex.com/Home/Api
# 
'''
Response example
[{'Bid': 5655.15, 'MarketName': 'USDT-BTC', 'Ask': 5665.0, 'BaseVolume': 19499585.87469274, 'High': 5888.0, 'Low': 5648.0, 'Volume': 3393.61801172, 'OpenBuyOrders': 8505, 'Created': '2015-12-11T06:31:40.633', 'PrevDay': 5762.180121, 'Last': 5665.0, 'OpenSellOrders': 4194, 'TimeStamp': '2017-10-28T12:24:39.38'}]
'''

__author__ = "wizzard94@github.com"

from exchange import Exchange, CURRENCY

class Bittrex(Exchange):
  CONFIG = {
    'name': 'Bittrex',
    'ticker': 'https://bittrex.com/api/v1.1/public/getmarketsummary',
    'asset_pairs': [
      {
        'isocode': 'XXBTZUSD',
        'pair': 'USDT-BTC',
        'name': 'BTC to USD',
        'currency': CURRENCY['usd']
      },
      {
        'isocode': 'XXLTZUSD',
        'pair': 'USDT-LTC',
        'name': 'LTC to USD',
        'currency': CURRENCY['usd']
      },
      {
        'isocode': 'XXETZUSD',
        'pair': 'USDT-ETH',
        'name': 'ETH to USD',
        'currency': CURRENCY['usd']
      },
      {
        'isocode': 'XXBCZBTC',
        'pair': 'BTC-BCC',
        'name': 'BCC to BTC',
        'currency': CURRENCY['btc']
      },
      {
        'isocode': 'XXETZBTC',
        'pair': 'BTC-ETH',
        'name': 'ETH to BTC',
        'currency': CURRENCY['btc']
      },
      {
        'isocode': 'XXRPZBTC',
        'pair': 'BTC-XRP',
        'name': 'XRP to BTC',
        'currency': CURRENCY['btc']
      },
      {
        'isocode': 'XXMRZBTC',
        'pair': 'BTC-XMR',
        'name': 'XMR to BTC',
        'currency': CURRENCY['btc']
      }
    ]
  }

  def get_ticker(self):
    return self.config['ticker'] + '?market=' + self.pair

  def _parse_result(self, asset):
    asset = asset['result'][0]

    label = asset['Last']
    bid = asset['Bid']
    high = asset['High']
    low = asset['Low']
    ask = asset['Ask']
    vol = None

    return {
      'label': label,
      'bid': bid,
      'high': high,
      'low': low,
      'ask': ask,
      'vol': vol
    }