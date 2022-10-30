# HitBTC
# https://github.com/hitbtc-com/hitbtc-api/blob/master/APIv1.md
# By Sander Van de Moortel <sander.vandemoortel@gmail.com>

from coin.exchange import CURRENCY, Exchange


class Hitbtc(Exchange):
    name = "HitBTC"
    code = "hitbtc"

    ticker = "https://api.hitbtc.com/api/1/public/"
    discovery = "http://api.hitbtc.com/api/1/public/symbols"

    default_label = "cur"

    @classmethod
    def _get_discovery_url(cls):
        return cls.discovery

    def _get_ticker_url(self):
        return self.ticker + self.pair + "/ticker"

    @staticmethod
    def _parse_discovery(result):
        asset_pairs = []
        assets = result.get("symbols")
        for asset in assets:
            base = asset.get("commodity")
            quote = asset.get("currency")

            names = {"IOTA": "IOT", "MAN": "MANA"}
            if base in names:
                base = names[base]

            if quote in names:
                quote = names[quote]

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
