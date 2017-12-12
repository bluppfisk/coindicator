# -*- coding: utf-8 -*-

# Utils
# 
from threading import Thread
import requests

__author__ = "nil.gradisnik@gmail.com"

currency = {
    'usd': '$',
    'eur': '€',
    'btc': '฿',
    'gbp': '£',
    'eth': 'Ξ'
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
    return str(round(float(number), decimals))

def decimal_auto(number):
    if(number < 1):
        return decimal_round(number, 5)
    else:
        return decimal_round(number, 2)

def async_get(*args, callback=None, timeout=15, **kwargs):
    """Makes request on a different thread, and optionally passes response to a
    `callback` function when request returns.
    """
    if callback:
        def callback_with_args(response, *args, **kwargs):
            callback(response)
        kwargs['hooks'] = {'response': callback_with_args}
    kwargs['timeout'] = timeout
    thread = Thread(target=requests.get, args=args, kwargs=kwargs)
    thread.start()