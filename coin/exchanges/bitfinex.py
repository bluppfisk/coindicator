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

    # CONFIG = {
    #     'name': 'Bitfinex',
    #     'ticker': 'https://api.bitfinex.com/v2/ticker/',
    #     'discovery': 'https://api.bitfinex.com/v1/symbols',
    #     'asset_pairs': [
    #         {'isocode': 'XAVTZUSD', 'pair': 'tAVTUSD', 'name': 'AVT to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XBATZUSD', 'pair': 'tBATUSD', 'name': 'BAT to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XBCHZUSD', 'pair': 'tBCHUSD', 'name': 'BCH to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XBTGZUSD', 'pair': 'tBTGUSD', 'name': 'BTG to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XDATZUSD', 'pair': 'tDATUSD', 'name': 'DAT to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XDSHZUSD', 'pair': 'tDSHUSD', 'name': 'DASH to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XEDOZUSD', 'pair': 'tEDOUSD', 'name': 'EDO to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XEOSZUSD', 'pair': 'tEOSUSD', 'name': 'EOS to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XETCZUSD', 'pair': 'tETCUSD', 'name': 'ETC to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XETHZUSD', 'pair': 'tETHUSD', 'name': 'ETH to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XETPZUSD', 'pair': 'tETPUSD', 'name': 'ETP to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XFUNZUSD', 'pair': 'tFUNUSD', 'name': 'FUN to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XGNTZUSD', 'pair': 'tGNTUSD', 'name': 'GNT to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XIOTZUSD', 'pair': 'tIOTUSD', 'name': 'IOT to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XLTCZUSD', 'pair': 'tLTCUSD', 'name': 'LTC to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XMNAZUSD', 'pair': 'tMNAUSD', 'name': 'MNA to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XNEOZUSD', 'pair': 'tNEOUSD', 'name': 'NEO to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XOMGZUSD', 'pair': 'tOMGUSD', 'name': 'OMG to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XQSHZUSD', 'pair': 'tQSHUSD', 'name': 'QSH to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XQTMZUSD', 'pair': 'tQTMUSD', 'name': 'QTM to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XRRTZUSD', 'pair': 'tRRTUSD', 'name': 'RRT to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XSANZUSD', 'pair': 'tSANUSD', 'name': 'SAN to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XSNTZUSD', 'pair': 'tSNTUSD', 'name': 'SNT to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XSPKZUSD', 'pair': 'tSPKUSD', 'name': 'SPK to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XTNBZUSD', 'pair': 'tTNBUSD', 'name': 'TNB to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XXBTZUSD', 'pair': 'tBTCUSD', 'name': 'BTC to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XXMRZUSD', 'pair': 'tXMRUSD', 'name': 'XMR to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XXRPZUSD', 'pair': 'tXRPUSD', 'name': 'XRP to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XYYWZUSD', 'pair': 'tYYWUSD', 'name': 'YYW to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XZECZUSD', 'pair': 'tZECUSD', 'name': 'ZEC to USD', 'currency': CURRENCY['usd']},
    #         {'isocode': 'XZRXZUSD', 'pair': 'tZRXUSD', 'name': 'ZRX to USD', 'currency': CURRENCY['usd']}
    #     ]
    # }

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
