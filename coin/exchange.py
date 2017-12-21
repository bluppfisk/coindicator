from gi.repository import GLib
import logging, requests, time
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
    'bid': 'Bid',
    'high': 'High',
    'low': 'Low',
    'ask': 'Ask',
    'volume': 'Vol',
    'first': 'First'
}

class Exchange(object):
  def __init__(self, indicator):
    self.latest_response = 0
    self.indicator = indicator
    self.timeout_id = None
    self.error = Error(self)
    self.config = self.CONFIG
    self.exchange_name = self.config['name']

  def get_ticker(self): # to be overwritten by child class
    pass

  def _parse_result(self, data): # to be overwritten by child class
    pass

  def start(self, error_refresh=None):
    refresh = error_refresh if error_refresh else self.indicator.refresh_frequency
    self.timeout_id = GLib.timeout_add_seconds(refresh, self.check_price)

  def stop(self):
    self.error.clear()
    if self.timeout_id is not None:
        GLib.source_remove(self.timeout_id)

  def check_price(self):
    self.asset_pair = self.indicator.active_asset_pair
    self.pair = [item['pair'] for item in self.config['asset_pairs'] if item['isocode'] == self.asset_pair][0]
    self.async_get(self.get_ticker(), validation=self.asset_pair, callback=self._handle_result)

    return self.error.is_ok() # continues the timer if there are no errors

  def _handle_error(self, error):
    self.error.increment()
    logging.info(self.exchange_name + " API error: " + str(error))

  def _handle_result(self, data, validation, timestamp):
    # Check to see if the returning response is still valid
    # (user may have changed exchanges before the request finished)
    if validation is not self.asset_pair: # we've already moved on.
      return

    # also check if a newer response hasn't already been returned
    if timestamp < self.latest_response: # this is an older request
      logging.warning('Discarding outdated response.')
      return

    if data.status_code != 200:
      self._handle_error('Server returned an error: ' + str(data.status_code))
      return

    else:
      try:
        asset = data.json()
      except Exception as e:
        # Usually a KeyError happens when an asynchronous response comes in
        # for a previously selected asset pair (see upstream issue #27)
        self._handle_error('Invalid response for ' + str(self.pair))
        return

    self.latest_response = timestamp
    results = self._parse_result(asset)

    config = [item for item in self.config['asset_pairs'] if item['isocode'] == self.asset_pair][0]
    currency = config['currency']
    volumecurrency = config.get('volumelabel').upper() if config.get('volumelabel') else config.get('name')[0:3].upper()

    label = currency + self.decimal_auto(results.get('label'))
    bid = CATEGORY['bid'] + ':\t\t' + currency + self.decimal_auto(results.get('bid')) if results.get('bid') else None
    high = CATEGORY['high'] + ':\t\t' + currency + self.decimal_auto(results.get('high')) if results.get('high') else None
    low = CATEGORY['low'] + ':\t\t' + currency + self.decimal_auto(results.get('low')) if results.get('low') else None
    ask = CATEGORY['ask'] + ':\t\t' + currency + self.decimal_auto(results.get('ask')) if results.get('ask') else None
    vol = CATEGORY['volume'] + ' (' + volumecurrency + '):\t' + self.decimal_auto(results.get('vol')) if results.get('vol') else None
    
    GLib.idle_add(self.indicator.set_data, label, bid, high, low, ask, vol)

  ## decimal_auto 
  # Rounds a number to a meaningful number of decimal places
  # and returns it as a string
  # 
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

  ##
  # Makes request on a different thread, and optionally passes response to a
  # `callback` function when request returns.
  # 
  def async_get(self, *args, callback=None, timeout=15, validation=None, **kwargs):  
    if callback:
      def callback_with_args(response, *args, **kwargs):
        timestamp = time.time()
        callback(response, validation, timestamp)
      kwargs['hooks'] = {'response': callback_with_args}
    kwargs['timeout'] = timeout
    thread = Thread(target=self.get_with_exception, args=args, kwargs=kwargs)
    thread.start()

  def get_with_exception(self, *args, **kwargs):
    try:
        r = requests.get(*args, **kwargs)
        return r
    except requests.exceptions.RequestException as e:
        self._handle_error('Connection error')