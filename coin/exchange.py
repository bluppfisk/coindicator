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
  def __init__(self, indicator):
    self.indicator = indicator
    self.timeout_id = 0
    self.error = Error(self)
    self.config = self.CONFIG

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
    self.async_get(self.get_ticker(), callback=self._handle_result)
    return self.error.is_ok()

  def _handle_error(self, error):
    self.error.increment()
    logging.info("API error: " + str(error))

  def _handle_result(self, data):
    if data.status_code != 200:
      self._handle_error('No result from server')
      return

    else:
      self.error.clear()
      try:
        asset = data.json()
      except Exception as e:
        # Usually a KeyError happens when an asynchronous response comes in
        # for a previously selected asset pair (see upstream issue #27)
        self._handle_error('invalid response for ' + str(self.pair))
        return

    results = self._parse_result(asset)
    config = [item for item in self.config['asset_pairs'] if item['isocode'] == self.asset_pair][0]
    currency = config['currency']
    coin = config['name']

    label = currency + self.decimal_auto(results.get('label'))
    bid = CATEGORY['bid'] + currency + self.decimal_auto(results.get('bid'))
    high = CATEGORY['high'] + currency + self.decimal_auto(results.get('high'))
    low = CATEGORY['low'] + currency + self.decimal_auto(results.get('low'))
    ask = CATEGORY['ask'] + currency + self.decimal_auto(results.get('ask'))
    vol = CATEGORY['volume'] + self.decimal_auto(results.get('vol'))
    
    GLib.idle_add(self.indicator.set_data, label, bid, high, low, ask, vol)

  def decimal_round(self, number, decimals=2):
    result = round(number, decimals)
    return result

  def decimal_auto(self, number):
    if number == None:
      return 'No data'
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
        self._handle_error('API request failed, probably just timed out')