# -*- coding: utf-8 -*-

# Utils

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

def decimal_auto(number):
    if(number < 1):
        return decimal_round(number, 2)
    else:
        return decimal_round(number, 5)

def decimal_round(number, decimals=2):
    return str(round(float(number), decimals))
