# -*- coding: utf-8 -*-

# Coin Price indicator
# Nil Gradisnik <nil.gradisnik@gmail.com>

# Thanks to http://conjurecode.com/create-indicator-applet-for-ubuntu-unity-with-python/

__author__ = "nil.gradisnik@gmail.com"

import signal
import yaml

from indicator import Indicator

from exchange.kraken import Kraken
from exchange.bitstamp import Bitstamp

if __name__ == "__main__":
  signal.signal(signal.SIGINT, signal.SIG_DFL) # ctr+c exit

  config = yaml.load(open('config.yaml', 'r'))
  print("Starting Coin Price indicator v" + str(config['app']['version']))

  # indicator applet
  indicator = Indicator(config)

  # exchanges
  exchanges = [
    {
      'code': 'kraken',
      'name': 'Kraken',
      'instance': Kraken(config, indicator)
    },
    {
      'code': 'bitstamp',
      'name': 'Bitstamp',
      'instance': Bitstamp(config, indicator)
    }
  ]

  # init
  indicator.init(exchanges)
