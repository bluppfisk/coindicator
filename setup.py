# -*- coding: utf-8 -*-

import yaml

from setuptools import setup, find_packages

config = yaml.load(open('config.yaml', 'r'))
readme = open('README.md', 'r')
license = open('LICENSE', 'r')

setup(
    name=config['app']['name'],
    version=config['app']['version'],
    description=config['app']['description'],
    long_description=readme,
    author=config['author']['name'],
    author_email=config['author']['email'],
    url=config['app']['url'],
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
