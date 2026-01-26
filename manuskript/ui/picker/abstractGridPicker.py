#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk, GObject

from typing import Iterable, Optional, Any


class AbstractGridPicker(Gtk.Box):
    __gsignals__ = {
        "item-selected": (GObject.SignalFlags.RUN_FIRST, None, (object,))
    }

    def __init__(self, *, button: Gtk.Button=None, enableSearch: bool=True, filters: Optional[Iterable]=None, columns: int=3):
        super().__init__()

        self.columns: int = columns
        self.filters: Optional[Iterable] = filters
        self.currentFilter = None
        self.searchText: str = ""

        self.store: Gtk.TreeStore = Gtk.TreeStore(GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT)
        self.filterModel: Gtk.TreeModelFilter = self.store.filter_new()
        self.filterModel.set_visible_func(self._filterFunc)

        builder: Gtk.Builder = Gtk.Builder()
        builder.add_from_file("ui/gridpicker/picker.glade")

        self.popover = builder.get_object("popover")
        self.grid = builder.get_object("grid")
        self.searchEntry = builder.get_object("search_entry")
        self.filterBox = builder.get_object("filter_box")

        if button:
            self.popover.set_relative_to(button)

        if enableSearch:
            self.searchEntry.connect("search-changed", self._searchEntryChanged)
        else:
            self.searchEntry.hide()

        if filters:
            self.setupFilters()
        else:
            self.filterBox.hide()

    def getItems(self):
        raise NotImplementedError

    def getItemLabel(self, item: Any) -> str:
        raise NotImplementedError

    def getItemPixbuf(self, item: Any):
        raise NotImplementedError

    def getItemFilterKey(self, item: Any):
        return None

    def _filterFunc(self, model, iter_, data=None):
        filterKey, item = model[iter_]

        if self.currentFilter is not None and filterKey != self.currentFilter:
            return False

        if self.searchText:
            return self.searchText.lower() in self.getItemLabel(item).lower()

        return True

    def _searchEntryChanged(self, entry: Gtk.Entry):
        self.searchText = entry.get_text()
        self.refresh()

    def setupFilters(self):
        self.cssProvider = Gtk.CssProvider()
        self.cssProvider.load_from_data(b"""
            .highlighted-button {
                border: 2px solid #000000;
            }
        """)

        self.lastClickedButton = None

        buttons = [("All", None)]

        if hasattr(self.filters, "__iter__"):
            if hasattr(self.filters, "__members__"):
                buttons += [
                    (f.name.capitalize(), f) for f in reversed(self.filters)
                ]
            else:
                buttons += self.filters

        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(),
            self.cssProvider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        for label, value in buttons:
            btn = Gtk.Button(label=label)

            if value is None:
                self.highlight(btn)

            btn.connect("clicked", self._filterButtonClicked, value)
            self.filterBox.pack_start(btn, False, False, 0)

    def _filterButtonClicked(self, button: Gtk.Button, value: Any):
        self.highlight(button)
        self.currentFilter = value
        self.refresh()

    def highlight(self, button: Gtk.Button):
        if self.lastClickedButton:
            self.lastClickedButton.get_style_context().remove_class("highlighted-button")

        button.get_style_context().add_class("highlighted-button")
        self.lastClickedButton = button

    def refresh(self):
        self.filterModel.refilter()
        self.rebuildGrid()

    def rebuildGrid(self):
        for child in self.grid.get_children():
            self.grid.remove(child)

        row = col = 0
        iter_ = self.filterModel.get_iter_first()

        while iter_:
            item = self.filterModel[iter_][1]

            btn = self.buildItemButton(item)
            self.grid.attach(btn, col, row, 1, 1)

            col += 1
            if col >= self.columns:
                col = 0
                row += 1

            iter_ = self.filterModel.iter_next(iter_)

        self.grid.show_all()

    def buildItemButton(self, item: Any):
        btn = Gtk.Button()
        box = Gtk.Box(spacing=6)

        image = Gtk.Image.new_from_pixbuf(self.getItemPixbuf(item))
        label = Gtk.Label(label=self.getItemLabel(item))

        box.pack_start(image, False, False, 0)
        box.pack_start(label, True, True, 0)

        btn.add(box)
        btn.connect("clicked", self._itemButtonClicked, item)

        return btn

    def _itemButtonClicked(self, button: Gtk.Button, item: Any):
        self.emit("item-selected", item)
        self.popover.hide()

    def shouldIncludeItem(self, item: Any):
        return True
    
    def set_relative_to(self, widget: Gtk.Widget):
        self.popover.set_relative_to(widget)

    def set_pointing_to(self, widget: Gtk.Widget):
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
        self.refresh()
        self.popover.show_all()
        self.popover.popup()