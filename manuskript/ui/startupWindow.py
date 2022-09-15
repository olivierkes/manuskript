#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk, Handy

from manuskript.ui.abstractDialog import AbstractDialog


class StartupWindow(AbstractDialog):

    def __init__(self, mainWindow):
        AbstractDialog.__init__(self, mainWindow, "ui/startup.glade", "startup_window")

        self.headerBar = None
        self.templateLeaflet = None

    def initWindow(self, builder, window):
        self.headerBar = builder.get_object("header_bar")
        self.templateLeaflet = builder.get_object("template_leaflet")

        self.templateLeaflet.bind_property("folded", self.headerBar, "show-close-button",
                                           GObject.BindingFlags.SYNC_CREATE |
                                           GObject.BindingFlags.INVERT_BOOLEAN)
