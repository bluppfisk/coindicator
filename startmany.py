# -*- coding: utf-8 -*-
# Coin Price Indicator Starter
# Sander Van de Moortel <sander.vandemoortel@gmail.com>

import subprocess
import os
import yaml

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

cp_instances = yaml.load(open(PROJECT_ROOT + '/startmany.yaml', 'r'))

for cp_instance in cp_instances:
	subprocess.call('python3 ' + PROJECT_ROOT + '/coin/coin.py ' + cp_instance['exchange'] + ':' + cp_instance['asset_pair'] + ':' + str(cp_instance['refresh']) + '&', shell=True)