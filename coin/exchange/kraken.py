# -*- coding: utf-8 -*-

# Kraken
# https://www.kraken.com/help/api#public-market-data

__author__ = "nil.gradisnik@gmail.com"

from gi.repository import GLib

import requests

import utils
from exchange.error import Error
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
    },
    {
      'code': 'XETHZUSD',
      'name': 'ETH to USD',
      'currency': utils.currency['usd']
    },
    {
      'code': 'XETHZEUR',
      'name': 'ETH to EUR',
      'currency': utils.currency['eur']
    },
    {
      'code': 'XXLMZUSD',
      'name': 'XLM to USD',
      'currency': utils.currency['usd']
    },
    {
      'code': 'XXLMZEUR',
      'name': 'XLM to EUR',
      'currency': utils.currency['eur']
    },
    {
      'code': 'BCHEUR',
      'name': 'BCH to EUR',
      'currency': utils.currency['eur']
    },
    {
      'code': 'XXRPZEUR',
      'name': 'XRP to EUR',
      'currency': utils.currency['eur']
    }
  ]
}

class Kraken:

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
      res = requests.get(CONFIG['ticker'] + '?pair=' + self.asset_pair)
      data = res.json()
      if data['error']:
        self._handle_error(data['error'])
      elif data['result']:
        self._parse_result(data['result'])

    except Exception as e:
      print(e)
      self.error.increment()

    return self.error.is_ok()

  def _parse_result(self, data):
    self.error.clear()

    asset = data[self.asset_pair]
    currency = [item['currency'] for item in CONFIG['asset_pairs'] if item['code'] == self.asset_pair][0]
    coin = [item['name'] for item in CONFIG['asset_pairs'] if item['code'] == self.asset_pair][0]

    label = coin[0:3] + ' = ' + currency + utils.decimal_round(asset['c'][0])

    bid = utils.category['bid'] + currency + utils.decimal_round(asset['b'][0])
    high = utils.category['high'] + currency + utils.decimal_round(asset['h'][0])
    low = utils.category['low'] + currency + utils.decimal_round(asset['l'][0])
    ask = utils.category['ask'] + currency + utils.decimal_round(asset['a'][0])

    # if self.alarm:
    #   self.alarm.check(float(data["last"]))

    self.indicator.set_data(label, bid, high, low, ask)

  def _handle_error(self, error):
    print("Kraken API error: " + error[0])
