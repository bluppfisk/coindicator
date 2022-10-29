# MXC
# https://mxcdevelop.github.io/APIDoc/
# By Giorgos Karapiperidis <gkarapiperidis@gmail.com>

from exchange import Exchange


class Mxc(Exchange):
    name = "MXC"
    code = "mxc"

    ticker = "https://www.mxc.com/open/api/v2/market/ticker"
    discovery = "https://www.mxc.com/open/api/v2/market/symbols"

    default_label = "cur"

    @classmethod
    def _get_discovery_url(cls):
        return cls.discovery

    def _get_ticker_url(self):
        return self.ticker + "?symbol=" + self.pair

    @staticmethod
    def _parse_discovery(result):
        asset_pairs = []
        assets = result.get("data")
        for asset in assets:
            basequote = asset.get("symbol").split("_")
            base = basequote[0]
            quote = basequote[1]

            asset_pair = {
                "pair": asset.get("symbol"),
                "base": base,
                "quote": quote,
                "name": base + " to " + quote,
                "currency": quote.lower(),
                "volumecurrency": base,
            }

            asset_pairs.append(asset_pair)

        return asset_pairs

    def _parse_ticker(self, asset):
        asset = asset.get("data")[0]

        cur = asset.get("last")
        bid = asset.get("bid")
        high = asset.get("high")
        low = asset.get("low")
        ask = asset.get("ask")
        vol = asset.get("volume")

        return {
            "cur": cur,
            "bid": bid,
            "high": high,
            "low": low,
            "ask": ask,
            "vol": vol,
        }
