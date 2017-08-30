# -*- coding: utf-8 -*-
# Coin Price indicator
# Nil Gradisnik <nil.gradisnik@gmail.com>

import os
import signal
import yaml
import sys
import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

from indicator import Indicator
from exchange.kraken import Kraken
from exchange.bitstamp import Bitstamp
from exchange.bityep import BitYep

__author__ = "nil.gradisnik@gmail.com"

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

signal.signal(signal.SIGINT, signal.SIG_DFL)  # ctrl+c exit

config = yaml.load(open(PROJECT_ROOT + '/config.yaml', 'r'))
config['project_root'] = PROJECT_ROOT

print("Coin Price indicator v" + config['app']['version'])

class Coin(object):
    def __init__(self):
        usage_error = 'Usage: coin.py [flags]\nasset\texchange:asset_pair:refresh_rate\nfile\tLoads various asset pairs from YAML file in ./coin directory'
        if len(sys.argv) > 2:
            quit('Too many parameters\n' + usage_error)

        if len(sys.argv) == 2:
            if '=' in sys.argv[1]:
                args = sys.argv[1].split('=')
                if args[0] == 'file':
                    try:
                        cp_instances = yaml.load(open(PROJECT_ROOT + '/coin/' + args[1], 'r'))
                    except:
                        quit('Error opening assets file')

                    self.run_many(cp_instances)

                elif args[0] == 'asset':
                    self.run(0, args[1])

                else:
                    quit('Invalid parameter\n' + usage_error)

            else:
                quit('Invalid parameter\n' + usage_error)

        else:
            self.run(0)

    def run(self, counter, settings=None):
        indicator = Indicator(counter, config, settings)
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
            },
            {
                'code': 'bityep',
                'name': 'BitYep',
                'instance': BitYep(config, indicator)
            }
        ]
        indicator.set_exchanges(exchanges)
        indicator.start()
        # return indicator


    def run_many(self, cp_instances):
        # indicators = []
        counter = 0     

        for cp_instance in cp_instances:
            counter = counter + 1
            settings = cp_instance['exchange'] + ':' + cp_instance['asset_pair'] + ':' + str(cp_instance['refresh'])
            self.run(counter, settings)
            # indicators.append(indicator)

coin = Coin()
# coin.run()
Gtk.main()