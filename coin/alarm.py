# -*- coding: utf-8 -*-

# Alarm
import notify2 as notify
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

__author__ = "sander.vandemoortel@gmail.com"

class Alarm(object):
    def __init__(self, app_name, ceil=None, floor=None):
        self.app_name = app_name
        self.ceil = ceil
        self.floor = floor
        self.active = False

    def set_ceil(self, price):
        self.ceil = price
        self.active = True

    def set_floor(self, price):
        self.floor = price
        self.active = True

    def deactivate(self):
        self.ceil = None
        self.floor = None
        self.active = False

    def check(self, price):
        if self.ceil:
            if self.ceil <= price:
                self.__notify('Price alert: ' + str(price),
                              'Price rose above your alarm threshold of ' + str(self.ceil))
                return True

        if self.floor:
            if self.floor >= price:
                self.__notify('Price alert: ' + str(price),
                              'Price fell below your alarm threshold of ' + str(self.floor))
                return True

        return False

    def __notify(self, title, message):
        if notify.init(self.app_name):
            n = notify.Notification(title, message)
            n.set_urgency(notify.URGENCY_CRITICAL)
            n.set_timeout(notify.EXPIRES_NEVER)
            n.show()

class AlarmSettingsWindow(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Set price alert", None, 0)

        self.parent = parent
        self.set_default_size(200, 100)
        self.set_keep_above(True)

        label = Gtk.Label("Set a price alert if the price is")

        hbox = Gtk.Box(spacing=2)
        radio_over = Gtk.RadioButton.new_with_label(None, 'above')
        radio_under = Gtk.RadioButton.new_with_label_from_widget(radio_over, 'below')

        price = 0

        # Get existing alarm settings
        if self.parent.alarm.active:
            if self.parent.alarm.ceil:
                price = self.parent.alarm.ceil
                radio_over.set_active(True)
            elif self.parent.alarm.floor:
                price = self.parent.alarm.floor
                radio_under.set_active(True)

        entry_price = Gtk.Entry()
        entry_price.set_text(str(price))
        entry_price.connect('activate', self._set_alarm, radio_over, entry_price)

        # Pack horizontally
        hbox.pack_start(label, False, False, 0)
        hbox.pack_start(radio_over, False, False, 0)
        hbox.pack_start(radio_under, False, False, 0)
        hbox.pack_start(entry_price, False, False, 0)

        # Set and Cancel buttons
        buttonbox = Gtk.Box(spacing=2)
        button_set = Gtk.Button('Set Alarm')
        button_cancel = Gtk.Button('Cancel')
        button_set.connect("clicked", self._set_alarm, radio_over, entry_price)
        button_cancel.connect("clicked", self._close)
        buttonbox.pack_start(button_set, False, False, 0)
        buttonbox.pack_start(button_cancel, False, False, 0)

        # Display in content area
        box = self.get_content_area()
        box.add(hbox)
        box.add(buttonbox)
        entry_price.grab_focus() # focus on entry field

        self.show_all()
        self.grab_focus()

    def _set_alarm(self, widget, radio_over, entry_price):
        above = radio_over.get_active()
        price = float(entry_price.get_text())
        
        if above:
            self.parent.alarm.set_ceil(price)
        else:
            self.parent.alarm.set_floor(price)

        self.destroy()

    def _close(self, widget):
        self.destroy()