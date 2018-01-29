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
    'eth': 'Ξ',
    'xbt': '฿',
    'cad': '$',
    'jpy': '¥'
}

CATEGORY = {
    'cur': 'Now',
    'bid': 'Bid',
    'high': 'High',
    'low': 'Low',
    'ask': 'Ask',
    'vol': 'Vol',
    'first': 'First'
}

class Exchange(object):
  def __init__(self, indicator=None, coin=None):
    self.indicator = indicator
    self.coin = coin
    self.timeout_id = None
    self.error = Error(self)
    self.config = self.CONFIG
    self.exchange_name = self.config.get('name')
    self.started = False

    self.normalise_assets()

  def normalise_assets(self):
    for ap in self.config['asset_pairs']:
      if not ap.get('base'):
        ap['base'] = ap.get('name').split(' ')[0]
      if not ap.get('quote'):
        ap['quote'] = ap.get('name').split(' ')[2]
      if not ap.get('volumecurrency'):
        ap['volumecurrency'] = ap.get('base')

  def get_name(self):
    return self.config.get('name')

  def get_code(self):
    return self.config.get('code', self.config.get('name').capitalize())

  def get_default_label(self):
    return self.config.get('default_label', 'cur')

  def get_currency(self):
    return self.asset_pair.get('currency')

  def get_volume_currency(self):
    return self.asset_pair.get('volumecurrency', self.asset_pair.get('base'))

  def get_ticker(self): # to be overwritten by child class
    pass

  def set_asset_pair(self, base, quote):
    for ap in self.config.get('asset_pairs'):
      if ap.get('base') == base and ap.get('quote') == quote:
        self.asset_pair = ap

  def set_asset_pair_from_isocode(self, isocode):
    for ap in self.config.get('asset_pairs'):
      if ap.get('isocode') == isocode:
        self.asset_pair = ap

  def discover_assets(self):
    self._async_get(self.get_discovery_url(), callback=self._handle_discovery_result)
    
  def get_discovery_url(self): # to be overwritten by child class
    pass

  def _handle_discovery_result(self, data, *args, **kwargs):
    if data.status_code is not 200:
      self._handle_error('API server returned an error: ' + str(data.status_code))

    result = data.json()
    asset_pairs = self._parse_discovery(result)
    self.config['asset_pairs'] = asset_pairs
    self.normalise_assets()

    GLib.idle_add(self.coin.update_assets) # update the asset menus of all instances

  def _parse_discovery(self, data): # to be overwritten by child class
    pass

  ##
  # Start exchange
  # 
  def start(self, error_refresh=None):
    if not self.started:
      self._check_price()

    self.started = True
    refresh = error_refresh if error_refresh else self.indicator.refresh_frequency
    self.timeout_id = GLib.timeout_add_seconds(refresh, self._check_price)

    return self

  ##
  # Stop exchange, resets errors
  # 
  def stop(self):
    self.started = False
    self.error.reset()
    if self.timeout_id is not None:
        GLib.source_remove(self.timeout_id)

    return self

  ##
  # Restarts the exchange. This is necessary for restoring normal frequency as
  # False must be returned for the restart operation to be done only once
  # 
  def restart(self):
    self.start()
    return False

  ##
  # This function is called frequently to get price updates from the API
  # 
  def _check_price(self):
    self.pair = self.asset_pair.get('pair')
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
    if validation is not self.asset_pair: # we've already moved on.
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
    
    for item in CATEGORY:
      if results.get(item):
        self.indicator.prices[item] = self._decimal_auto(results.get(item))

    self.error.reset()
    
    GLib.idle_add(self.indicator.update_gui)

  def _parse_result(self, data): # to be overwritten by child class
    pass

  ##
  # Rounds a number to a meaningful number of decimal places
  # and returns it as a string
  # 
  def _decimal_auto(self, number):
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
