# -*- coding: utf-8 -*-

# Gemini
# https://docs.gemini.com/rest-api/

__author__ = "rick@anteaterllc.com"

from gi.repository import GLib

import requests
import logging

import utils
from exchange.error import Error
from alarm import Alarm

CONFIG = {
  'ticker': 'https://api.gemini.com/v1/pubticker/',
  'asset_pairs': [
    {
      'isocode': 'XXBTZUSD',
      'pair': 'btcusd',
      'name': 'BTC to USD',
      'currency': utils.currency['usd'],
      'volumelabel' : 'USD'
    },
    {
      'isocode': 'XXETZUSD',
      'pair': 'ethusd',
      'name': 'ETH to USD',
      'currency': utils.currency['usd'],
       'volumelabel' : 'USD'
    },
    {
      'isocode': 'XXETZBT',
      'pair': 'ethbtc',
      'name': 'ETH to BTC',
      'currency': utils.currency['btc'],
      'volumelabel' : 'BTC'
    },

  ]
}

class Gemini:
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
      res = requests.get(CONFIG['ticker'] + pair)
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
 
    item = [i for i in CONFIG['asset_pairs'] if i['isocode'] == self.asset_pair][0]
    currency = item['currency']
    coin = item['name']

    label = currency + utils.decimal_round(asset['last'])

    bid = utils.category['bid'] + currency + utils.decimal_round(asset['bid'])
    ask = utils.category['ask'] + currency + utils.decimal_round(asset['ask'])
    volume = utils.category['volume'] + currency + utils.decimal_round(asset['volume'][ item['volumelabel'] ])

    self.indicator.set_data(label, bid, ask, volume, 'no further data')

  def _handle_error(self, error):
    logging.info("Gemini API error: " + str(error))
