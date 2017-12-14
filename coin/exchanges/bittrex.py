# -*- coding: utf-8 -*-

# Bittrex
# https://bittrex.com/Home/Api
# 
'''
Response example
[{'Bid': 5655.15, 'MarketName': 'USDT-BTC', 'Ask': 5665.0, 'BaseVolume': 19499585.87469274, 'High': 5888.0, 'Low': 5648.0, 'Volume': 3393.61801172, 'OpenBuyOrders': 8505, 'Created': '2015-12-11T06:31:40.633', 'PrevDay': 5762.180121, 'Last': 5665.0, 'OpenSellOrders': 4194, 'TimeStamp': '2017-10-28T12:24:39.38'}]
'''

__author__ = "wizzard94@github.com"

from gi.repository import GLib
import logging
from error import Error
from exchange import Exchange, CURRENCY, CATEGORY


CONFIG = {
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

class Bittrex(Exchange):
  pass

  def get_ticker(self):
    return self.config['ticker'] + '?market=' + self.pair

  def _parse_result(self, data):
    if data.status_code == 200:
      self.error.clear()
      asset = data.json()['result'][0]
    else:
      self.error.increment()
      return

    config = [item for item in CONFIG['asset_pairs'] if item['isocode'] == self.asset_pair][0]
    currency = config['currency']
    coin = config['name']

    label = currency + self.decimal_auto(asset['Last'])

    bid = CATEGORY['bid'] + currency + self.decimal_auto(asset['Bid'])
    high = CATEGORY['high'] + currency + self.decimal_auto(asset['High'])
    low = CATEGORY['low'] + currency + self.decimal_auto(asset['Low'])
    ask = CATEGORY['ask'] + currency + self.decimal_auto(asset['Ask'])

    GLib.idle_add(self.indicator.set_data, label, bid, high, low, ask)