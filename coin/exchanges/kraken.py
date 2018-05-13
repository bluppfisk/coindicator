# -*- coding: utf-8 -*-

# Kraken
# https://www.kraken.com/help/api#public-market-data
# By Nil Gradisnik <nil.gradisnik@gmail.com>

from exchange import Exchange, CURRENCY


class Kraken(Exchange):
    name = "Kraken"
    code = "kraken"

    CONFIG = {
        'name': 'Kraken',
        'default_label': 'cur',
        'ticker': 'https://api.kraken.com/0/public/Ticker',
        'discovery': 'https://api.kraken.com/0/public/AssetPairs',
        'asset_pairs': [
            {
                'isocode': 'XXBTZUSD',
                'pair': 'XXBTZUSD',
                'name': 'BTC to USD',
                'currency': CURRENCY['usd']
            },
            {
                'isocode': 'XXBTZEUR',
                'pair': 'XXBTZEUR',
                'name': 'BTC to EUR',
                'currency': CURRENCY['eur']
            },
            {
                'isocode': 'XXLTZUSD',
                'pair': 'XLTCZUSD',
                'name': 'LTC to USD',
                'currency': CURRENCY['usd']
            },
            {
                'isocode': 'XXLTZEUR',
                'pair': 'XLTCZEUR',
                'name': 'LTC to EUR',
                'currency': CURRENCY['eur']
            },
            {
                'isocode': 'XXETZUSD',
                'pair': 'XETHZUSD',
                'name': 'ETH to USD',
                'currency': CURRENCY['usd']
            },
            {
                'isocode': 'XXETZEUR',
                'pair': 'XETHZEUR',
                'name': 'ETH to EUR',
                'currency': CURRENCY['eur']
            },
            {
                'isocode': 'XXBCZEUR',
                'pair': 'BCHEUR',
                'name': 'BCH to EUR',
                'currency': CURRENCY['eur']
            },
            {
                'isocode': 'XXRPZEUR',
                'pair': 'XXRPZEUR',
                'name': 'XRP to EUR',
                'currency': CURRENCY['eur']
            }
        ]
    }

    def get_discovery_url(self):
        return self.config.get('discovery')

    def _get_ticker_url(self):
        return self.config.get('ticker') + '?pair=' + self.pair

    def _parse_discovery(self, result):
        asset_pairs = []
        assets = result.get('result')
        for asset in assets:
            # strange double assets in Kraken results, ignore ba
            if asset[-2:] == ".d":
                continue

            asset_data = assets.get(asset)
            base = asset_data.get('base')[-3:]
            quote = asset_data.get('quote')[-3:]

            kraken_names = {'XBT': 'BTC', 'XZC': 'ZEC'}
            if base in kraken_names:
                base = kraken_names[base]

            if quote in kraken_names:
                quote = kraken_names[quote]

            asset_pair = {
                'pair': asset,
                'base': base,
                'quote': quote,
                'name': base + ' to ' + quote,
                'currency': quote.lower(),
                'volumecurrency': base
            }

            asset_pairs.append(asset_pair)

        return asset_pairs

    def _parse_ticker(self, asset):
        asset = asset.get('result').get(self.pair)

        cur = asset.get('c')[0]
        bid = asset.get('b')[0]
        high = asset.get('h')[1]
        low = asset.get('l')[1]
        ask = asset.get('a')[0]
        vol = asset.get('v')[1]

        return {
            'cur': cur,
            'bid': bid,
            'high': high,
            'low': low,
            'ask': ask,
            'vol': vol
        }
