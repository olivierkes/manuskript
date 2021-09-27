#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Handy

Handy.init()

from manuskript.data import Settings


class RevisionsPage:

    def __init__(self, settings: Settings):
        self.settings = settings

        builder = Gtk.Builder()
        builder.add_from_file("ui/settings/revisions.glade")

        self.widget = builder.get_object("revisions_page")

        self.revisionsKeep = builder.get_object("revisions_keep")
        self.revisionsSmartremove = builder.get_object("revisions_smartremove")

        self.revisionsKeep.set_active(self.settings.get("revisions.keep"))
        self.revisionsSmartremove.set_active(self.settings.get("revisions.smartremove"))

        self.revisionsKeep.connect("toggled", self._revisionsKeepToggled)
        self.revisionsSmartremove.connect("toggled", self._revisionsSmartremoveToggled)

    def _revisionsKeepToggled(self, button: Gtk.ToggleButton):
        self.settings.set("revisions.keep", button.get_active())

    def _revisionsSmartremoveToggled(self, button: Gtk.ToggleButton):
        self.settings.set("revisions.smartremove", button.get_active())
