# -*- coding: utf-8 -*-

# Bitfinex
# https://docs.bitfinex.com/

__author__ = "eliezer.aquino@gmail.com"

from gi.repository import GLib
import logging, utils
from exchange.error import Error

CONFIG = {
  'ticker': 'https://api.bitfinex.com/v1/pubticker/',
  'asset_pairs': [
    {
       'isocode': 'XXBTZUSD',
      'pair': 'btcusd',
      'name': 'BTC to USD',
      'currency': utils.currency['usd']
    },
    {
      'isocode': 'XIOTZUSD',
      'pair': 'iotusd',
      'name': 'IOTA to USD',
      'currency': utils.currency['usd']
    }
  ]
}

class Bitfinex:
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
    self.asset_pair = self.indicator.active_asset_pair
    pair = [item['pair'] for item in CONFIG['asset_pairs'] if item['isocode'] == self.asset_pair][0]    
    utils.async_get(CONFIG['ticker'] + pair, callback=self._parse_result)

    return self.error.is_ok()

  def _parse_result(self, data):
    if data.status_code == 200:
      self.error.clear()
      asset = data.json()
    else:
      self.error.increment()
      return
    
    currency = utils.currency['usd']

    label = currency + utils.decimal_round(asset['last_price'])

    bid = utils.category['bid'] + currency + utils.decimal_round(asset['bid'])
    high = utils.category['high'] + currency + utils.decimal_round(asset['high'])
    low = utils.category['low'] + currency + utils.decimal_round(asset['low'])
    ask = utils.category['ask'] + currency + utils.decimal_round(asset['ask'])
    volume = utils.category['volume'] + utils.decimal_round(asset['volume'])

    GLib.idle_add(self.indicator.set_data, label, bid, high, low, ask, volume)

  def _handle_error(self, error):
    logging.info("Bitfinex API error: " + error[0])
