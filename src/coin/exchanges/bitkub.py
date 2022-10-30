# Bitkub
# https://github.com/bitkub/bitkub-official-api-docs/blob/master/restful-api.md
# By Theppasith N. <tutorgaming@gmail.com>

from coin.exchange import CURRENCY, Exchange


class Bitkub(Exchange):
    name = "Bitkub"
    code = "bitkub"

    ticker = "https://api.bitkub.com/api/market/ticker"
    discovery = "https://api.bitkub.com/api/market/symbols"

    default_label = "cur"

    @classmethod
    def _get_discovery_url(cls):
        return cls.discovery

    def _get_ticker_url(self):
        return self.ticker + "?sym=" + self.pair

    @staticmethod
    def _parse_discovery(result):
        asset_pairs = []
        # Bitkub provide fetching result in error field
        success = result.get("error") == 0
        if not success:
            return []
        assets = result.get("result")

        # Iterate through all symbols
        for asset in assets:
            symbol = asset.get("symbol")
            split_sym = str(symbol).strip().split("_")
            base = split_sym[1]
            quote = split_sym[0]

            asset_pair = {
                "pair": symbol,
                "base": base,
                "quote": quote,
                "name": asset.get("info"),
                "currency": quote.lower(),
                "volumecurrency": base,
            }
            asset_pairs.append(asset_pair)

        return asset_pairs

    def _parse_ticker(self, asset):
        data = asset[next(iter(asset))]
        cur = data.get("last")
        bid = data.get("highestBid")
        high = data.get("high24hr")
        low = data.get("low24hr")
        ask = data.get("lowestAsk")
        vol = data.get("baseVolume")

        return {
            "cur": cur,
            "bid": bid,
            "high": high,
            "low": low,
            "ask": ask,
            "vol": vol,
        }
