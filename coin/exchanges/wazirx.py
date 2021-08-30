# Wazirx
# https://api.wazirx.com/api/v2/tickers
# By Rishabh Rawat <rishabhrawat.rishu@gmail.com>

from exchange import Exchange, CURRENCY

class Wazirx(Exchange):
    name = "Wazirx"
    code = "wazirx"

    ticker = "https://api.wazirx.com/api/v2/tickers"
    discovery = "https://api.wazirx.com/api/v2/market-status"

    default_label = "last"

    @classmethod
    def _get_discovery_url(cls):
        return cls.discovery

    def _get_ticker_url(self):
        return self.ticker + '/' + self.pair

    @staticmethod
    def _parse_discovery(result):
        asset_pairs = []
        assets = result.get('markets')
        for asset in assets:
            base = asset.get('baseMarket')
            quote = asset.get('quoteMarket')

            asset_pair = {
                'pair': base+quote,
                'base': base.upper(),
                'quote': quote.upper(),
                'name': base + ' to ' + quote,
                'currency': quote.lower(),
                'volumecurrency': base
            }

            asset_pairs.append(asset_pair)

        return asset_pairs

    def _parse_ticker(self, asset):
        asset = asset.get('ticker')
        cur = asset.get('last')
        bid = asset.get('buy')
        high = asset.get('high')
        low = asset.get('low')
        ask = asset.get('sell')
        vol = asset.get('vol')

        return {
            'cur': cur,
            'bid': bid,
            'high': high,
            'low': low,
            'ask': ask,
            'vol': vol
        }
