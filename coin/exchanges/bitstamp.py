# -*- coding: utf-8 -*-

# Bitstamp
# https://www.bitstamp.net/api/
# By Nil Gradisnik <nil.gradisnik@gmail.com>

from exchange import Exchange, CURRENCY


class Bitstamp(Exchange):
    name = "Bitstamp"
    code = "bitstamp"

    CONFIG = {
        'name': 'Bitstamp',
        'ticker': 'https://www.bitstamp.net/api/v2/ticker/',
        'discovery': 'https://www.bitstamp.net/api/v2/trading-pairs-info/',
        'asset_pairs': [
            {
                'isocode': 'XXBTZUSD',
                'pair': 'XXBTZUSD',
                'name': 'BTC to USD',
                'currency': CURRENCY['usd']
            }
        ]
    }

    def get_discovery_url(self):
        return self.config.get('discovery')

    def _parse_discovery(self, result):
        asset_pairs = []
        for asset in result:
            basequote = asset.get('name').split('/')
            base = basequote[0]
            quote = basequote[1]

            asset_pair = {
                'pair': asset.get('url_symbol'),
                'base': base,
                'quote': quote,
                'name': base + ' to ' + quote,
                'currency': quote.lower(),
                'volumecurrency': base
            }

            asset_pairs.append(asset_pair)

        return asset_pairs

    def _get_ticker_url(self):
        return self.config.get('ticker') + self.pair

    def _parse_ticker(self, asset):
        cur = asset.get('last')
        bid = asset.get('bid')
        ask = asset.get('ask')
        vol = asset.get('volume')
        high = asset.get('high')
        low = asset.get('low')

        return {
            'cur': cur,
            'bid': bid,
            'high': high,
            'low': low,
            'ask': ask,
            'vol': vol
        }
