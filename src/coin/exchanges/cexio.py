# CEX.io
# https://cex.io/rest-api
# By Sander Van de Moortel <sander.vandemoortel@gmail.com>

from coin.exchange import Exchange


class Cexio(Exchange):
    name = "CEX.io"
    code = "cexio"

    ticker = "https://cex.io/api/ticker"
    discovery = "https://cex.io/api/currency_limits"

    default_label = "cur"

    @classmethod
    def _get_discovery_url(cls):
        return cls.discovery

    def _get_ticker_url(self):
        return self.ticker + "/" + self.pair  # base/quote

    @staticmethod
    def _parse_discovery(result):
        asset_pairs = []
        data = result.get("data")
        for asset in data.get("pairs"):
            base = asset.get("symbol1")
            quote = asset.get("symbol2")

            asset_pair = {
                "pair": base + "/" + quote,
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
