# -*- coding: utf-8 -*-
# Coin Price indicator
# Nil Gradisnik <nil.gradisnik@gmail.com>

import os
import signal
import yaml
import sys
import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GdkPixbuf

from indicator import Indicator
from exchange.kraken import Kraken
from exchange.bitstamp import Bitstamp

__author__ = "nil.gradisnik@gmail.com"

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

signal.signal(signal.SIGINT, signal.SIG_DFL)  # ctrl+c exit

config = yaml.load(open(PROJECT_ROOT + '/config.yaml', 'r'))
config['project_root'] = PROJECT_ROOT

print("Coin Price indicator v" + config['app']['version'])

cp_instances = yaml.load(open(PROJECT_ROOT + '/startmany.yaml', 'r'))

threads = []
indicators = []
counter = 0

for cp_instance in cp_instances:
    counter = counter + 1;
    settings = cp_instance['exchange'] + ':' + cp_instance['asset_pair'] + ':' + str(cp_instance['refresh'])
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
    ]
    indicator.set_exchanges(exchanges)
    indicators.append(indicator)

for indicator in indicators:
    indicator.start()

Gtk.main()