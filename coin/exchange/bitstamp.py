# -*- coding: utf-8 -*-

# Bitstamp
# https://www.bitstamp.net/api/

__author__ = "nil.gradisnik@gmail.com"

from gi.repository import GLib
import logging
import utils as utils
from exchange.error import Error

CONFIG = {
  'ticker': 'https://www.bitstamp.net/api/ticker/',
  'asset_pairs': [
    {
      'isocode': 'XXBTZUSD',
      'pair': 'XXBTZUSD',
      'name': 'BTC to USD',
      'currency': utils.currency['usd']
    }
  ]
}

class Bitstamp:
  def __init__(self, config, indicator):
    self.indicator = indicator
    self.timeout_id = 0
    self.error = Error(self)

  def start(self, error_refresh=None):
    refresh = error_refresh if error_refresh else self.indicator.refresh_frequency
    self.timeout_id = GLib.timeout_add_seconds(refresh, self.check_price)

  def stop(self):
    if self.timeout_id is not 0:
      GLib.source_remove(self.timeout_id)

  def check_price(self):
    utils.async_get(CONFIG['ticker'], callback=self._parse_result)
    return self.error.is_ok()

  def _parse_result(self, data):
    if data.status_code == 200:
      self.error.clear()
      asset = data.json()
    else:
      self.error.increment()
      return

    currency = utils.currency['usd']
    label = currency + utils.decimal_round(asset['last'])

    bid = utils.category['bid'] + currency + utils.decimal_round(asset['bid'])
    high = utils.category['high'] + currency + utils.decimal_round(asset['high'])
    low = utils.category['low'] + currency + utils.decimal_round(asset['low'])
    ask = utils.category['ask'] + currency + utils.decimal_round(asset['ask'])
    volume = utils.category['volume'] + utils.decimal_round(asset['volume'])

    GLib.idle_add(self.indicator.set_data, label, bid, high, low, ask, volume)

  def _handle_error(self, error):
    logging.info("Bitstamp API error: " + error[0])
