from gi.repository import GLib
import logging, requests, time
from error import Error
from threading import Thread

CURRENCY = {
    'usd': '$',
    'eur': '€',
    'btc': '฿',
    'thb': '฿',
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
    self.round = True
    self.indicator = indicator
    self.timeout_id = None
    self.error = Error(self)
    self.config = self.CONFIG
    self.exchange_name = self.config['name']
    self.started = False

  def get_ticker(self): # to be overwritten by child class
    pass

  def _parse_result(self, data): # to be overwritten by child class
    pass

  # helper function for restoring normal frequency
  # False must be returned for the restart operation to be done only once
  def restart(self):
    self.start()
    return False

  def start(self, error_refresh=None):
    if not self.started:
      self._check_price()

    self.started = True
    refresh = error_refresh if error_refresh else self.indicator.refresh_frequency
    self.timeout_id = GLib.timeout_add_seconds(refresh, self._check_price)

    return self

  def stop(self):
    self.started = False
    self.error.reset()
    if self.timeout_id is not None:
        GLib.source_remove(self.timeout_id)

    return self

  def _check_price(self):
    self.asset_pair = self.indicator.active_asset_pair
    self.pair = [item.get('pair') for item in self.config.get('asset_pairs') if item.get('isocode') == self.asset_pair][0]
    timestamp = time.time()
    self._async_get(self.get_ticker(), validation=self.asset_pair, timestamp=timestamp, callback=self._handle_result)
    logging.debug('Request with TS: ' + str(timestamp))
    return self.error.is_ok() # continues the timer if there are no errors

  def _handle_error(self, error):
    self.error.log(str(error))
    self.error.increment()

  def _handle_result(self, data, validation, timestamp):
    # Check to see if the returning response is still valid
    # (user may have changed exchanges before the request finished)
    if validation is not self.indicator.active_asset_pair: # we've already moved on.
      logging.debug("Discarding packet for wrong exchange")
      return

    # also check if a newer response hasn't already been returned
    if timestamp < self.indicator.latest_response: # this is an older request
      logging.debug("Discarding outdated packet")
      return

    if data.status_code != 200:
      self._handle_error('API server returned an error: ' + str(data.status_code))
      return

    else:
      try:
        asset = data.json()
      except Exception as e:
        # Before, a KeyError happened when an asynchronous response comes in
        # for a previously selected asset pair (see upstream issue #27)
        self._handle_error('Invalid response for ' + str(self.pair))
        return

    results = self._parse_result(asset)
    self.indicator.latest_response = timestamp
    logging.debug('Requests comes in with timestamp ' + str(timestamp) + ', last response at ' + str(self.indicator.latest_response))
    
    self.indicator.current = self._decimal_auto(results.get('cur')) if results.get('cur') else None
    self.indicator.bid = self._decimal_auto(results.get('bid')) if results.get('bid') else None
    self.indicator.high = self._decimal_auto(results.get('high')) if results.get('high') else None
    self.indicator.low = self._decimal_auto(results.get('low')) if results.get('high') else None
    self.indicator.ask = self._decimal_auto(results.get('ask')) if results.get('ask') else None
    self.indicator.volume = self._decimal_auto(results.get('vol')) if results.get('vol') else None

    config = [item for item in self.config.get('asset_pairs') if item.get('isocode') == self.asset_pair][0]
    self.indicator.volumecurrency = config.get('volumelabel').upper() if config.get('volumelabel') else config.get('name').split(' ')[0].upper()
    self.indicator.currency = config['currency']

    self.error.reset()
    
    GLib.idle_add(self.indicator.update_gui)

  ## _decimal_auto 
  # Rounds a number to a meaningful number of decimal places
  # and returns it as a string
  # 
  def _decimal_auto(self, number):
    if self.round is False:
    	return str(number)
    else:
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
  def _async_get(self, *args, callback=None, timeout=5, validation=None, timestamp=None, **kwargs):  
    if callback:
      def _callback_with_args(response, *args, **kwargs):
        callback(response, validation, timestamp)
      kwargs['hooks'] = {'response': _callback_with_args}
    kwargs['timeout'] = timeout
    thread = Thread(target=self._get_with_exception, args=args, kwargs=kwargs)
    thread.start()

  def _get_with_exception(self, *args, **kwargs):
    try:
        r = requests.get(*args, **kwargs) # probably should do error code handling here
        return r
    except requests.exceptions.RequestException as e:
        self._handle_error('Connection error')
