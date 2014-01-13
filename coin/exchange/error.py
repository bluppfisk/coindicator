# -*- coding: utf-8 -*-

# Echange error handling

__author__ = "nil.gradisnik@gmail.com"

MAX_ERRORS = 5  # maximum number of errors before chilling
REFRESH_INTERVAL = 60  # chill refresh frequency in seconds

class Error:

  def __init__(self, exchange):
    self.exchange = exchange

    self.count = 0
    self.chill = False

  def increment(self):
    self.count += 1

  def clear(self):
    self.count = 0

    if (self.chill):
      print("All ok. Restoring normal refresh frequency.")
      self.exchange.stop()
      self.exchange.start()
      self.chill = False

  def is_ok(self):
    max = self.count < MAX_ERRORS

    if (max is False):
      print("Warning: maximum error count reached [" + str(MAX_ERRORS) + "]. Cooling down (" + str(REFRESH_INTERVAL) + "s refresh)")
      self.exchange.stop()
      self.exchange.start(REFRESH_INTERVAL)
      self.chill = True
    else:
      self.chill = False

    return max
