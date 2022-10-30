# Poloniex
# https://poloniex.com/public?command=returnTicker
# By Sander Van de Moortel <sander.vandemoortel@gmail.com>

from coin.exchange import Exchange


class Poloniex(Exchange):
    name = "Poloniex"
    code = "poloniex"

    ticker = "https://poloniex.com/public?command=returnTicker"
    discovery = "https://poloniex.com/public?command=returnTicker"

    default_label = "cur"

    @classmethod
    def _get_discovery_url(cls):
        return cls.discovery

    def _get_ticker_url(self):
        return self.ticker

    @staticmethod
    def _parse_discovery(result):
        asset_pairs = []
        for asset in result:
            asset_data = asset.split("_")
            base = asset_data[0]
            quote = asset_data[1]

            asset_pair = {
                "pair": asset,
                "base": base,
                "quote": quote,
                "name": base + " to " + quote,
                "currency": quote.lower(),
                "volumecurrency": base,
            }

            asset_pairs.append(asset_pair)

        return asset_pairs

    def _parse_ticker(self, asset):
        asset = asset.get(self.pair)

        cur = asset.get("last")
        bid = asset.get("highestBid")
        high = asset.get("high24hr")
        low = asset.get("low24hr")
        ask = asset.get("lowestAsk")
        vol = asset.get("quoteVolume")

        return {
            "cur": cur,
            "bid": bid,
            "high": high,
            "low": low,
            "ask": ask,
            "vol": vol,
        }
