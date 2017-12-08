# -*- coding: utf-8 -*-

# Bitfinex
# hhttps://docs.bitfinex.com/

__author__ = "eliezer.aquino@gmail.com"

from gi.repository import GLib

import requests
import logging

import utils as utils
from exchange.error import Error
from alarm import Alarm

CONFIG = {
  'ticker': 'https://api.bitfinex.com/v1/pubticker/',
  'asset_pairs': [
    {
       'isocode': 'XXBTZUSD',
      'pair': 'btcusd',
      'name': 'BTC to USD',
      'currency': utils.currency['usd']
    }
  ]
}

class Bitfinex:

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

    config = CONFIG['asset_pairs'][0]
    pair = config['pair']
    
    try:
      res = requests.get(CONFIG['ticker'] + pair)
      data = res.json()
      
      

      if data:
        self._parse_result(data)

    except Exception as e:
      logging.info(e)
      self.error.increment()

    return self.error.is_ok()

  def _parse_result(self, data):
    self.error.clear()
    currency = utils.currency['usd']

    

    label = currency + utils.decimal_round(data['last_price'])

    bid = utils.category['bid'] + currency + utils.decimal_round(data['bid'])
    high = utils.category['high'] + currency + utils.decimal_round(data['high'])
    low = utils.category['low'] + currency + utils.decimal_round(data['low'])
    ask = utils.category['ask'] + currency + utils.decimal_round(data['ask'])
    volume = utils.category['volume'] + utils.decimal_round(data['volume'])

    # if self.alarm:
    #   self.alarm.check(float(data["last"]))

    self.indicator.set_data(label, bid, high, low, ask, volume)

  def _handle_error(self, error):
    logging.info("Bitfinex API error: " + error[0])
