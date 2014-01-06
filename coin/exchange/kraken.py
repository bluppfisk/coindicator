# -*- coding: utf-8 -*-

# Kraken
# https://www.kraken.com/help/api#public-market-data

__author__ = "nil.gradisnik@gmail.com"

from gi.repository import GObject

import requests

import utils
from alarm import Alarm

CONFIG = {
  'ticker': 'https://api.kraken.com/0/public/Ticker',
  'asset_pairs': [
    {
      'code': 'XXBTZUSD',
      'name': 'BTC to USD',
      'currency': utils.currency['usd']
    },
    {
      'code': 'XXBTZEUR',
      'name': 'BTC to EUR',
      'currency': utils.currency['eur']
    },
    {
      'code': 'XLTCZUSD',
      'name': 'LTC to USD',
      'currency': utils.currency['usd']
    },
    {
      'code': 'XLTCZEUR',
      'name': 'LTC to EUR',
      'currency': utils.currency['eur']
    }
  ]
}

class Kraken:

  def __init__(self, config, indicator):
    self.indicator = indicator

    self.timeout_id = 0
    self.currency = 'euro'
    self.alarm = Alarm(config['app']['name'])

  def start(self):
    self.refresh_frequency = self.indicator.refresh_frequency
    self.asset_pair = self.indicator.active_asset_pair

    self._check_price()
    self.timeout_id = GObject.timeout_add(self.refresh_frequency * 1000, self._check_price)

  def stop(self):
    if self.timeout_id:
      GObject.source_remove(self.timeout_id)

  def _check_price(self):
    try:
      res = requests.get(CONFIG['ticker'] + '?pair=' + self.asset_pair)
      data = res.json()

      if data['error']:
        self._handle_error(data['error'])
      elif data['result']:
        self._parse_result(data['result'])

    except Exception as e:
      print(e)

  def _parse_result(self, data):
    asset = data[self.asset_pair]
    currency = [item['currency'] for item in CONFIG['asset_pairs'] if item['code'] == self.asset_pair][0]

    label = currency + utils.decimal_round(asset['c'][0])

    bid = utils.category['bid'] + currency + utils.decimal_round(asset['b'][0])
    high = utils.category['high'] + currency + utils.decimal_round(asset['h'][0])
    low = utils.category['low'] + currency + utils.decimal_round(asset['l'][0])
    ask = utils.category['ask'] + currency + utils.decimal_round(asset['a'][0])

    # if self.alarm:
    #   self.alarm.check(float(data["last"]))

    self.indicator.set_data(label, bid, high, low, ask)

  def _handle_error(self, error):
    print("Kraken API error: " + error[0])
