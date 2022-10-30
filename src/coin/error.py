# Exchange error handling

import logging

from gi.repository import GLib

MAX_ERRORS = 5  # maximum number of errors before chilling
REFRESH_INTERVAL = 60  # chill refresh frequency in seconds


class Error:
    def __init__(self, exchange):
        self.exchange = exchange

        self.count = 0
        self.chill = False

    def increment(self):
        self.count += 1

    def reset(self):
        self.count = 0

    def clear(self):
        self.reset()

        if self.chill:
            self.log("Restoring normal refresh frequency.")
            self.exchange.stop().start()
            self.chill = False

    def log(self, message):
        logging.warning("%s: %s" % (self.exchange.name, str(message)))

    def is_ok(self):
        max = self.count <= MAX_ERRORS

        if max is False:
            self.log(
                "Error limit reached. Cooling down for "
                + str(REFRESH_INTERVAL)
                + " seconds."
            )
            self.exchange.stop()
            GLib.timeout_add_seconds(REFRESH_INTERVAL, self.exchange.restart)
            self.chill = True
        else:
            self.chill = False

        return max
