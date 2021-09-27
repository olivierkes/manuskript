#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Handy

Handy.init()

from manuskript.data import Settings


class GeneralPage:

    def __init__(self, settings: Settings):
        self.settings = settings

        builder = Gtk.Builder()
        builder.add_from_file("ui/settings/general.glade")

        self.widget = builder.get_object("general_page")

        self.autoSave = builder.get_object("auto_save")
        self.autoSaveDelay = builder.get_object("auto_save_delay")
        self.autoSaveNoChanges = builder.get_object("auto_save_nochanges")
        self.autoSaveNoChangesDelay = builder.get_object("auto_save_nochanges_delay")
        self.saveOnQuit = builder.get_object("save_on_quit")
        self.saveToZip = builder.get_object("save_to_zip")

        self.autoSave.set_active(self.settings.get("autoSave"))
        self.autoSaveDelay.set_value(self.settings.get("autoSaveDelay"))
        self.autoSaveNoChanges.set_active(self.settings.get("autoSaveNoChanges"))
        self.autoSaveNoChangesDelay.set_value(self.settings.get("autoSaveNoChangesDelay"))
        self.saveOnQuit.set_active(self.settings.get("saveOnQuit"))
        self.saveToZip.set_active(self.settings.get("saveToZip"))

        self.autoSave.connect("toggled", self._autoSaveToggled)
        self.autoSaveDelay.connect("value-changed", self._autoSaveChanged)
        self.autoSaveNoChanges.connect("toggled", self._autoSaveNoChangesToggled)
        self.autoSaveNoChangesDelay.connect("value-changed", self._autoSaveNoChangesChanged)
        self.saveOnQuit.connect("toggled", self._saveOnQuitToggled)
        self.saveToZip.connect("toggled", self._saveToZipToggled)

    def _autoSaveToggled(self, button: Gtk.ToggleButton):
        self.settings.set("autoSave", button.get_active())

    def _autoSaveChanged(self, button: Gtk.SpinButton):
        self.settings.set("autoSaveDelay", button.get_value())

    def _autoSaveNoChangesToggled(self, button: Gtk.ToggleButton):
        self.settings.set("autoSaveNoChanges", button.get_active())

    def _autoSaveNoChangesChanged(self, button: Gtk.SpinButton):
        self.settings.set("autoSaveNoChangesDelay", button.get_value())

    def _saveOnQuitToggled(self, button: Gtk.ToggleButton):
        self.settings.set("saveOnQuit", button.get_active())

    def _saveToZipToggled(self, button: Gtk.ToggleButton):
        self.settings.set("saveToZip", button.get_active())
