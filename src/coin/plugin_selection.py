# Plugin selection window

import gi
from gi.repository import Gdk, Gtk

from .exchange import Exchange


class PluginSelectionWindow(Gtk.Window):
    def __init__(self, parent):
        Gtk.Window.__init__(self, title="Plugins")

        self.parent = parent
        self.set_keep_above(True)
        self.set_border_width(5)
        self.set_position(Gtk.WindowPosition.MOUSE)
        self.connect("key-release-event", self._on_key_release)

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(True)
        self.add(grid)

        self.plugin_store = Gtk.ListStore(bool, str, object)
        for item in self.parent.exchanges.values():
            self.plugin_store.append([item.active, item.name, item])

        self.plugin_store.set_sort_column_id(1, Gtk.SortType.ASCENDING)

        self.view_plugins = Gtk.TreeView(self.plugin_store)

        rend_checkbox = Gtk.CellRendererToggle()
        rend_checkbox.connect("toggled", self._toggle)
        rend_plugin = Gtk.CellRendererText()

        col_chk = Gtk.TreeViewColumn("", rend_checkbox, active=0)
        col_plugin = Gtk.TreeViewColumn("Plugin", rend_plugin, text=1)
        # col_plugin.set_sort_column_id(0)

        self.view_plugins.append_column(col_chk)
        self.view_plugins.append_column(col_plugin)

        self.set_focus_child(self.view_plugins)

        sw = Gtk.ScrolledWindow()
        sw.set_vexpand(True)
        sw.add(self.view_plugins)
        grid.attach(sw, 0, 0, 100, 220)

        buttonbox = Gtk.Box(spacing=2)

        button_set = Gtk.Button("Select")
        button_set.connect("clicked", self._select_plugins)
        button_set.set_can_default(True)
        button_set.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)

        button_cancel = Gtk.Button("Close")
        button_cancel.connect("clicked", self._close)

        buttonbox.pack_start(button_set, True, True, 0)
        buttonbox.pack_start(button_cancel, True, True, 0)

        grid.attach(buttonbox, 0, 245, 100, 50)

        self.show_all()
        self.present()

    def _toggle(self, renderer, path):
        iter = self.plugin_store.get_iter(path)
        self.plugin_store[iter][0] = not self.plugin_store[iter][0]

    def _select_plugins(self, widget=None):
        for item in self.plugin_store:
            item[2].active = item[0]

        self.parent.plugins_updated()
        self._close()

    def _on_key_release(self, widget, ev, data=None):
        if ev.keyval == Gdk.KEY_Escape:
            self._close()

    def _close(self, widget=None):
        self.destroy()
