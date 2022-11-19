#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

from manuskript.data import OutlineItem
from manuskript.ui.util import iconByOutlineItemType
from manuskript.util import validString


class GridItem:

    def __init__(self, outlineItem: OutlineItem):
        self.outlineItem = outlineItem

        builder = Gtk.Builder()
        builder.add_from_file("ui/editor/grid-item.glade")

        self.widget = builder.get_object("grid_item")

        self.iconImage = builder.get_object("icon")
        self.titleLabel = builder.get_object("title")
        self.summaryLabel = builder.get_object("summary")

        self.reloadOutlineItem()

    def reloadOutlineItem(self):
        icon = iconByOutlineItemType(self.outlineItem)

        self.iconImage.set_from_icon_name(icon, Gtk.IconSize.MENU)
        self.titleLabel.set_text(validString(self.outlineItem.title))
        self.summaryLabel.set_text(validString(self.outlineItem.summaryFull))

    def show(self):
        self.widget.show_all()
