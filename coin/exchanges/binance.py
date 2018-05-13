# -*- coding: utf-8 -*-

# Binance
# https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md
# By Lari Taskula <lari@taskula.fi>

from exchange import Exchange, CURRENCY


class Binance(Exchange):
    name = "Binance"
    code = "binance"

    asset_pairs = [
        {
            'isocode': 'XXBTZUSD',
            'pair': 'BTCUSDT',
            'name': 'BTC to USD',
            'currency': CURRENCY['usd']
        }
    ]

    CONFIG = {
        'name': 'Binance',
        'ticker': 'https://www.binance.com/api/v1/ticker/24hr',
        'discovery': 'https://www.binance.com/api/v1/exchangeInfo',
        'asset_pairs': [
            {
                'isocode': 'XXBTZUSD',
                'pair': 'BTCUSDT',
                'name': 'BTC to USD',
                'currency': CURRENCY['usd']
            }
        ]
    }

    def get_discovery_url(self):
        return self.config.get('discovery')

    def _parse_discovery(self, result):
        asset_pairs = []
        assets = result.get('symbols')
        for asset in assets:
            base = asset.get('baseAsset')
            quote = asset.get('quoteAsset')

            names = {'XZC': 'ZEC', 'BCC': 'BCH', 'IOTA': 'IOT'}
            if base in names:
                base = names[base]

            if quote in names:
                quote = names[quote]

            asset_pair = {
                'pair': asset.get('symbol'),
                'base': base,
                'quote': quote,
                'name': base + ' to ' + quote,
                'currency': quote.lower(),
                'volumecurrency': base
            }

            asset_pairs.append(asset_pair)

        return asset_pairs

    def _get_ticker_url(self):
        return self.config['ticker'] + '?symbol=' + self.pair

    def _parse_ticker(self, asset):
        cur = asset.get('lastPrice')
        bid = asset.get('bidPrice')
        high = asset.get('highPrice')
        low = asset.get('lowPrice')
        ask = asset.get('askPrice')
        vol = asset.get('volume')

        return {
            'cur': cur,
            'bid': bid,
            'high': high,
            'low': low,
            'ask': ask,
            'vol': vol
        }
