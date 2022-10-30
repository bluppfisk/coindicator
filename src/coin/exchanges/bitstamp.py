# Bitstamp
# https://www.bitstamp.net/api/
# By Nil Gradisnik <nil.gradisnik@gmail.com>

from coin.exchange import CURRENCY, Exchange


class Bitstamp(Exchange):
    name = "Bitstamp"
    code = "bitstamp"

    ticker = "https://www.bitstamp.net/api/v2/ticker/"
    discovery = "https://www.bitstamp.net/api/v2/trading-pairs-info/"

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
            basequote = asset.get("name").split("/")
            base = basequote[0]
            quote = basequote[1]

            asset_pair = {
                "pair": asset.get("url_symbol"),
                "base": base,
                "quote": quote,
                "name": base + " to " + quote,
                "currency": quote.lower(),
                "volumecurrency": base,
            }

            asset_pairs.append(asset_pair)

        return asset_pairs

    def _parse_ticker(self, asset):
        cur = asset.get("last")
        bid = asset.get("bid")
        ask = asset.get("ask")
        vol = asset.get("volume")
        high = asset.get("high")
        low = asset.get("low")

        return {
            "cur": cur,
            "bid": bid,
            "high": high,
            "low": low,
            "ask": ask,
            "vol": vol,
        }
