# -*- coding: utf-8 -*-
# Coin Price Indicator Starter
# Sander Van de Moortel <sander.vandemoortel@gmail.com>

import subprocess
import os
import yaml

from coin.coin import Coin

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GdkPixbuf


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

cp_instances = yaml.load(open(PROJECT_ROOT + '/startmany.yaml', 'r'))

threads = []
counter = 0

for cp_instance in cp_instances:
	++counter
	settings = cp_instance['exchange'] + ':' + cp_instance['asset_pair'] + ':' + str(cp_instance['refresh'])
	threads.append(Coin(counter, 'coin' + str(counter), counter, settings))

for thread in threads:
	thread.start()
	thread.join()

# Gtk.main()