#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any

from gi.repository import GObject, Gtk, Handy

from manuskript.ui.abstractDialog import AbstractDialog
from manuskript.data import Project

class ImportWindow(AbstractDialog):
    def __init__(self, mainWindow: Any) -> None:
        AbstractDialog.__init__(self, mainWindow, "ui/import.glade", "import_window")

        self.headerBar: Gtk.HeaderBar = None
        self.back: Gtk.Button = None
        self.forward: Gtk.Button = None
        self.previewLeaflet: Handy.Leaflet = None

    def initWindow(self, builder: Gtk.Builder, window: Any) -> None:
        self.headerBar = builder.get_object("header_bar")
        self.back = builder.get_object("back")
        self.forward = builder.get_object("forward")
        self.previewLeaflet = builder.get_object("preview_leaflet")

        self.previewLeaflet.bind_property(
            "folded", self.back, "visible", GObject.BindingFlags.SYNC_CREATE
        )
        self.previewLeaflet.bind_property(
            "folded", self.forward, "visible", GObject.BindingFlags.SYNC_CREATE
        )
        self.previewLeaflet.bind_property(
            "folded",
            self.headerBar,
            "show-close-button",
            GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.INVERT_BOOLEAN,
        )

        self.back.connect("clicked", self._backClicked)
        self.forward.connect("clicked", self._forwardClicked)

    def _backClicked(self, button: Gtk.Button) -> None:
        if self.previewLeaflet.get_visible_child_name() == "preview_box":
            self.previewLeaflet.set_visible_child_name("settings_box")
        else:
            self.hide()

    def _forwardClicked(self, button: Gtk.Button) -> None:
        if self.previewLeaflet.get_visible_child_name() == "settings_box":
            self.previewLeaflet.set_visible_child_name("preview_box")
