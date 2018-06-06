# Gdax
# https://api.gdax.com/
# By Sander Van de Moortel <sander.vandemoortel@gmail.com>

from exchange import WSExchange, WSSubscription, CURRENCY


class Gdax(WSExchange):
    name = "Gdax"
    code = "gdax"
    client_type = "ws"

    ticker = "https://api.gdax.com/products/"
    discovery = "https://api.gdax.com/products/"
    websocket_url = "wss://ws-feed.gdax.com"

    default_label = "cur"

    asset_pairs = [
        {'isocode': 'XXBTZUSD', 'pair': 'BTC-USD', 'name': 'BTC to USD', 'currency': CURRENCY['usd']},
        {'isocode': 'XXBTZEUR', 'pair': 'BTC-EUR', 'name': 'BTC to EUR', 'currency': CURRENCY['eur']},
        {'isocode': 'XXBTZGBP', 'pair': 'BTC-GBP', 'name': 'BTC to GBP', 'currency': CURRENCY['gbp']},
        {'isocode': 'XXETZUSD', 'pair': 'ETH-USD', 'name': 'ETH to USD', 'currency': CURRENCY['usd']},
        {'isocode': 'XXETZEUR', 'pair': 'ETH-EUR', 'name': 'ETH to EUR', 'currency': CURRENCY['eur']},
        {'isocode': 'XXLTZUSD', 'pair': 'LTC-USD', 'name': 'LTC to USD', 'currency': CURRENCY['usd']},
        {'isocode': 'XXLTZEUR', 'pair': 'LTC-EUR', 'name': 'LTC to EUR', 'currency': CURRENCY['eur']},
        {'isocode': 'XXBCZEUR', 'pair': 'BCH-EUR', 'name': 'BCH to EUR', 'currency': CURRENCY['eur']},
        {'isocode': 'XXBCZUSD', 'pair': 'BCH-USD', 'name': 'BCH to USD', 'currency': CURRENCY['usd']},
    ]

    @classmethod
    def _get_discovery_url(cls):
        return cls.discovery

    def _get_ticker_url(self):
        return self.ticker + self.pair + '/ticker'

    @staticmethod
    def _parse_discovery(result):
        asset_pairs = []
        for asset in result:
            base = asset.get('base_currency')
            quote = asset.get('quote_currency')

            asset_pair = {
                'pair': asset.get('id'),
                'base': base,
                'quote': quote,
                'name': base + ' to ' + quote,
                'currency': quote.lower(),
                'volumecurrency': base
            }

            asset_pairs.append(asset_pair)

        return asset_pairs

    @classmethod
    def get_subscription(cls, listener, pair, callback):
        sub_msg = {
            "type": "subscribe",
            "product_ids": [pair],
            "channels": ["ticker"]
        }

        unsub_msg = {**sub_msg, "type": "unsubscribe"}  # copy and modify

        return WSSubscription(
            listener=listener,
            url=cls.websocket_url,
            pair=pair,
            sub_msg=sub_msg,
            unsub_msg=unsub_msg,
            callback=callback
        )

    def _parse_ticker(self, asset):
        cur = asset.get('price')
        bid = asset.get('best_bid')
        high = asset.get('high_24h')
        low = asset.get('low_24h')
        ask = asset.get('best_ask')
        vol = asset.get('volume_24h')

        return {
            'cur': cur,
            'bid': bid,
            'high': high,
            'low': low,
            'ask': ask,
            'vol': vol
        }
