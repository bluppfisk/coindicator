# Bittrex
# https://bittrex.com/Home/Api
# By "Sir Paul" <wizzard94@github.com>
'''
Response example
[{'Bid': 5655.15, 'MarketName': 'USDT-BTC', 'Ask': 5665.0, 'BaseVolume': 19499585.87469274, 'High': 5888.0, 'Low': 5648.0, 'Volume': 3393.61801172, 'OpenBuyOrders': 8505, 'Created': '2015-12-11T06:31:40.633', 'PrevDay': 5762.180121, 'Last': 5665.0, 'OpenSellOrders': 4194, 'TimeStamp': '2017-10-28T12:24:39.38'}]
'''

from exchange import Exchange, CURRENCY


class Bittrex(Exchange):
    name = "Bittrex"
    code = "bittrex"

    ticker = "https://bittrex.com/api/v1.1/public/getmarketsummary"
    discovery = "https://bittrex.com/api/v1.1/public/getmarkets"

    default_label = "cur"

    @classmethod
    def _get_discovery_url(cls):
        return cls.discovery

    def _get_ticker_url(self):
        return self.ticker + '?market=' + self.pair

    @staticmethod
    def _parse_discovery(result):
        asset_pairs = []
        assets = result.get('result')
        for asset in assets:
            base = asset.get('MarketCurrency')
            quote = asset.get('BaseCurrency')

            names = {'SWIFT': 'SWFTC', 'DSH': 'DASH', 'TRST': 'TRUST',
                     'XZC': 'ZEC', 'GAM': 'GAME', 'BCC': 'BCH'}
            if base in names:
                base = names[base]

            if quote in names:
                quote = names[quote]

            asset_pair = {
                'pair': asset.get('MarketName'),
                'base': base,
                'quote': quote,
                'name': base + ' to ' + quote,
                'currency': quote.lower(),
                'volumecurrency': base
            }

            asset_pairs.append(asset_pair)

        return asset_pairs

    def _parse_ticker(self, asset):
        asset = asset['result'][0]

        cur = asset.get('Last')
        bid = asset.get('Bid')
        high = asset.get('High')
        low = asset.get('Low')
        ask = asset.get('Ask')
        vol = None

        return {
            'cur': cur,
            'bid': bid,
            'high': high,
            'low': low,
            'ask': ask,
            'vol': vol
        }
