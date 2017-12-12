# -*- coding: utf-8 -*-

# Gemini
# https://docs.gemini.com/rest-api/

__author__ = "rick@anteaterllc.com"

from gi.repository import GLib

import grequests
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
      'srccurrency' : utils.currency['btc'],
      'volumelabel' : 'BTC',
      'precision' : 2
    },
    {
      'isocode': 'XXETZUSD',
      'pair': 'ethusd',
      'name': 'ETH to USD',
      'currency': utils.currency['usd'],
      'srccurrency' : utils.currency['eth'],
      'volumelabel' : 'ETH', 
      'precision' : 2
    },
    {
      'isocode': 'XXETZXBT',
      'pair': 'ethbtc',
      'name': 'ETH to BTC',
      'currency': utils.currency['btc'],
      'srccurrency' : utils.currency['eth'],
      'volumelabel' : 'ETH',
      'precision' : 8
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

    self.config = [i for i in CONFIG['asset_pairs'] if i['isocode'] == self.asset_pair][0]
    pair = self.config['pair']

    res = grequests.get(CONFIG['ticker'] + pair, callback=self.tester)
    responses = grequests.map([res])
    # print(responses[0].text)


    # try:
    #   res = requests.get(CONFIG['ticker'] + pair)
    #   data = res.json()
    #   if res.status_code != 200:
    #     self._handle_error('HTTP error code ' + res.status_code)
    #   else:
    #     self._parse_result(data, config)

    # except Exception as e:
    #   self._handle_error(e)
    #   self.error.increment()

    # return self.error.is_ok()
  
  def tester(self, data, *args, **kwargs):
    # config = {'srccurrency': '฿', 'isocode': 'XXBTZUSD', 'precision': 2, 'currency': '$', 'volumelabel': 'BTC', 'pair': 'btcusd', 'name': 'BTC to USD'}
    if data.status_code == 200:
      asset = data.json()
      self._parse_result(asset, self.config)
    else:
      print(data.status_code)

  def _parse_result(self, asset, config):
    self.error.clear()

    currency = config['currency']
    srccurrency = config['srccurrency']
    coin = config['name']
    volumelabel = config['volumelabel']
    precision = config['precision']

    label = currency + utils.decimal_round(asset['last'], precision)
    bid = utils.category['bid'] + currency + utils.decimal_round(asset['bid'], precision)
    ask = utils.category['ask'] + currency + utils.decimal_round(asset['ask'], precision)

    volume = utils.category['volume'] + srccurrency + utils.decimal_round(asset['volume'][volumelabel], 2)

    self.indicator.set_data(label, bid, ask, volume, 'no further data')

  def _handle_error(self, error):
    logging.info("Gemini API error: " + str(error))
