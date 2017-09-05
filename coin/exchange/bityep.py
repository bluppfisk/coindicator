# -*- coding: utf-8 -*-

# BitYep
# https://bityep.com/api/1/ticker

__author__ = "sander.vandemoortel@gmail.com"

from gi.repository import GLib

import requests
import logging

import utils
from exchange.error import Error
from alarm import Alarm

CONFIG = {
  'ticker': 'https://bityep.com/api/1/ticker',
  'asset_pairs': [
    {
      'isocode': 'XXBTZUSD',
      'pair': '0',
      'name': 'BTC to USD',
      'currency': utils.currency['usd']
    },
    {
      'isocode': 'XXDAZXBT',
      'pair': '1',
      'name': 'DASH to BTC',
      'currency': utils.currency['btc']
    }
  ]
}

class BitYep:
  def __init__(self, config, indicator):
    self.indicator = indicator

    self.timeout_id = 0
    self.alarm = Alarm(config['app']['name'])

    self.error = Error(self)

  def start(self, error_refresh=None):
    refresh = error_refresh if error_refresh else self.indicator.refresh_frequency
    self.timeout_id = GLib.timeout_add_seconds(refresh, self.check_price)

  def stop(self):
    if self.timeout_id:
      GLib.source_remove(self.timeout_id)

  def check_price(self):
    self.asset_pair = self.indicator.active_asset_pair

    try:
      res = requests.get(CONFIG['ticker'])
      data = res.json()
      if res.status_code != 200:
        self._handle_error('HTTP error code ' + res.status_code)
      else:
        self._parse_result(data)

    except Exception as e:
      self._handle_error(e)
      self.error.increment()

    return self.error.is_ok()

  def _parse_result(self, data):
    self.error.clear()

    asset = data[int([item['pair'] for item in CONFIG['asset_pairs'] if item['isocode'] == self.asset_pair][0])]
    currency = [item['currency'] for item in CONFIG['asset_pairs'] if item['isocode'] == self.asset_pair][0]
    coin = [item['name'] for item in CONFIG['asset_pairs'] if item['isocode'] == self.asset_pair][0]

    label = currency + utils.decimal_round(asset['last'])

    first = utils.category['first'] + currency + utils.decimal_round(asset['first'])
    high = utils.category['high'] + currency + utils.decimal_round(asset['high'])
    low = utils.category['low'] + currency + utils.decimal_round(asset['low'])
    volume = utils.category['volume'] + asset['volume']

    self.indicator.set_data(label, first, high, low, volume)

  def _handle_error(self, error):
    logging.info("BitYep API error: " + str(error))
