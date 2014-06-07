# -*- coding: utf-8 -*-

# MtGox
# https://en.bitcoin.it/wiki/MtGox/API/HTTP/v2

# Legacy code

__author__ = "nil.gradisnik@gmail.com"

from gi.repository import GLib

import requests

import utils
from exchange.error import Error
from alarm import Alarm

CONFIG = {
  'ticker': 'http://data.mtgox.com/api/2/',
  'ticker_suffix': '/money/ticker',
  'asset_pairs': [
    {
      'code': 'BTCUSD',
      'name': 'BTC to USD'
    },
    {
      'code': 'BTCEUR',
      'name': 'BTC to EUR'
    }
  ]
}

class MtGox:

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
      res = requests.get(CONFIG['ticker'] + self.asset_pair + CONFIG['ticker_suffix'])
      data = res.json()
      if data:
        self._parse_result(data['data'])

    except Exception as e:
      print(e)
      self.error.increment()

    return self.error.is_ok()

  def _parse_result(self, data):
    self.error.clear()

    label = data['last']['display_short']

    bid = utils.category['bid'] + data['buy']['display_short']
    high = utils.category['high'] + data['high']['display_short']
    low = utils.category['low'] + data['low']['display_short']
    ask = utils.category['ask'] + data['sell']['display_short']
    volume = utils.category['volume'] + data['vol']['display_short']

    # if self.alarm:
    #   self.alarm.check(float(data["last"]))

    self.indicator.set_data(label, bid, high, low, ask, volume)

  def _handle_error(self, error):
    print("MtGox API error: " + error[0])
