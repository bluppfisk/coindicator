# Lets the user set an alert for a certain price point

import gi
import notify2
import pygame

from coin.config import Config

from gi.repository import Gdk, GdkPixbuf, Gtk
from gi.repository.Gdk import Color


class Alarm(object):
    def __init__(self, parent, ceil=None, floor=None):
        self.parent = parent
        self.app_name = parent.coin.config.get("app").get("name")
        self.ceil = ceil
        self.floor = floor
        self.active = False
        self.config = Config()

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

    ##
    # Checks the threshold property against a given price and
    # calls the notification function
    #
    def check(self, price):
        if self.ceil:
            if price > self.ceil:
                self.__notify(price, "rose above", self.ceil)
                return True

        if self.floor:
            if price < self.floor:
                self.__notify(price, "fell below", self.floor)
                return True

        return False

    ##
    # Creates a system notification. On Ubuntu 16.04 with Unity 7, this is a
    # translucent bubble, of which only one can be shown at the same time.
    #
    def __notify(self, price, direction, threshold):
        exchange_name = self.parent.exchange.name
        asset_name = self.parent.exchange.asset_pair.get("base")

        title = asset_name + " price alert: " + self.parent.symbol + str(price)
        message = (
            "Price on "
            + exchange_name
            + " "
            + direction
            + " "
            + self.parent.symbol
            + str(threshold)
        )

        if notify2.init(self.app_name):
            if pygame.init():
                pygame.mixer.music.load(
                    self.config["project_root"] / "resources/ca-ching.wav"
                )
                pygame.mixer.music.play()
            logo = GdkPixbuf.Pixbuf.new_from_file(
                str(self.config["project_root"] / "resources/icon_32px.png")
            )

            n = notify2.Notification(title, message)
            n.set_icon_from_pixbuf(logo)
            n.set_urgency(2)  # highest
            n.show()


class AlarmSettingsWindow(Gtk.Window):
    def __init__(self, parent, price):
        Gtk.Window.__init__(self, title="Set price alert")

        self.parent = parent
        self.set_keep_above(True)
        self.set_border_width(5)
        self.set_position(Gtk.WindowPosition.MOUSE)
        self.connect("key-release-event", self._on_key_release)

        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)

        label = Gtk.Label("Alert if the active price is")

        hbox = Gtk.Box(spacing=2)
        radio_over = Gtk.RadioButton.new_with_label(None, "above")
        radio_under = Gtk.RadioButton.new_with_label_from_widget(radio_over, "below")

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
        entry_price.connect("activate", self._set_alarm, radio_over, entry_price)
        entry_price.connect("changed", self._strip_text)
        self.set_focus_child(entry_price)

        # Pack horizontally
        hbox.pack_start(label, False, False, 0)
        hbox.pack_start(radio_over, False, False, 0)
        hbox.pack_start(radio_under, False, False, 0)
        hbox.pack_start(entry_price, True, True, 0)

        # Set and Cancel buttons
        buttonbox = Gtk.Box(spacing=2)
        button_set = Gtk.Button("Set Alert")
        button_clear = Gtk.Button("Delete Alert")
        button_cancel = Gtk.Button("Close")
        button_set.connect("clicked", self._set_alarm, radio_over, entry_price)
        button_set.set_can_default(True)
        button_set.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
        button_clear.connect("clicked", self._clear_alarm)
        button_cancel.connect("clicked", self._close)
        buttonbox.pack_start(button_set, True, True, 0)
        buttonbox.pack_start(button_clear, True, True, 0)
        buttonbox.pack_start(button_cancel, True, True, 0)

        # Display in content area
        self.grid.attach(hbox, 0, 0, 50, 50)
        self.grid.attach(buttonbox, 0, 50, 50, 50)
        self.add(self.grid)

        self.set_accept_focus(True)
        self.show_all()
        self.present()
        entry_price.grab_focus()  # focus on entry field

    ##
    # This function strips all but numbers and decimal points from
    # the entry field. If the value cannot be converted to a float,
    # the text colour will turn red.
    #
    def _strip_text(self, widget):
        widget.modify_fg(Gtk.StateFlags.NORMAL, None)
        text = widget.get_text().strip()
        filtered_text = "".join([i for i in text if i in "0123456789."])
        widget.set_text(filtered_text)
        try:
            float(filtered_text)
        except ValueError:
            widget.modify_fg(Gtk.StateFlags.NORMAL, Color(50000, 0, 0))

    ##
    # Sets the alarm threshold
    #
    def _set_alarm(self, widget, radio_over, entry_price):
        above = radio_over.get_active()  # if False, then 'under' must be True
        try:
            price = float(entry_price.get_text())
            if above:
                self.parent.alarm.set_ceil(price)
                self.parent.alarm.set_floor(None)
            else:
                self.parent.alarm.set_floor(price)
                self.parent.alarm.set_ceil(None)

            self.destroy()

        # if user attempts to set an incorrect value, the dialog box stays
        # and the field is emptied
        except ValueError:
            entry_price.set_text("")
            entry_price.grab_focus()

    def _on_key_release(self, widget, ev, data=None):
        if ev.keyval == Gdk.KEY_Escape:
            self._close()

    def _clear_alarm(self, widget=None):
        self.parent.alarm.deactivate()
        self.destroy()

    def _close(self, widget=None):
        self.destroy()
