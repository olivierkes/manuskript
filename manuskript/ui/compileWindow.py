#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk, Handy

Handy.init()

from manuskript.ui.abstractDialog import AbstractDialog

from manuskript.data import Project


class CompileWindow(AbstractDialog):

    def __init__(self, mainWindow):
        AbstractDialog.__init__(self, mainWindow, "ui/compile.glade", "compile_window")

        self.headerBar = None
        self.back = None
        self.forward = None
        self.previewLeaflet = None
        self.manageExportersButton = None

    def initWindow(self, builder, window):
        self.headerBar = builder.get_object("header_bar")
        self.back = builder.get_object("back")
        self.forward = builder.get_object("forward")
        self.previewLeaflet = builder.get_object("preview_leaflet")
        self.manageExportersButton = builder.get_object("manage_exporters")

        self.previewLeaflet.bind_property("folded", self.back, "visible",
                                          GObject.BindingFlags.SYNC_CREATE)
        self.previewLeaflet.bind_property("folded", self.forward, "visible",
                                          GObject.BindingFlags.SYNC_CREATE)
        self.previewLeaflet.bind_property("folded", self.headerBar, "show-close-button",
                                          GObject.BindingFlags.SYNC_CREATE |
                                          GObject.BindingFlags.INVERT_BOOLEAN)
        
        self.back.connect("clicked", self._backClicked)
        self.forward.connect("clicked", self._forwardClicked)
    
    def _backClicked(self, button: Gtk.Button):
        if self.previewLeaflet.get_visible_child_name() == "preview_box":
            self.previewLeaflet.set_visible_child_name("settings_box")
        else:
            self.hide()
    
    def _forwardClicked(self, button: Gtk.Button):
        if self.previewLeaflet.get_visible_child_name() == "settings_box":
            self.previewLeaflet.set_visible_child_name("preview_box")
