# -*- coding: utf-8 -*-

# Alarm

import notify2 as notify

__author__ = "nil.gradisnik@gmail.com"


class Alarm(object):
    def __init__(self, app_name, ceil=1000, floor=100):
        self.app_name = app_name
        self.ceil = ceil
        self.floor = floor

    def set_ceil(self, price):
        self.ceil = price

    def set_floor(self, price):
        self.floor = price

    def check(self, price):
        if self.ceil <= price:
            self.__notify('High Bitcoin price alert: $' + str(price),
                          'Current bitcoin price rose above your alarm threshold: $' + str(self.ceil))
        if self.floor >= price:
            self.__notify('Low Bitcoin price alert: $' + str(price),
                          'Current bitcoin price fell below your alarm threshold: $' + str(self.floor))

    def __notify(self, title, message):
        if notify.init(self.app_name):
            n = notify.Notification(title, message)
            n.set_urgency(notify.URGENCY_CRITICAL)
            n.set_timeout(notify.EXPIRES_NEVER)
            n.show()
