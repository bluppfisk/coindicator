# OKCoin
# https://cex.io/rest-api
# By Sander Van de Moortel <sander.vandemoortel@gmail.com>

from coin.exchange import CURRENCY, Exchange


class Okcoin(Exchange):
    name = "OKCoin"
    code = "okcoin"

    ticker = "https://www.okcoin.cn/api/v1/ticker.do"
    discovery = False  # no discovery here

    default_label = "cur"

    @classmethod
    def _get_discovery_url(cls):
        return None

    def _get_ticker_url(self):
        return self.ticker + "?symbol=" + self.pair  # base/quote

    @staticmethod
    def _parse_discovery(result):
        return [
            {"pair": "btc_cny", "name": "BTC to CNY", "currency": CURRENCY["cny"]},
            {"pair": "ltc_cny", "name": "LTC to CNY", "currency": CURRENCY["cny"]},
            {"pair": "eth_cny", "name": "ETH to CNY", "currency": CURRENCY["cny"]},
        ]

    def _parse_ticker(self, asset):
        asset = asset.get("ticker")

        cur = asset.get("last")
        bid = asset.get("buy")
        high = asset.get("high")
        low = asset.get("low")
        ask = asset.get("sell")
        vol = asset.get("volume")

        return {
            "cur": cur,
            "bid": bid,
            "high": high,
            "low": low,
            "ask": ask,
            "vol": vol,
        }
