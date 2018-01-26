# -*- coding: utf-8 -*-

import yaml

from setuptools import setup, find_packages

config = yaml.load(open('config.yaml', 'r'))
readme = open('README.md', 'r')
license = open('LICENSE', 'r')

setup(
    name=config['app']['name'].replace(" ","-"),
    version=config['app']['version'],
    description=config['app']['description'],
    long_description=readme.read(),
    author=config['authors'][0]['name'],
    author_email=config['authors'][0]['email'],
    url=config['app']['url'],
    license=license.read(),
    packages=find_packages(exclude=('tests', 'docs'))
)
