# -*- coding: utf-8 -*-

# Gdax
# https://api.gdax.com/

__author__ = "sander.vandemoortel@gmail.com"

from gi.repository import GLib

import requests
import logging

import utils
from exchange.error import Error
from alarm import Alarm

CONFIG = {
  'ticker': 'https://api.gdax.com/products/',
  'asset_pairs': [
    {
      'isocode': 'XXBTZUSD',
      'pair': 'BTC-USD',
      'name': 'BTC to USD',
      'currency': utils.currency['usd']
    },
    {
      'isocode': 'XXBTZEUR',
      'pair': 'BTC-EUR',
      'name': 'BTC to EUR',
      'currency': utils.currency['eur']
    },
    {
      'isocode': 'XXBTZGBP',
      'pair': 'BTC-GBP',
      'name': 'BTC to GBP',
      'currency': utils.currency['gbp']
    },
    {
      'isocode': 'XXETZUSD',
      'pair': 'ETH-USD',
      'name': 'ETH to USD',
      'currency': utils.currency['usd']
    },
    {
      'isocode': 'XXETZEUR',
      'pair': 'ETH-EUR',
      'name': 'ETH to EUR',
      'currency': utils.currency['eur']
    },
    {
      'isocode': 'XXLTZUSD',
      'pair': 'LTC-USD',
      'name': 'LTC to USD',
      'currency': utils.currency['usd']
    },
    {
      'isocode': 'XXLTZEUR',
      'pair': 'LTC-EUR',
      'name': 'LTC to EUR',
      'currency': utils.currency['eur']
    }
  ]
}

class Gdax:
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

    pair = [item['pair'] for item in CONFIG['asset_pairs'] if item['isocode'] == self.asset_pair][0]

    try:
      res = requests.get(CONFIG['ticker'] + pair + '/ticker')
      data = res.json()
      if res.status_code != 200:
        self._handle_error('HTTP error code ' + res.status_code)
      else:
        self._parse_result(data)

    except Exception as e:
      self._handle_error(e)
      self.error.increment()

    return self.error.is_ok()

  def _parse_result(self, asset):
    self.error.clear()

    currency = [item['currency'] for item in CONFIG['asset_pairs'] if item['isocode'] == self.asset_pair][0]
    coin = [item['name'] for item in CONFIG['asset_pairs'] if item['isocode'] == self.asset_pair][0]

    label = currency + utils.decimal_round(asset['price'])

    bid = utils.category['bid'] + currency + utils.decimal_round(asset['bid'])
    ask = utils.category['ask'] + currency + utils.decimal_round(asset['ask'])
    volume = utils.category['volume'] + utils.decimal_round(asset['volume'])

    self.indicator.set_data(label, bid, ask, volume, 'no further data')

  def _handle_error(self, error):
    logging.info("Gdax API error: " + str(error))
