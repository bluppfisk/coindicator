# Gemini
# https://docs.gemini.com/rest-api/
# By Rick Ramstetter <rick@anteaterllc.com>

from coin.exchange import CURRENCY, Exchange


class Gemini(Exchange):
    name = "Gemini"
    code = "gemini"

    ticker = "https://api.gemini.com/v1/pubticker/"
    discovery = "https://api.gemini.com/v1/symbols"

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
        volumelabel = [
            item for item in self.config["asset_pairs"] if item["pair"] == self.pair
        ][0]["volumelabel"]
        cur = asset.get("last")
        bid = asset.get("bid")
        ask = asset.get("ask")
        vol = asset.get("volume").get(volumelabel)

        return {
            "cur": cur,
            "bid": bid,
            "high": None,
            "low": None,
            "ask": ask,
            "vol": vol,
        }
