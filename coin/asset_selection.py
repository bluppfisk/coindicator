# Asset Selection window

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
from gi.repository.Gdk import Color

class AssetSelectionWindow(Gtk.Window):
    def __init__(self, parent):
        Gtk.Window.__init__(self, title="Select Assets")

        self.parent = parent
        self.set_keep_above(True)
        self.set_border_width(5)
        self.set_modal(True)

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(True)
        self.add(grid)

        base_store = Gtk.ListStore(str)
        for item in self.parent.coin.bases:
            base_store.append([item])

        quote_store = Gtk.ListStore(str)
        ex_store = Gtk.ListStore(str, str)

        def _base_changed(selection):
            (model, iter) = selection.get_selected()
            if iter == None:
                return

            quote_store.clear()
            self.current_base = model[iter][0]
            for quote in self.parent.coin.bases[self.current_base]:
                quote_store.append([quote])
                view_quotes.set_cursor(0)

        def _quote_changed(selection):
            (model, iter) = selection.get_selected()
            if iter == None:
                return

            ex_store.clear()
            self.current_quote = model[iter][0]
            for exchange in self.parent.coin.bases[self.current_base][self.current_quote]:
                ex_store.append([exchange.get('name'), exchange.get('code')])
                view_exchanges.set_cursor(0)

        def _exchange_changed(selection):
            (model, iter) = selection.get_selected()
            if iter == None:
                return

            self.current_exchange = model[iter][1]

        view_bases = Gtk.TreeView(base_store)
        view_quotes = Gtk.TreeView(quote_store)
        view_exchanges = Gtk.TreeView(ex_store)

        view_bases.get_selection().connect("changed", _base_changed)
        view_quotes.get_selection().connect("changed", _quote_changed)
        view_exchanges.get_selection().connect("changed", _exchange_changed)

        rend_base = Gtk.CellRendererText()
        rend_quote = Gtk.CellRendererText()
        rend_exchange = Gtk.CellRendererText()

        col_base = Gtk.TreeViewColumn("Base", rend_base, text=0)
        col_quote = Gtk.TreeViewColumn("Quote", rend_quote, text=0)
        col_exchange = Gtk.TreeViewColumn("Exchange", rend_exchange, text=0)

        view_bases.append_column(col_base)
        view_quotes.append_column(col_quote)
        view_exchanges.append_column(col_exchange)

        sw = Gtk.ScrolledWindow()
        sw.set_vexpand(True)
        sw.add(view_bases)
        grid.attach(sw, 0,0,200,400)

        sw2 = Gtk.ScrolledWindow()
        sw2.set_vexpand(True)
        sw2.add(view_quotes)
        grid.attach(sw2, 200,0,200,400)

        sw3 = Gtk.ScrolledWindow()
        sw3.set_vexpand(True)
        sw3.add(view_exchanges)
        grid.attach(sw3, 400,0,200,400)

        buttonbox = Gtk.Box(spacing=2)

        button_set = Gtk.Button('Set')
        button_set.connect("clicked", self._update_indicator)
        button_set.set_can_default(True)
        button_set.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)

        button_cancel = Gtk.Button('Cancel')
        button_cancel.connect("clicked", self._close)
        buttonbox.pack_start(button_set, True, True, 0)
        buttonbox.pack_start(button_cancel, True, True, 0)

        grid.attach(buttonbox, 0, 400, 200, 50)

        self.show_all()
        self.grab_focus()

    def _update_indicator(self, widget):
        self.parent.change_assets(self.current_base, self.current_quote, self.current_exchange)

    def _close(self, widget):
        self.destroy()