# -*- coding: utf-8 -*-
# Alarm
# 

import gi, pygame, notify2
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, GdkPixbuf
from gi.repository.Gdk import Color

class Alarm(object):
    def __init__(self, parent, ceil=None, floor=None):
        self.parent = parent
        self.app_name = parent.coin.config['app']['name']
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
                self.__notify(price, 'rose above', self.ceil)
                return True

        if self.floor:
            if self.floor >= price:
                self.__notify(price, 'fell below', self.floor)
                return True

        return False

    def __notify(self, price, direction, threshold):
        exchange_name = [e.get('name') for e in self.parent.EXCHANGES if self.parent.active_exchange == e.get('code')][0]
        assets = self.parent.CURRENCIES[self.parent.active_exchange]
        asset_name = [e.get('name') for e in assets if self.parent.active_asset_pair == e.get('isocode')][0][0:3]

        title = asset_name + ' price alert: ' + self.parent.currency + str(price)
        message = 'Price on ' + exchange_name + ' ' + direction + ' ' + self.parent.currency + str(threshold)

        if notify2.init(self.app_name):
            if pygame.init():
                pygame.mixer.music.load(self.parent.coin.config['project_root'] + '/resources/ca-ching.wav')
                pygame.mixer.music.play()
            logo = GdkPixbuf.Pixbuf.new_from_file(self.parent.coin.config['project_root'] + '/resources/icon_32px.png')
            n = notify2.Notification(title, message)
            n.set_icon_from_pixbuf(logo)
            n.set_urgency(2) # highest
            n.show()

class AlarmSettingsWindow(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Set price alert", None, 0)

        self.parent = parent
        self.set_keep_above(True)
        self.set_border_width(5)
        self.set_modal(True)

        label = Gtk.Label("Alert if the active price is")

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
        entry_price.connect('changed', self._strip_text)
        self.set_focus_child(entry_price)

        # Pack horizontally
        hbox.pack_start(label, False, False, 0)
        hbox.pack_start(radio_over, False, False, 0)
        hbox.pack_start(radio_under, False, False, 0)
        hbox.pack_start(entry_price, False, False, 0)

        # Set and Cancel buttons
        buttonbox = Gtk.Box(spacing=2)
        button_set = Gtk.Button('Set Alert')
        button_clear = Gtk.Button('Clear Alert')
        button_cancel = Gtk.Button('Cancel')
        button_set.connect("clicked", self._set_alarm, radio_over, entry_price)
        button_set.set_can_default(True)
        button_set.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
        button_clear.connect("clicked", self._clear_alarm)
        button_cancel.connect("clicked", self._close)
        buttonbox.pack_start(button_set, True, True, 0)
        buttonbox.pack_start(button_clear, True, True, 0)
        buttonbox.pack_start(button_cancel, True, True, 0)

        # Display in content area
        box = self.get_content_area()
        box.add(hbox)
        box.add(buttonbox)
        entry_price.grab_focus() # focus on entry field

        self.show_all()
        self.grab_focus()

    def _strip_text(self, widget):
        widget.modify_fg(Gtk.StateFlags.NORMAL, None)
        text = widget.get_text().strip()
        filtered_text = (''.join([i for i in text if i in '0123456789.']))
        widget.set_text(filtered_text)
        try:
            price = float(filtered_text)
        except ValueError:
            widget.modify_fg(Gtk.StateFlags.NORMAL, Color(50000, 0, 0))

    def _set_alarm(self, widget, radio_over, entry_price):
        above = radio_over.get_active()
        try:
            price = float(entry_price.get_text())
            if above:
                self.parent.alarm.set_ceil(price)
                self.parent.alarm.set_floor(None)
            else:
                self.parent.alarm.set_floor(price)
                self.parent.alarm.set_ceil(None)

            self.destroy()
        
        except ValueError:
            entry_price.set_text('')
            entry_price.grab_focus()
        
    def _clear_alarm(self, widget):
        self.parent.alarm.deactivate()
        self.destroy()

    def _close(self, widget):
        self.destroy()