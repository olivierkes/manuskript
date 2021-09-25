#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from manuskript.ui.abstractDialog import AbstractDialog


class SettingsWindow(AbstractDialog):

    def __init__(self, mainWindow):
        AbstractDialog.__init__(self, mainWindow, "ui/settings.glade", "settings_window")

    def initWindow(self, builder, window):
        self.autoSave = builder.get_object("auto_save")
        self.autoSaveDelay = builder.get_object("auto_save_delay")
        self.autoSaveNoChanges = builder.get_object("auto_save_nochanges")
        self.autoSaveNoChangesDelay = builder.get_object("auto_save_nochanges_delay")
        self.saveOnQuit = builder.get_object("save_on_quit")
        self.saveToZip = builder.get_object("save_to_zip")

        self.revisionsKeep = builder.get_object("revisions_keep")
        self.revisionsSmartremove = builder.get_object("revisions_smartremove")

        self.autoSave.set_active(self.getSettings().get("autoSave"))
        self.autoSaveDelay.set_value(self.getSettings().get("autoSaveDelay"))
        self.autoSaveNoChanges.set_active(self.getSettings().get("autoSaveNoChanges"))
        self.autoSaveNoChangesDelay.set_value(self.getSettings().get("autoSaveNoChangesDelay"))
        self.saveOnQuit.set_active(self.getSettings().get("saveOnQuit"))
        self.saveToZip.set_active(self.getSettings().get("saveToZip"))

        self.revisionsKeep.set_active(self.getSettings().get("revisions.keep"))
        self.revisionsSmartremove.set_active(self.getSettings().get("revisions.smartremove"))

        self.autoSave.connect("toggled", self._autoSaveToggled)
        self.autoSaveDelay.connect("value-changed", self._autoSaveChanged)
        self.autoSaveNoChanges.connect("toggled", self._autoSaveNoChangesToggled)
        self.autoSaveNoChangesDelay.connect("value-changed", self._autoSaveNoChangesChanged)
        self.saveOnQuit.connect("toggled", self._saveOnQuitToggled)
        self.saveToZip.connect("toggled", self._saveToZipToggled)

        self.revisionsKeep.connect("toggled", self._revisionsKeepToggled)
        self.revisionsSmartremove.connect("toggled", self._revisionsSmartremoveToggled)

    def _autoSaveToggled(self, button: Gtk.ToggleButton):
        self.getSettings().set("autoSave", button.get_active())

    def _autoSaveChanged(self, button: Gtk.SpinButton):
        self.getSettings().set("autoSaveDelay", button.get_value())

    def _autoSaveNoChangesToggled(self, button: Gtk.ToggleButton):
        self.getSettings().set("autoSaveNoChanges", button.get_active())

    def _autoSaveNoChangesChanged(self, button: Gtk.SpinButton):
        self.getSettings().set("autoSaveNoChangesDelay", button.get_value())

    def _saveOnQuitToggled(self, button: Gtk.ToggleButton):
        self.getSettings().set("saveOnQuit", button.get_active())

    def _saveToZipToggled(self, button: Gtk.ToggleButton):
        self.getSettings().set("saveToZip", button.get_active())

    def _revisionsKeepToggled(self, button: Gtk.ToggleButton):
        self.getSettings().set("revisions.keep", button.get_active())

    def _revisionsSmartremoveToggled(self, button: Gtk.ToggleButton):
        self.getSettings().set("revisions.smartremove", button.get_active())

    def getSettings(self):
        return self.mainWindow.getSettings()
