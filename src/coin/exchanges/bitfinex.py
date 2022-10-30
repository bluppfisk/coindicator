# Bitfinex
# https://bitfinex.readme.io/v2/docs
# By Alessio Carrafa <ruzzico@gmail.com>

from coin.exchange import CURRENCY, Exchange


class Bitfinex(Exchange):
    name = "Bitfinex"
    code = "bitfinex"

    ticker = "https://api.bitfinex.com/v2/ticker/"
    discovery = "https://api.bitfinex.com/v1/symbols"

    default_label = "cur"

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

            names = {"DSH": "DASH", "TRST": "TRUST", "XZC": "ZEC"}
            if base in names:
                base = names[base]

            if quote in names:
                quote = names[quote]

            asset_pair = {
                "pair": "t" + asset.upper(),
                "base": base,
                "quote": quote,
                "name": base + " to " + quote,
                "currency": quote.lower(),
                "volumecurrency": base,
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
            "cur": cur,
            "bid": bid,
            "high": high,
            "low": low,
            "ask": ask,
            "vol": vol,
        }
