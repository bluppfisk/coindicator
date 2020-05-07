# Gdax
# https://api.gdax.com/
# By Sander Van de Moortel <sander.vandemoortel@gmail.com>

from exchange import Exchange, CURRENCY


class Gdax(Exchange):
    name = "Gdax"
    code = "gdax"

    ticker = "https://api.gdax.com/products/"
    discovery = "https://api.gdax.com/products/"

    default_label = "cur"

    @classmethod
    def _get_discovery_url(cls):
        return cls.discovery

    def _get_ticker_url(self):
        return self.ticker + self.pair + '/ticker'

    @staticmethod
    def _parse_discovery(result):
        asset_pairs = []
        for asset in result:
            base = asset.get('base_currency')
            quote = asset.get('quote_currency')

            asset_pair = {
                'pair': asset.get('id'),
                'base': base,
                'quote': quote,
                'name': base + ' to ' + quote,
                'currency': quote.lower(),
                'volumecurrency': base
            }

            asset_pairs.append(asset_pair)

        return asset_pairs

    def _parse_ticker(self, asset):
        cur = asset.get('price')
        bid = asset.get('bid')
        ask = asset.get('ask')
        vol = asset.get('volume')

        return {
            'cur': cur,
            'bid': bid,
            'high': None,
            'low': None,
            'ask': ask,
            'vol': vol
        }
