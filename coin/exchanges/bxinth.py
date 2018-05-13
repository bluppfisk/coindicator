# Bx.in.th
# https://bx.in.th/api/
# By Theppasith N. <tutorgaming@gmail.com>

from exchange import Exchange, CURRENCY


class Bxinth(Exchange):
    name = "BX.in.th"
    code = "bxinth"

    ticker = "https://bx.in.th/api/"
    discovery = "https://bx.in.th/api/"

    default_label = "cur"

    asset_pairs = [
        {'isocode': 'XXBTCZTHB', 'pair': 'XXBTCZTHB', 'name': 'BTC to THB', 'volumelabel': 'BTC', 'currency': CURRENCY['thb'], 'pairing_id': 1, 'primary_currency': 'THB', 'secondary_currency': 'BTC'},
        {'isocode': 'XXETHZTHB', 'pair': 'XXETHZTHB', 'name': 'ETH to THB', 'volumelabel': 'ETH', 'currency': CURRENCY['thb'], 'pairing_id': 21, 'primary_currency': 'THB', 'secondary_currency': 'ETH'},
        {'isocode': 'XXDASZTHB', 'pair': 'XXDASZTHB', 'name': 'DASH to THB', 'volumelabel': 'DAS', 'currency': CURRENCY['thb'], 'pairing_id': 22, 'primary_currency': 'THB', 'secondary_currency': 'DAS'},
        {'isocode': 'XXREPZTHB', 'pair': 'XXREPZTHB', 'name': 'REP to THB', 'volumelabel': 'REP', 'currency': CURRENCY['thb'], 'pairing_id': 23, 'primary_currency': 'THB', 'secondary_currency': 'REP'},
        {'isocode': 'XXGNOZTHB', 'pair': 'XXGNOZTHB', 'name': 'GNO to THB', 'volumelabel': 'GNO', 'currency': CURRENCY['thb'], 'pairing_id': 24, 'primary_currency': 'THB', 'secondary_currency': 'GNO'},
        {'isocode': 'XXRPZTHB', 'pair': 'XXRPZTHB', 'name': 'XRP to THB', 'volumelabel': 'XRP', 'currency': CURRENCY['thb'], 'pairing_id': 25, 'primary_currency': 'THB', 'secondary_currency': 'XRP'},
        {'isocode': 'XXOMGZTHB', 'pair': 'XXOMGZTHB', 'name': 'OMG to THB', 'volumelabel': 'OMG', 'currency': CURRENCY['thb'], 'pairing_id': 26, 'primary_currency': 'THB', 'secondary_currency': 'OMG'},
        {'isocode': 'XXBCHZTHB', 'pair': 'XXBCHZTHB', 'name': 'BCH to THB', 'volumelabel': 'BCH', 'currency': CURRENCY['thb'], 'pairing_id': 27, 'primary_currency': 'THB', 'secondary_currency': 'BCH'},
        {'isocode': 'XXEVXZTHB', 'pair': 'XXEVXZTHB', 'name': 'EVX to THB', 'volumelabel': 'EVX', 'currency': CURRENCY['thb'], 'pairing_id': 28, 'primary_currency': 'THB', 'secondary_currency': 'EVX'},
        {'isocode': 'XXXZCZTHB', 'pair': 'XXXZCZTHB', 'name': 'XZC to THB', 'volumelabel': 'XZC', 'currency': CURRENCY['thb'], 'pairing_id': 29, 'primary_currency': 'THB', 'secondary_currency': 'XZC'},
        {'isocode': 'XXLTCZTHB', 'pair': 'XXLTCZTHB', 'name': 'LTC to THB', 'volumelabel': 'LTC', 'currency': CURRENCY['thb'], 'pairing_id': 30, 'primary_currency': 'THB', 'secondary_currency': 'LTC'}
    ]

    @classmethod
    def _get_discovery_url(cls):
        return cls.discovery

    def _get_ticker_url(self):
        return self.ticker

    @staticmethod
    def _parse_discovery(result):
        asset_pairs = []
        for asset in result:
            base = result[asset].get('secondary_currency')
            quote = result[asset].get('primary_currency')

            names = {'DAS': 'DASH', 'DOG': 'DOGE'}
            if base in names:
                base = names[base]

            if quote in names:
                quote = names[quote]

            asset_pair = {
                'pair': base + quote,
                'base': base,
                'quote': quote,
                'name': base + ' to ' + quote,
                'currency': quote.lower(),
                'volumecurrency': base,
                'primary_currency': quote,
                'secondary_currency': base
            }

            asset_pairs.append(asset_pair)

        return asset_pairs

    def _parse_ticker(self, data):
        database = []

        # convert key value to array
        for key, value in data.items():
            database.append(value)

        selected_asset = self.asset_pair

        query_result = [item for item in database
                        if item['primary_currency'] == selected_asset['primary_currency'] and
                        item['secondary_currency'] == selected_asset['secondary_currency']][0]

        current = float(query_result['last_price'])

        bids_highbid = float(query_result['orderbook']['bids']['highbid'])  # Buy price

        asks_highbid = float(query_result['orderbook']['asks']['highbid'])  # Sell price

        volume = float(query_result['volume_24hours'])

        return {
            'cur': current,
            'bid': bids_highbid,
            'high': None,
            'low': None,
            'ask': asks_highbid,
            'vol': volume
        }
