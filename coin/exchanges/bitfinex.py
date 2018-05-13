# Bitfinex
# https://bitfinex.readme.io/v2/docs
# By Alessio Carrafa <ruzzico@gmail.com>

from exchange import Exchange, CURRENCY


class Bitfinex(Exchange):
    name = "Bitfinex"
    code = "bitfinex"

    ticker = "https://api.bitfinex.com/v2/ticker/"
    discovery = "https://api.bitfinex.com/v1/symbols"

    default_label = "cur"

    asset_pairs = [
        {'isocode': 'XBCHZUSD', 'pair': 'tBCHUSD', 'name': 'BCH to USD', 'currency': CURRENCY['usd']},
        {'isocode': 'XDSHZUSD', 'pair': 'tDSHUSD', 'name': 'DASH to USD', 'currency': CURRENCY['usd']},
        {'isocode': 'XEOSZUSD', 'pair': 'tEOSUSD', 'name': 'EOS to USD', 'currency': CURRENCY['usd']},
        {'isocode': 'XETCZUSD', 'pair': 'tETCUSD', 'name': 'ETC to USD', 'currency': CURRENCY['usd']},
        {'isocode': 'XETHZUSD', 'pair': 'tETHUSD', 'name': 'ETH to USD', 'currency': CURRENCY['usd']},
        {'isocode': 'XIOTZUSD', 'pair': 'tIOTUSD', 'name': 'IOT to USD', 'currency': CURRENCY['usd']},
        {'isocode': 'XLTCZUSD', 'pair': 'tLTCUSD', 'name': 'LTC to USD', 'currency': CURRENCY['usd']},
        {'isocode': 'XNEOZUSD', 'pair': 'tNEOUSD', 'name': 'NEO to USD', 'currency': CURRENCY['usd']},
        {'isocode': 'XXBTZUSD', 'pair': 'tBTCUSD', 'name': 'BTC to USD', 'currency': CURRENCY['usd']},
        {'isocode': 'XXMRZUSD', 'pair': 'tXMRUSD', 'name': 'XMR to USD', 'currency': CURRENCY['usd']},
        {'isocode': 'XXRPZUSD', 'pair': 'tXRPUSD', 'name': 'XRP to USD', 'currency': CURRENCY['usd']},
        {'isocode': 'XZECZUSD', 'pair': 'tZECUSD', 'name': 'ZEC to USD', 'currency': CURRENCY['usd']},
        {'isocode': 'XZRXZUSD', 'pair': 'tZRXUSD', 'name': 'ZRX to USD', 'currency': CURRENCY['usd']}
    ]

    @classmethod
    def _get_discovery_url(cls):
        return cls.discovery

    def _get_ticker_url(self):
        return self.ticker + self.pair

    @staticmethod
    def _parse_discovery(result):
        asset_pairs = []
        for asset in result:
            base = asset[0:3].upper()
            quote = asset[-3:].upper()

            names = {'DSH': 'DASH', 'TRST': 'TRUST', 'XZC': 'ZEC'}
            if base in names:
                base = names[base]

            if quote in names:
                quote = names[quote]

            asset_pair = {
                'pair': 't' + asset.upper(),
                'base': base,
                'quote': quote,
                'name': base + ' to ' + quote,
                'currency': quote.lower(),
                'volumecurrency': base
            }

            asset_pairs.append(asset_pair)

        return asset_pairs

    def _parse_ticker(self, asset):

        cur = asset[6]
        bid = asset[0]
        ask = asset[2]
        vol = asset[7]
        high = asset[8]
        low = asset[9]

        return {
            'cur': cur,
            'bid': bid,
            'high': high,
            'low': low,
            'ask': ask,
            'vol': vol
        }
