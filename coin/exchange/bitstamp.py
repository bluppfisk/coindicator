# -*- coding: utf-8 -*-

# Bitstamp
# https://www.bitstamp.net/api/

__author__ = "nil.gradisnik@gmail.com"

from gi.repository import GLib

import requests

import utils as utils
from exchange.error import Error
from alarm import Alarm

CONFIG = {
  'ticker': 'https://www.bitstamp.net/api/ticker/'
}

class Bitstamp:

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
    try:
      res = requests.get(CONFIG['ticker'])
      data = res.json()
      if data:
        self._parse_result(data)

    except Exception as e:
      print(e)
      self.error.increment()

    return self.error.is_ok()

  def _parse_result(self, data):
    self.error.clear()

    currency = utils.currency['usd']

    label = currency + utils.decimal_round(data['last'])

    bid = utils.category['bid'] + currency + utils.decimal_round(data['bid'])
    high = utils.category['high'] + currency + utils.decimal_round(data['high'])
    low = utils.category['low'] + currency + utils.decimal_round(data['low'])
    ask = utils.category['ask'] + currency + utils.decimal_round(data['ask'])
    volume = utils.category['volume'] + utils.decimal_round(data['volume'])

    # if self.alarm:
    #   self.alarm.check(float(data["last"]))

    self.indicator.set_data(label, bid, high, low, ask, volume)

  def _handle_error(self, error):
    print("Bitstamp API error: " + error[0])
