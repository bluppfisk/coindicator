# -*- coding: utf-8 -*-

# Coin Price indicator
# Nil Gradisnik <nil.gradisnik@gmail.com>

__author__ = "nil.gradisnik@gmail.com"

import os
import signal
import yaml

from indicator import Indicator

from exchange.kraken import Kraken
from exchange.bitstamp import Bitstamp

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

if __name__ == "__main__":
  signal.signal(signal.SIGINT, signal.SIG_DFL)  # ctr+c exit

  config = yaml.load(open(PROJECT_ROOT + '/config.yaml', 'r'))
  config['project_root'] = PROJECT_ROOT

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
