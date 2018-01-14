# -*- coding: utf-8 -*-

# Utils
# 
from threading import Thread
import logging, requests

__author__ = "nil.gradisnik@gmail.com"

currency = {
    'usd': '$',
    'eur': '€',
    'gbp': '£',
    'eth': 'Ξ',
    'btc': 'B',
    'thb': '฿'
}

category = {
    'bid': 'Bid:\t\t',
    'high': 'High:\t\t',
    'low': 'Low:\t\t',
    'ask': 'Ask:\t\t',
    'volume': 'Volume:\t',
    'first': 'First:\t\t'
}

def decimal_round(number, decimals=2):
    result = round(number, decimals)
    return result

def decimal_auto(number):
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

def async_get(*args, callback=None, timeout=15, **kwargs):
    """Makes request on a different thread, and optionally passes response to a
    `callback` function when request returns.
    """
    if callback:
        def callback_with_args(response, *args, **kwargs):
            callback(response)
        kwargs['hooks'] = {'response': callback_with_args}
    kwargs['timeout'] = timeout
    thread = Thread(target=get_with_exception, args=args, kwargs=kwargs)
    thread.start()

def get_with_exception(*args, **kwargs):
    try:
        r = requests.get(*args, **kwargs)
        return r
    except requests.exceptions.RequestException as e:
        logging.info('API request failed, probably just timed out')