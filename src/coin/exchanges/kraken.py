# Kraken
# https://www.kraken.com/help/api#public-market-data
# By Nil Gradisnik <nil.gradisnik@gmail.com>

from coin.exchange import CURRENCY, Exchange


class Kraken(Exchange):
    name = "Kraken"
    code = "kraken"

    ticker = "https://api.kraken.com/0/public/Ticker"
    discovery = "https://api.kraken.com/0/public/AssetPairs"

    default_label = "cur"

    @classmethod
    def _get_discovery_url(cls):
        return cls.discovery

    def _get_ticker_url(self):
        return self.ticker + "?pair=" + self.pair

    @staticmethod
    def _parse_discovery(result):
        asset_pairs = []
        assets = result.get("result")
        for asset in assets:
            # strange double assets in Kraken results, ignore ba
            if asset[-2:] == ".d":
                continue

            asset_data = assets.get(asset)
            # new kraken api data contains a 'wsname' property
            # which names assets a lot more consistently
            names = asset_data.get("wsname").split("/")
            base = names[0]
            quote = names[1]

            kraken_names = {"XBT": "BTC", "XZC": "ZEC"}
            if base in kraken_names:
                base = kraken_names[base]

            if quote in kraken_names:
                quote = kraken_names[quote]

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
        asset = asset.get("result").get(self.pair)

        cur = asset.get("c")[0]
        bid = asset.get("b")[0]
        high = asset.get("h")[1]
        low = asset.get("l")[1]
        ask = asset.get("a")[0]
        vol = asset.get("v")[1]

        return {
            "cur": cur,
            "bid": bid,
            "high": high,
            "low": low,
            "ask": ask,
            "vol": vol,
        }
