# -*- coding: utf-8 -*-

# Bitfinex
# https://bitfinex.readme.io/v2/docs

__author__ = "ruzzico@gmail.com"

from exchange import Exchange, CURRENCY

class Bitfinex(Exchange):
  CONFIG = {
    'name': 'Bitfinex',
    'ticker': 'https://api.bitfinex.com/v2/ticker/',
    'asset_pairs': [
      { 'isocode': 'XAVTZUSD', 'pair': 'tAVTUSD', 'name': 'AVT to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XBATZUSD', 'pair': 'tBATUSD', 'name': 'BAT to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XBCHZUSD', 'pair': 'tBCHUSD', 'name': 'BCH to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XBTGZUSD', 'pair': 'tBTGUSD', 'name': 'BTG to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XDATZUSD', 'pair': 'tDATUSD', 'name': 'DAT to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XDSHZUSD', 'pair': 'tDSHUSD', 'name': 'DSH to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XEDOZUSD', 'pair': 'tEDOUSD', 'name': 'EDO to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XEOSZUSD', 'pair': 'tEOSUSD', 'name': 'EOS to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XETCZUSD', 'pair': 'tETCUSD', 'name': 'ETC to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XETHZUSD', 'pair': 'tETHUSD', 'name': 'ETH to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XETPZUSD', 'pair': 'tETPUSD', 'name': 'ETP to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XFUNZUSD', 'pair': 'tFUNUSD', 'name': 'FUN to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XGNTZUSD', 'pair': 'tGNTUSD', 'name': 'GNT to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XIOTZUSD', 'pair': 'tIOTUSD', 'name': 'IOT to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XLTCZUSD', 'pair': 'tLTCUSD', 'name': 'LTC to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XMNAZUSD', 'pair': 'tMNAUSD', 'name': 'MNA to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XNEOZUSD', 'pair': 'tNEOUSD', 'name': 'NEO to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XOMGZUSD', 'pair': 'tOMGUSD', 'name': 'OMG to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XQSHZUSD', 'pair': 'tQSHUSD', 'name': 'QSH to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XQTMZUSD', 'pair': 'tQTMUSD', 'name': 'QTM to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XRRTZUSD', 'pair': 'tRRTUSD', 'name': 'RRT to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XSANZUSD', 'pair': 'tSANUSD', 'name': 'SAN to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XSNTZUSD', 'pair': 'tSNTUSD', 'name': 'SNT to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XSPKZUSD', 'pair': 'tSPKUSD', 'name': 'SPK to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XTNBZUSD', 'pair': 'tTNBUSD', 'name': 'TNB to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XXBTZUSD', 'pair': 'tBTCUSD', 'name': 'BTC to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XXMRZUSD', 'pair': 'tXMRUSD', 'name': 'XMR to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XXRPZUSD', 'pair': 'tXRPUSD', 'name': 'XRP to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XYYWZUSD', 'pair': 'tYYWUSD', 'name': 'YYW to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XZECZUSD', 'pair': 'tZECUSD', 'name': 'ZEC to USD', 'currency': CURRENCY['usd'] },
      { 'isocode': 'XZRXZUSD', 'pair': 'tZRXUSD', 'name': 'ZRX to USD', 'currency': CURRENCY['usd'] }
    ]
  }

  def get_ticker(self):
    return self.config['ticker'] + self.pair

  def _parse_result(self, asset):

    label = asset[6]
    bid = asset[0]
    ask = asset[2]
    vol = asset[7]
    high = asset[8]
    low = asset[9]

    return {
      'label': label,
      'bid': bid,
      'high': high,
      'low': low,
      'ask': ask,
      'vol': vol
    }