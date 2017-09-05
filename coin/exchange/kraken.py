# -*- coding: utf-8 -*-

# Kraken
# https://www.kraken.com/help/api#public-market-data

__author__ = "nil.gradisnik@gmail.com"

from gi.repository import GLib

import requests
import logging

import utils
from exchange.error import Error
from alarm import Alarm

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
      'isocode': 'XETHZUSD',
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

    self.pair = [item['pair'] for item in CONFIG['asset_pairs'] if item['isocode'] == self.asset_pair][0]

    try:
      res = requests.get(CONFIG['ticker'] + '?pair=' + self.pair)
      data = res.json()
      if data['error']:
        self._handle_error(data['error'])
      elif data['result']:
        self._parse_result(data['result'])

    except Exception as e:
      logging.info('Error: ' + str(e))
      self.error.increment()

    return self.error.is_ok()

  def _parse_result(self, data):
    self.error.clear()

    asset = data[self.pair]
    currency = [item['currency'] for item in CONFIG['asset_pairs'] if item['isocode'] == self.asset_pair][0]
    coin = [item['name'] for item in CONFIG['asset_pairs'] if item['isocode'] == self.asset_pair][0]

    label = currency + utils.decimal_round(asset['c'][0])

    bid = utils.category['bid'] + currency + utils.decimal_round(asset['b'][0])
    high = utils.category['high'] + currency + utils.decimal_round(asset['h'][0])
    low = utils.category['low'] + currency + utils.decimal_round(asset['l'][0])
    ask = utils.category['ask'] + currency + utils.decimal_round(asset['a'][0])

    self.indicator.set_data(label, bid, high, low, ask)

  def _handle_error(self, error):
    logging.info("Kraken API error: " + error[0])
