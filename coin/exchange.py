from gi.repository import GLib
import logging, requests, time, pickle
from error import Error
from threading import Thread

CURRENCY = {
    'usd': '$',
    'eur': '€',
    'btc': 'B',
    'thb': '฿',
    'gbp': '£',
    'eth': 'Ξ',
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

  ##
  # Abstract methods to be overwritten by the child classes
  # 
  def get_discovery_url(self): pass

  def _parse_discovery(self, data): pass

  def _get_ticker_url(self): pass

  def _parse_ticker(self, data): pass

  ##
  # Getters and setters follow
  # 
  def get_name(self):
    return self.config.get('name')

  def get_code(self):
    return self.config.get('code', self.config.get('name').lower())

  def get_default_label(self):
    return self.config.get('default_label', 'cur')

  def get_currency(self):
    return self.asset_pair.get('quote').lower()

  def get_symbol(self):
    return CURRENCY.get(self.get_currency(), self.get_currency().upper())

  def get_volume_currency(self):
    return self.asset_pair.get('volumecurrency', self.asset_pair.get('base'))

  def set_asset_pair(self, base, quote):
    for ap in self.get_asset_pairs():
      if ap.get('base').upper() == base.upper() and ap.get('quote').upper() == quote.upper():
        self.asset_pair = ap

  def set_asset_pair_from_code(self, code):
    for ap in self.get_asset_pairs():
      if ap.get('pair').upper() == code.upper():
        self.asset_pair = ap

  ##
  # Legacy function to make sure the hard-coded asset
  # configuration is consistent with the new format
  # 
  def normalise_assets(self):
    for ap in self.config['asset_pairs']:
      if not ap.get('base'):
        ap['base'] = ap.get('name').split(' ')[0]
      if not ap.get('quote'):
        ap['quote'] = ap.get('name').split(' ')[2]
      if not ap.get('volumecurrency'):
        ap['volumecurrency'] = ap.get('base')

  ##
  # Loads asset pairs from the config files or,
  # failing that, from the hard-coded lines
  # 
  def get_asset_pairs(self):
    try:
      with open('./coin/exchanges/' + self.get_code() + '.conf', 'rb') as handle:
        asset_pairs = pickle.loads(handle.read())
        return asset_pairs

    except:
      # no CONF file, return predefined from config
      self.normalise_assets()
      return self.config.get('asset_pairs')

  ##
  # Saves asset pairs to disk
  # 
  def store_asset_pairs(self, asset_pairs):
    try:
      with open('./coin/exchanges/' + self.get_code() + '.conf', 'wb') as handle:
        pickle.dump(asset_pairs, handle)
    except:
      logging.error('Could not write to config file')

  ##
  # Discovers assets from the exchange's API url retrieved
  # through the instance-specific method _get_discovery_url()
  # 
  def discover_assets(self):
    self._async_get(self.get_discovery_url(), callback=self._handle_discovery_result)

  ##
  # Deals with the result from the discovery HTTP request
  # Should probably be merged with _handle_result() later
  # 
  def _handle_discovery_result(self, data, *args, **kwargs):
    if data.status_code is not 200:
      self._handle_error('API server returned an error: ' + str(data.status_code))

    try:
      result = data.json()
      asset_pairs = self._parse_discovery(result)
      self.normalise_assets()
      self.store_asset_pairs(asset_pairs)
    except Exception as e:
      self._handle_error(e)

    self.coin.update_assets() # update the asset menus of all instances

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
    if self.timeout_id:
      GLib.source_remove(self.timeout_id)

    self.started = False
    self.indicator.alarm.deactivate()
    self.error.reset()

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
    self._async_get(self._get_ticker_url(), validation=self.asset_pair, timestamp=timestamp, callback=self._handle_result)
    logging.info('Request with TS: ' + str(timestamp))
    if not self.error.is_ok():
      self.timeout_id = None
    
    return self.error.is_ok() # continues the timer if there are no errors

  def _handle_error(self, error):
    self.error.log(str(error))
    self.error.increment()

  def _handle_result(self, data, validation, timestamp):
    # Check to see if the returning response is still valid
    # (user may have changed exchanges before the request finished)
    if not self.started:
      logging.info("Discarding packet for inactive exchange")
      return

    if validation is not self.asset_pair: # we've already moved on.
      logging.info("Discarding packet for wrong asset pair or exchange")
      return

    # also check if a newer response hasn't already been returned
    if timestamp < self.indicator.latest_response: # this is an older request
      logging.info("Discarding outdated packet")
      return

    if data.status_code != 200:
      self._handle_error('API server returned an error: ' + str(data.status_code))
      return

    try:
      asset = data.json()
    except Exception as e:
      # Before, a KeyError happened when an asynchronous response comes in
      # for a previously selected asset pair (see upstream issue #27)
      self._handle_error('Invalid response for ' + str(self.pair))
      return

    results = self._parse_ticker(asset)
    self.indicator.latest_response = timestamp
    logging.info('Requests comes in with timestamp ' + str(timestamp) + ', last response at ' + str(self.indicator.latest_response))
    
    for item in CATEGORY:
      if results.get(item):
        self.indicator.prices[item] = self._decimal_auto(results.get(item))

    self.error.reset()
    
    GLib.idle_add(self.indicator.update_gui)

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
