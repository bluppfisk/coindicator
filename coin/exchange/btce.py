# -*- coding: utf-8 -*-

# BtcE
# https://btc-e.com/api/documentation

__author__ = "nil.gradisnik@gmail.com"

from gi.repository import GLib

import requests

import utils
from exchange.error import Error
from alarm import Alarm

CONFIG = {
  'ticker': 'https://btc-e.com/api/2/',
  'ticker_suffix': '/ticker',
  'asset_pairs': [
    {
      'code': 'btc_usd',
      'name': 'BTC to USD',
      'currency': utils.currency['usd']
    },
    {
      'code': 'btc_eur',
      'name': 'BTC to EUR',
      'currency': utils.currency['eur']
    },
    {
      'code': 'ltc_usd',
      'name': 'LTC to USD',
      'currency': utils.currency['usd']
    },
    {
      'code': 'ltc_eur',
      'name': 'LTC to EUR',
      'currency': utils.currency['eur']
    }
  ]
}

class BtcE:

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
        self._parse_result(data['ticker'])

    except Exception as e:
      print(e)
      self.error.increment()

    return self.error.is_ok()

  def _parse_result(self, data):
    self.error.clear()

    # currency = CONFIG['asset_pairs'][0]['currency']
    currency = [item['currency'] for item in CONFIG['asset_pairs'] if item['code'] == self.asset_pair][0]
    coin = [item['name'] for item in CONFIG['asset_pairs'] if item['code'] == self.asset_pair][0]

    label = coin[0:3] + ' = ' + currency + utils.decimal_round(data['last'])

    bid = utils.category['bid'] + currency + utils.decimal_round(data['buy'])
    high = utils.category['high'] + currency + utils.decimal_round(data['high'])
    low = utils.category['low'] + currency + utils.decimal_round(data['low'])
    ask = utils.category['ask'] + currency + utils.decimal_round(data['sell'])
    volume = utils.category['volume'] + utils.decimal_round(data['vol'])

    # if self.alarm:
    #   self.alarm.check(float(data["last"]))

    self.indicator.set_data(label, bid, high, low, ask, volume)

  def _handle_error(self, error):
    print("BtcE API error: " + error[0])
