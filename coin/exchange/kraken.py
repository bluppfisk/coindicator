# -*- coding: utf-8 -*-

# Kraken
# https://www.kraken.com/help/api#public-market-data

__author__ = "nil.gradisnik@gmail.com"

from gi.repository import GLib
import logging, utils
from exchange.error import Error

CONFIG = {
  'ticker': 'https://api.kraken.com/0/public/Ticker',
  'asset_pairs': [
    {
      'isocode': 'XXBTZUSD',
      'pair': 'XXBTZUSD',
      'name': 'BTC to USD',
      'currency': utils.currency['usd']
    },
    {
      'isocode': 'XXBTZEUR',
      'pair': 'XXBTZEUR',
      'name': 'BTC to EUR',
      'currency': utils.currency['eur']
    },
    {
      'isocode': 'XXLTZUSD',
      'pair': 'XLTCZUSD',
      'name': 'LTC to USD',
      'currency': utils.currency['usd']
    },
    {
      'isocode': 'XXLTZEUR',
      'pair': 'XLTCZEUR',
      'name': 'LTC to EUR',
      'currency': utils.currency['eur']
    },
    {
      'isocode': 'XXETZUSD',
      'pair': 'XETHZUSD',
      'name': 'ETH to USD',
      'currency': utils.currency['usd']
    },
    {
      'isocode': 'XXETZEUR',
      'pair': 'XETHZEUR',
      'name': 'ETH to EUR',
      'currency': utils.currency['eur']
    },
    {
      'isocode': 'XXBCZEUR',
      'pair': 'BCHEUR',
      'name': 'BCH to EUR',
      'currency': utils.currency['eur']
    },
    {
      'isocode': 'XXRPZEUR',
      'pair': 'XXRPZEUR',
      'name': 'XRP to EUR',
      'currency': utils.currency['eur']
    }
  ]
}

class Kraken(object):
  def __init__(self, config, indicator):
    self.indicator = indicator
    self.timeout_id = 0
    self.error = Error(self)

  def start(self, error_refresh=None):
    # self.indicator.idle()
    refresh = error_refresh if error_refresh else self.indicator.refresh_frequency
    self.timeout_id = GLib.timeout_add_seconds(refresh, self.check_price)

  def stop(self):
    if self.timeout_id is not 0:
      GLib.source_remove(self.timeout_id)

  def check_price(self):
    self.asset_pair = self.indicator.active_asset_pair
    self.pair = [item['pair'] for item in CONFIG['asset_pairs'] if item['isocode'] == self.asset_pair][0]
    utils.async_get(CONFIG['ticker'] + '?pair=' + self.pair, callback=self._parse_result)

    return self.error.is_ok()

  def _parse_result(self, data):
    if data.status_code == 200:
      self.error.clear()
      asset = data.json()['result'][self.pair]
    else:
      self.error.increment()
      return

    config = [item for item in CONFIG['asset_pairs'] if item['isocode'] == self.asset_pair][0]

    currency = config['currency']
    coin = config['name']

    label = currency + utils.decimal_round(asset['c'][0])

    bid = utils.category['bid'] + currency + utils.decimal_round(asset['b'][0])
    high = utils.category['high'] + currency + utils.decimal_round(asset['h'][0])
    low = utils.category['low'] + currency + utils.decimal_round(asset['l'][0])
    ask = utils.category['ask'] + currency + utils.decimal_round(asset['a'][0])
    vol = utils.category['volume'] + utils.decimal_round(asset['v'][0])

    GLib.idle_add(self.indicator.set_data, label, bid, high, low, ask, vol)

  def _handle_error(self, error):
    logging.info("Kraken API error: " + error[0])
