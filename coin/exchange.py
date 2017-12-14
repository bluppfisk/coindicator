from gi.repository import GLib
import logging, requests
from error import Error
from threading import Thread

CURRENCY = {
    'usd': '$',
    'eur': '€',
    'btc': '฿',
    'gbp': '£',
    'eth': 'Ξ'
}

CATEGORY = {
    'bid': 'Bid:\t\t',
    'high': 'High:\t\t',
    'low': 'Low:\t\t',
    'ask': 'Ask:\t\t',
    'volume': 'Volume:\t',
    'first': 'First:\t\t'
}

class Exchange(object):
  def __init__(self, config, indicator):
    self.indicator = indicator
    self.timeout_id = 0
    self.error = Error(self)
    self.config = config

  def get_ticker(self): # to be overwritten by child classes
    pass

  def _parse_result(self, data): # to be overwritten by child classes
    pass

  def start(self, error_refresh=None):
    refresh = error_refresh if error_refresh else self.indicator.refresh_frequency
    self.timeout_id = GLib.timeout_add_seconds(refresh, self.check_price)

  def stop(self):
    if self.timeout_id is not 0:
        GLib.source_remove(self.timeout_id)

  def check_price(self):
    self.asset_pair = self.indicator.active_asset_pair
    self.pair = [item['pair'] for item in self.config['asset_pairs'] if item['isocode'] == self.asset_pair][0]
    self.async_get(self.get_ticker(), callback=self._parse_result)
    return self.error.is_ok()

  def _handle_error(self, error):
    logging.info("API error: " + error[0])

  def decimal_round(self, number, decimals=2):
      result = round(number, decimals)
      return result

  def decimal_auto(self, number):
      number = float(number)
      if number < 10:
          for i in range(8, 0, -1):
              if number < 10**-i:
                  break
      elif number >= 100:
          i = -2
      elif number >= 10:
          i = -1

      return ('{0:.' + str(i + 2) + 'f}').format(number)

  def async_get(self, *args, callback=None, timeout=15, **kwargs):
      """Makes request on a different thread, and optionally passes response to a
      `callback` function when request returns.
      """
      if callback:
          def callback_with_args(response, *args, **kwargs):
              callback(response)
          kwargs['hooks'] = {'response': callback_with_args}
      kwargs['timeout'] = timeout
      thread = Thread(target=self.get_with_exception, args=args, kwargs=kwargs)
      thread.start()

  def get_with_exception(self, *args, **kwargs):
      try:
          r = requests.get(*args, **kwargs)
          return r
      except requests.exceptions.RequestException as e:
          logging.info('API request failed, probably just timed out')
          self.error.increment()