from gi.repository import Gtk, GObject


class AbstractGridPicker(Gtk.Box):
    __gsignals__ = {
        "item-selected": (GObject.SignalFlags.RUN_FIRST, None, (object,))
    }

    def __init__(self, *, button=None, enableSearch=True, filters=None, columns=3):
        super().__init__()

        self.columns = columns
        self.filters = filters
        self.currentFilter = None
        self.searchText = ""

        self.store = Gtk.TreeStore(GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT)
        self.filterModel = self.store.filter_new()
        self.filterModel.set_visible_func(self._filterFunc)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_border_width(6)

        if enableSearch:
            self.search_entry = Gtk.SearchEntry()
            self.search_entry.connect("search-changed", self._onSearchChanged)
            box.pack_start(self.search_entry, False, False, 0)

        if filters:
            self.cssProvider = Gtk.CssProvider()
            self.cssProvider.load_from_data(b"""
                .highlighted-button {
                    border: 2px solid #000000;
                }
            """)

            Gtk.StyleContext.add_provider_for_screen(
                self.get_screen(), self.cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            box.pack_start(self._buildFilterButtons(), False, False, 0)            

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_min_content_height(300)

        self.grid = Gtk.Grid(column_spacing=12, row_spacing=6)
        scroller.add(self.grid)

        box.pack_start(scroller, True, True, 0)

        if button:
            self.popover = Gtk.Popover.new(button)
        else:
            self.popover = Gtk.Popover()
        self.popover.add(box)

    def getItems(self):
        raise NotImplementedError

    def getItemLabel(self, item) -> str:
        raise NotImplementedError

    def getItemPixbuf(self, item):
        raise NotImplementedError

    def getItemFilterKey(self, item):
        return None

    def _filterFunc(self, model, iter_, data=None):
        filterKey, item = model[iter_]

        if self.currentFilter is not None and filterKey != self.currentFilter:
            return False

        if self.searchText:
            return self.searchText.lower() in self.getItemLabel(item).lower()

        return True

    def _onSearchChanged(self, entry):
        self.searchText = entry.get_text()
        self._refresh()

    def _buildFilterButtons(self):
        box = Gtk.Box(spacing=6)

        self.lastClickedButton = None

        buttons = [("All", None)]

        if hasattr(self.filters, "__iter__"):
            if hasattr(self.filters, "__members__"):
                buttons += [
                    (f.name.capitalize(), f) for f in reversed(self.filters)
                ]
            else:
                buttons += self.filters

        for label, value in buttons:
            btn = Gtk.Button(label=label)

            if value is None:
                self._highlight(btn)

            btn.connect("clicked", self._onFilterSelected, value)
            box.pack_start(btn, False, False, 0)

        return box

    def _onFilterSelected(self, button, value):
        self._highlight(button)
        self.currentFilter = value
        self._refresh()

    def _highlight(self, button):
        if self.lastClickedButton:
            self.lastClickedButton.get_style_context().remove_class("highlighted-button")

        button.get_style_context().add_class("highlighted-button")
        self.lastClickedButton = button

    def _refresh(self):
        self.filterModel.refilter()
        self._rebuildGrid()

    def _rebuildGrid(self):
        for child in self.grid.get_children():
            self.grid.remove(child)

        row = col = 0
        iter_ = self.filterModel.get_iter_first()

        while iter_:
            item = self.filterModel[iter_][1]

            btn = self._buildItemButton(item)
            self.grid.attach(btn, col, row, 1, 1)

            col += 1
            if col >= self.columns:
                col = 0
                row += 1

            iter_ = self.filterModel.iter_next(iter_)

        self.grid.show_all()

    def _buildItemButton(self, item):
        btn = Gtk.Button()
        box = Gtk.Box(spacing=6)

        image = Gtk.Image.new_from_pixbuf(self.getItemPixbuf(item))
        label = Gtk.Label(label=self.getItemLabel(item))

        box.pack_start(image, False, False, 0)
        box.pack_start(label, True, True, 0)

        btn.add(box)
        btn.connect("clicked", self._onItemClicked, item)

        return btn

    def _onItemClicked(self, button, item):
        self.emit("item-selected", item)
        self.popover.hide()

    def shouldIncludeItem(self, item):
        return True
    
    def set_relative_to(self, widget):
        self.popover.set_relative_to(widget)

    def set_pointing_to(self, widget):
        self.popover.set_pointing_to(widget)

    def set_position(self, position: Gtk.PositionType):
        self.popover.set_position(position)

    def show(self, *args, **kwargs):
        self.store.clear()

        for item in self.getItems():
            if not self.shouldIncludeItem(item):
                continue

            self.store.append(
                None,
                [self.getItemFilterKey(item), item]
            )

        self.currentFilter = None
        self._refresh()
        self.popover.show_all()
        self.popover.popup()