# Bittrex
# https://bittrex.com/Home/Api
# By "Sir Paul" <wizzard94@github.com>

from coin.exchange import Exchange


class Bittrex(Exchange):
    name = "Bittrex"
    code = "bittrex"

    ticker = "https://api.bittrex.com/v3/markets/{}/ticker"
    discovery = "https://api.bittrex.com/v3/markets"

    default_label = "ask"

    @classmethod
    def _get_discovery_url(cls):
        return cls.discovery

    def _get_ticker_url(self):
        return self.ticker.format(self.pair)

    @staticmethod
    def _parse_discovery(result):
        asset_pairs = []
        for asset in result:
            base = asset.get("baseCurrencySymbol")
            quote = asset.get("quoteCurrencySymbol")
            market = asset.get("symbol")

            names = {
                "SWIFT": "SWFTC",
                "DSH": "DASH",
                "TRST": "TRUST",
                "XZC": "ZEC",
                "GAM": "GAME",
                "BCC": "BCH",
            }
            if base in names:
                base = names[base]

            if quote in names:
                quote = names[quote]

            asset_pair = {
                "pair": market,
                "base": base,
                "quote": quote,
                "name": base + " to " + quote,
                "currency": quote.lower(),
                "volumecurrency": base,
            }

            asset_pairs.append(asset_pair)

        return asset_pairs

    def _parse_ticker(self, asset):
        # Bittrex moved last, high, low and volume to a separate API
        # endpoint in v3. Coinprice-indicator currently does not support
        # aggregating data from multiple endpoints

        # cur = asset.get("Last")
        bid = asset.get("bidRate")
        # high = asset.get("High")
        # low = asset.get("Low")
        ask = asset.get("askRate")
        # vol = None

        return {
            # "cur": cur,
            "bid": bid,
            # "high": high,
            # "low": low,
            "ask": ask,
            # "vol": vol,
        }
