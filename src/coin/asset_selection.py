# Asset selection window

from gi.repository import Gdk, Gtk


class AssetSelectionWindow(Gtk.Window):
    def __init__(self, parent):
        Gtk.Window.__init__(self, title="Select Asset")

        self.parent = parent
        self.set_keep_above(True)
        self.set_border_width(5)
        self.set_position(Gtk.WindowPosition.MOUSE)
        self.connect("key-release-event", self._on_key_release)
        # self.set_modal(True)

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(True)
        self.add(grid)

        self.base_store = Gtk.ListStore(str)
        for item in self.parent.coin.bases:
            self.base_store.append([item])

        self.base_store.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        self.quote_store = Gtk.ListStore(str)
        self.ex_store = Gtk.ListStore(str, str)

        self.view_bases = Gtk.TreeView(self.base_store)
        self.view_quotes = Gtk.TreeView(self.quote_store)
        self.view_exchanges = Gtk.TreeView(self.ex_store)

        self.view_bases.get_selection().connect("changed", self._base_changed)
        self.view_quotes.get_selection().connect("changed", self._quote_changed)
        self.view_exchanges.get_selection().connect("changed", self._exchange_changed)

        rend_base = Gtk.CellRendererText()
        rend_quote = Gtk.CellRendererText()
        rend_exchange = Gtk.CellRendererText()

        col_base = Gtk.TreeViewColumn("Base", rend_base, text=0)
        col_base.set_sort_column_id(0)
        col_quote = Gtk.TreeViewColumn("Quote", rend_quote, text=0)
        col_quote.set_sort_column_id(0)
        col_exchange = Gtk.TreeViewColumn("Exchange", rend_exchange, text=0)
        col_exchange.set_sort_column_id(0)

        self.view_bases.append_column(col_base)
        self.view_quotes.append_column(col_quote)
        self.view_exchanges.append_column(col_exchange)
        self.view_exchanges.connect("row-activated", self._update_indicator)

        self.set_focus_child(self.view_bases)

        sw = Gtk.ScrolledWindow()
        sw.set_vexpand(True)
        sw.add(self.view_bases)
        grid.attach(sw, 0, 0, 200, 400)

        sw2 = Gtk.ScrolledWindow()
        sw2.set_vexpand(True)
        sw2.add(self.view_quotes)
        grid.attach(sw2, 200, 0, 200, 400)

        sw3 = Gtk.ScrolledWindow()
        sw3.set_vexpand(True)
        sw3.add(self.view_exchanges)
        grid.attach(sw3, 400, 0, 200, 400)

        lbl_hint = Gtk.Label("Hint: Start typing in a list to search.")
        grid.attach(lbl_hint, 100, 400, 400, 25)

        buttonbox = Gtk.Box(spacing=2)

        button_set_close = Gtk.Button("Set and Close")
        button_set_close.connect("clicked", self._update_indicator_close)

        button_set = Gtk.Button("Set")
        button_set.connect("clicked", self._update_indicator)
        button_set.set_can_default(True)
        button_set.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)

        button_cancel = Gtk.Button("Close")
        button_cancel.connect("clicked", self._close)

        buttonbox.pack_start(button_set_close, True, True, 0)
        buttonbox.pack_start(button_set, True, True, 0)
        buttonbox.pack_start(button_cancel, True, True, 0)

        grid.attach(buttonbox, 0, 425, 600, 50)

        self._select_currents()
        self.show_all()
        self.present()

    def _base_changed(self, selection):
        (model, iter) = selection.get_selected()
        if iter is None:
            return

        self.quote_store.clear()
        self.current_base = model[iter][0]
        for quote in self.parent.coin.bases[self.current_base]:
            self.quote_store.append([quote])

        self.quote_store.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        self.view_quotes.set_cursor(0)

    def _quote_changed(self, selection):
        (model, iter) = selection.get_selected()
        if iter is None:
            return

        self.ex_store.clear()
        self.current_quote = model[iter][0]
        for exchange in self.parent.coin.bases[self.current_base][self.current_quote]:
            if exchange.active:
                self.ex_store.append([exchange.name, exchange.code])

        self.ex_store.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        self.view_exchanges.set_cursor(0)

    def _exchange_changed(self, selection):
        (model, iter) = selection.get_selected()
        if iter is None:
            return

        self.current_exchange = model[iter][1]

    ##
    # Select the currently active values and scroll them into view
    #
    def _select_currents(self):
        def _select_and_scroll(store, view, current_value):
            for row in store:
                if row[0] == current_value:
                    view.set_cursor(row.path)
                    view.scroll_to_cell(row.path)
                    break

        _select_and_scroll(
            self.base_store,
            self.view_bases,
            self.parent.exchange.asset_pair.get("base"),
        )
        _select_and_scroll(
            self.quote_store,
            self.view_quotes,
            self.parent.exchange.asset_pair.get("quote"),
        )
        _select_and_scroll(
            self.ex_store, self.view_exchanges, self.parent.exchange.name
        )

    def _update_indicator_close(self, widget):
        self._update_indicator(widget)
        self._close(widget)

    def _update_indicator(self, widget, *args):
        exchange = self.parent.coin.exchanges[self.current_exchange]
        self.parent.change_assets(self.current_base, self.current_quote, exchange)

    def _on_key_release(self, widget, ev, data=None):
        if ev.keyval == Gdk.KEY_Escape:
            self._close()

    def _close(self, widget=None):
        self.destroy()
