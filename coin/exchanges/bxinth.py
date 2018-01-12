# -*- coding: utf-8 -*-

# Bx.in.th Api 
# https://bittrex.com/Home/Api
# Added by : Theppasith N. 
__author__ = "tutorgaming@gmail.com"

from exchange import Exchange, CURRENCY

class Bxinth(Exchange):
    """
    Bx.in.th Exchange class
    """
    CONFIG = {
    'name' : 'BX.in.th',
    'default_label': 'current',
    'ticker' : 'https://bx.in.th/api/',
    'asset_pairs': [
        {
        'isocode' : 'XXBTCZTHB',
        'pair' : 'XXBTCZTHB',
        'name' : 'BTC to THB',
        'volumelabel' : 'BTC',
        'currency' : CURRENCY['thb'],
        'pairing_id' : 1,
        'primary_currency': 'THB',
        'secondary_currency': 'BTC'
        },
         {
            'isocode' : 'XXETHZTHB',
            'pair' : 'XXETHZTHB',
            'name' : 'ETH TO THB',
            'volumelabel' : 'ETH',
            'currency' : CURRENCY['thb'],
            'pairing_id' : 21,
            'primary_currency': 'THB',
            'secondary_currency': 'ETH'
        },
         {
            'isocode' : 'XXDASZTHB',
            'pair' : 'XXDASZTHB',
            'name' : 'DASH TO THB',
            'volumelabel' : 'DAS',
            'currency' : CURRENCY['thb'],
            'pairing_id' : 22,
            'primary_currency': 'THB',
            'secondary_currency': 'DAS'
        },
         {
            'isocode' : 'XXREPZTHB',
            'pair' : 'XXREPZTHB',
            'name' : 'REP TO THB',
            'volumelabel' : 'REP',
            'currency' : CURRENCY['thb'],
            'pairing_id' : 23,
            'primary_currency': 'THB',
            'secondary_currency': 'REP'
        },
         {
            'isocode' : 'XXGNOZTHB',
            'pair' : 'XXGNOZTHB',
            'name' : 'GNO TO THB',
            'volumelabel' : 'GNO',
            'currency' : CURRENCY['thb'],
            'pairing_id' : 24,
            'primary_currency': 'THB',
            'secondary_currency': 'GNO'
        },
         {
            'isocode' : 'XXRPZTHB',
            'pair' : 'XXRPZTHB',
            'name' : 'XRP TO THB',
            'volumelabel' : 'XRP',
            'currency' : CURRENCY['thb'],
            'pairing_id' : 25,
            'primary_currency': 'THB',
            'secondary_currency': 'XRP'
        },
         {
            'isocode' : 'XXOMGZTHB',
            'pair' : 'XXOMGZTHB',
            'name' : 'OMG TO THB',
            'volumelabel' : 'OMG',
            'currency' : CURRENCY['thb'],
            'pairing_id' : 26,
            'primary_currency': 'THB',
            'secondary_currency': 'OMG'
        },
         {
            'isocode' : 'XXBCHZTHB',
            'pair' : 'XXBCHZTHB',
            'name' : 'BCH TO THB',
            'volumelabel' : 'BCH',
            'currency' : CURRENCY['thb'],
            'pairing_id' : 27,
            'primary_currency': 'THB',
            'secondary_currency': 'BCH'
        },
         {
            'isocode' : 'XXEVXZTHB',
            'pair' : 'XXEVXZTHB',
            'name' : 'EVX TO THB',
            'volumelabel' : 'EVX',
            'currency' : CURRENCY['thb'],
            'pairing_id' : 28,
            'primary_currency': 'THB',
            'secondary_currency': 'EVX'
        },
         {
            'isocode' : 'XXXZCZTHB',
            'pair' : 'XXXZCZTHB',
            'name' : 'XZC TO THB',
            'volumelabel' : 'XZC',
            'currency' : CURRENCY['thb'],
            'pairing_id' : 29,
            'primary_currency': 'THB',
            'secondary_currency': 'XZC'
        },
         {
            'isocode' : 'XXLTCZTHB',
            'pair' : 'XXLTCZTHB',
            'name' : 'LTC TO THB',
            'volumelabel' : 'LTC',
            'currency' : CURRENCY['thb'],
            'pairing_id' : 30,
            'primary_currency': 'THB',
            'secondary_currency': 'LTC'
        }
        ]
    }
    
    def __init__(self,indicator):
        super().__init__(indicator)
        self.round = False

    def get_ticker(self):
        return self.config['ticker']

    def _parse_result(self, data):
        database = []
        # convert key value to array 

        for key,value in data.items():
            database.append(value)

        selected_isocode = self.asset_pair


        # Select result by its isocode
        selected_asset = [item for item in self.config['asset_pairs'] if item['isocode'] == selected_isocode][0]

        query_result = [item for item in database 
                        if item['primary_currency'] == selected_asset['primary_currency'] and
                           item['secondary_currency'] == selected_asset['secondary_currency'] ][0]

        
        current = float(query_result['last_price'])

        bids_highbid = float(query_result['orderbook']['bids']['highbid']) #Buy price 
        bids_volume = float(query_result['orderbook']['bids']['volume'])
        
        asks_volume = float(query_result['orderbook']['asks']['volume'])
        asks_highbid = float(query_result['orderbook']['asks']['highbid']) #Sell price
        
        volume = float(query_result['volume_24hours'])
        
        return {
          'cur': current,
          'bid': bids_highbid,
          'high': 0,
          'low': 0,
          'ask': asks_highbid,
          'vol': volume
        }


####################################################################

# from gi.repository import GLib

# import requests
# import logging

# import utils
# from exchange.error import Error
# from alarm import Alarm

# # BX.in.th Return all of the currency pairs when request 

# CONFIG = {
#     'name' : 'BX.in.th'
#     'ticker' : 'https://bx.in.th/api/',
#     'asset_pairs': [
#         {
#         'isocode' : 'XXBTCZTHB',
#         'pair' : 'XXBTCZTHB',
#         'name' : 'BTC to THB',
#         'volumelabel' : 'THB',
#         'currency' : CURRENCY['thb'],
#         'pairing_id' : 1,
#         'primary_currency': 'THB',
#         'secondary_currency': 'BTC'
#     },
#      {
#         'isocode' : 'XXETHZTHB',
#         'pair' : 'XXETHZTHB',
#         'name' : 'ETH TO THB',
#         'volumelabel' : 'THB',
#         'currency' : CURRENCY['thb'],
#         'pairing_id' : 21,
#         'primary_currency': 'THB',
#         'secondary_currency': 'ETH'
#     },
#      {
#         'isocode' : 'XXDASZTHB',
#         'pair' : 'XXDASZTHB',
#         'name' : 'DASH TO THB',
#         'volumelabel' : 'THB',
#         'currency' : CURRENCY['thb'],
#         'pairing_id' : 22,
#         'primary_currency': 'THB',
#         'secondary_currency': 'DAS'
#     },
#      {
#         'isocode' : 'XXREPZTHB',
#         'pair' : 'XXREPZTHB',
#         'name' : 'REP TO THB',
#         'volumelabel' : 'THB',
#         'currency' : CURRENCY['thb'],
#         'pairing_id' : 23,
#         'primary_currency': 'THB',
#         'secondary_currency': 'REP'
#     },
#      {
#         'isocode' : 'XXGNOZTHB',
#         'pair' : 'XXGNOZTHB',
#         'name' : 'GNO TO THB',
#         'volumelabel' : 'THB',
#         'currency' : CURRENCY['thb'],
#         'pairing_id' : 24,
#         'primary_currency': 'THB',
#         'secondary_currency': 'GNO'
#     },
#      {
#         'isocode' : 'XXRPZTHB',
#         'pair' : 'XXRPZTHB',
#         'name' : 'XRP TO THB',
#         'volumelabel' : 'THB',
#         'currency' : CURRENCY['thb'],
#         'pairing_id' : 25,
#         'primary_currency': 'THB',
#         'secondary_currency': 'XRP'
#     },
#      {
#         'isocode' : 'XXOMGZTHB',
#         'pair' : 'XXOMGZTHB',
#         'name' : 'OMG TO THB',
#         'volumelabel' : 'THB',
#         'currency' : CURRENCY['thb'],
#         'pairing_id' : 26,
#         'primary_currency': 'THB',
#         'secondary_currency': 'OMG'
#     },
#      {
#         'isocode' : 'XXBCHZTHB',
#         'pair' : 'XXBCHZTHB',
#         'name' : 'BCH TO THB',
#         'volumelabel' : 'THB',
#         'currency' : CURRENCY['thb'],
#         'pairing_id' : 27,
#         'primary_currency': 'THB',
#         'secondary_currency': 'BCH'
#     },
#      {
#         'isocode' : 'XXEVXZTHB',
#         'pair' : 'XXEVXZTHB',
#         'name' : 'EVX TO THB',
#         'volumelabel' : 'THB',
#         'currency' : CURRENCY['thb'],
#         'pairing_id' : 28,
#         'primary_currency': 'THB',
#         'secondary_currency': 'EVX'
#     },
#      {
#         'isocode' : 'XXXZCZTHB',
#         'pair' : 'XXXZCZTHB',
#         'name' : 'XZC TO THB',
#         'volumelabel' : 'THB',
#         'currency' : CURRENCY['thb'],
#         'pairing_id' : 29,
#         'primary_currency': 'THB',
#         'secondary_currency': 'XZC'
#     },
#      {
#         'isocode' : 'XXLTCZTHB',
#         'pair' : 'XXLTCZTHB',
#         'name' : 'LTC TO THB',
#         'volumelabel' : 'THB',
#         'currency' : CURRENCY['thb'],
#         'pairing_id' : 30,
#         'primary_currency': 'THB',
#         'secondary_currency': 'LTC'
#     }
#     ]
# }






# class Bxinth:
#     def __init__(self, config, indicator):
#         self.indicator = indicator

#         self.timeout_id = 0
#         self.alarm = Alarm(config['app']['name'])

#         self.error = Error(self)

#     def start(self, error_refresh=None):
#         refresh = error_refresh if error_refresh else self.indicator.refresh_frequency
#         self.timeout_id = GLib.timeout_add_seconds(refresh, self.check_price)

#     def stop(self):
#         if self.timeout_id:
#             GLib.source_remove(self.timeout_id)

#     def check_price(self):
#         self.asset_pair = self.indicator.active_asset_pair

#         try:
#             # Bx return all pair
#             res = requests.get(CONFIG['ticker'])
#             data = res.json()

#             print(res.status_code)

#             # if res.status_code != 200:
#             #     self._handle_error(data['error'])
#             # else:
#             if data:
#                 self._parse_result(data)
    
#         except Exception as e:
#             logging.info('Error: ' + str(e))
#             self.error.increment()

#         return self.error.is_ok()

#     def _parse_result(self, data):
#         self.error.clear()
#         '''
#         {
#         "1": {
#             "pairing_id": 1,
#             "primary_currency": "THB",
#             "secondary_currency": "BTC",
#             "change": 18.17,
#             "last_price": 495000,
#             "volume_24hours": 1078.99393315,
#             "orderbook": {
#                 "bids": {
#                     "total": 2020,
#                     "volume": 402.86325154,
#                     "highbid": 494550
#                 },
#                 "asks": {
#                     "total": 1023,
#                     "volume": 121.50280514,
#                     "highbid": 495000
#                 }
#             }
#         }
#         '''
#         database = []
#         # convert key value to array 

#         for key,value in data.items():
#             database.append(value)

#         print("----------")
#         print(self.asset_pair)

#         selected_isocode = self.asset_pair


#         # Select result by its isocode
#         selected_asset = [item for item in CONFIG['asset_pairs'] if item['isocode'] == selected_isocode][0]

#         query_result = [item for item in database 
#                         if item['primary_currency'] == selected_asset['primary_currency'] and
#                            item['secondary_currency'] == selected_asset['secondary_currency'] ][0]

#         print(query_result)


#         label = str(query_result['secondary_currency']) + "  : " + str(query_result['last_price']) + " " + str(query_result['primary_currency'])
#         bids_highbid = str("BIDS HIGHBID : \t\t") + str(query_result['orderbook']['bids']['highbid']) #Buy price 
#         bids_volume = str("BIDS VOL : \t\t\t") + str(query_result['orderbook']['bids']['volume'])
        
#         asks_volume = str("ASKS VOL : \t\t\t") + str(query_result['orderbook']['asks']['volume'])
#         asks_highbid = str("ASKS HIGHBID : \t\t") + str(query_result['orderbook']['asks']['highbid']) #Sell price
        

#         self.indicator.set_data(label, bids_highbid,bids_volume, asks_volume,asks_highbid)

#     def _handle_error(self, error):
#         logging.info("BX.in.th API error: " + error)