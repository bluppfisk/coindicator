# Unocoin
# https://www.unocoin.com/how-it-works?info=tickerapi
# By Sander Van de Moortel <sander.vandemoortel@gmail.com>

from coin.exchange import CURRENCY, Exchange


class Unocoin(Exchange):
    name = "Unocoin"
    code = "unocoin"

    ticker = "https://api.unocoin.com/api/trades/{}/all"
    discovery = "https://api.unocoin.com/api/trades/all/all"

    default_label = "avg"

    @classmethod
    def _get_discovery_url(cls):
        return cls.discovery

    def _get_ticker_url(self):
        return self.ticker.format(self.asset_pair.get("base").lower())

    @staticmethod
    def _parse_discovery(result):
        asset_pairs = []
        for asset in result:
            base = asset
            quote = "INR"

            asset_pair = {
                "pair": base + quote,
                "base": base,
                "quote": quote,
                "name": base + " to " + quote,
                "currency": quote.lower(),
                "volumecurrency": base,
            }

            asset_pairs.append(asset_pair)

        return asset_pairs

    def _parse_ticker(self, asset):
        avg = asset.get("average_price")
        bid = asset.get("buying_price")
        ask = asset.get("selling_price")

        return {"avg": avg, "bid": bid, "ask": ask}
