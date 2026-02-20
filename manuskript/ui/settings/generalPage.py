#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk, Handy

from manuskript.data import Settings, SettingsKeys
from manuskript.util import AppSettings, AppSettingsKeys
from manuskript.ui.settings.abstractPage import AbstractPage


class GeneralPage(AbstractPage):

    def __init__(self, settings: Settings):
        self.settings = settings
        self.appSettings = AppSettings()

        builder = Gtk.Builder()
        builder.add_from_file("ui/settings/general.glade")
        
        self.widget = builder.get_object("general_page")

        self.generalLanguage: Gtk.ComboBox = builder.get_object("general_language")
        self.generalFontSize: Gtk.SpinButton = builder.get_object("general_font_size")
        self.automaticLoad: Gtk.ToggleButton = builder.get_object("automatic_load")
        self.autoSave: Gtk.ToggleButton = builder.get_object("auto_save")
        self.autoSaveDelay: Gtk.SpinButton = builder.get_object("auto_save_delay")
        self.autoSaveNoChanges: Gtk.ToggleButton = builder.get_object("auto_save_nochanges")
        self.autoSaveNoChangesDelay: Gtk.SpinButton = builder.get_object("auto_save_nochanges_delay")
        self.saveOnQuit: Gtk.ToggleButton = builder.get_object("save_on_quit")
        self.saveToZip: Gtk.ToggleButton = builder.get_object("save_to_zip")

        self.setActiveComboItem(self.generalLanguage, self.appSettings.getValue(AppSettingsKeys.GENERAL_LANGUAGE), 0)
        self.generalFontSize.set_value(self.appSettings.getValue(AppSettingsKeys.GENERAL_FONTSIZE))
        self.automaticLoad.set_active(self.appSettings.getValue(AppSettingsKeys.AUTOMATIC_LOAD))
        self.autoSave.set_active(self.settings.get(SettingsKeys.AUTO_SAVE))
        self.autoSaveDelay.set_value(self.settings.get(SettingsKeys.AUTO_SAVE_DELAY))
        self.autoSaveNoChanges.set_active(self.settings.get(SettingsKeys.AUTO_SAVE_NO_CHANGES))
        self.autoSaveNoChangesDelay.set_value(self.settings.get(SettingsKeys.AUTO_SAVE_NO_CHANGES_DELAY))
        self.saveOnQuit.set_active(self.settings.get(SettingsKeys.SAVE_ON_QUIT))
        self.saveToZip.set_active(self.settings.get(SettingsKeys.SAVE_TO_ZIP))

        self.generalLanguage.connect("changed", self._generalLanguageChanged)
        self.generalFontSize.connect("value-changed", self._generalFontSizeChanged)
        self.automaticLoad.connect("toggled", self._automaticLoadToggled)
        self.autoSave.connect("toggled", self._genericToggleButtonToggled, SettingsKeys.AUTO_SAVE)
        self.autoSaveDelay.connect("value-changed", self._genericSpinButtonValueChanged, SettingsKeys.AUTO_SAVE_DELAY)
        self.autoSaveNoChanges.connect("toggled", self._genericToggleButtonToggled, SettingsKeys.AUTO_SAVE_NO_CHANGES)
        self.autoSaveNoChangesDelay.connect("value-changed", self._genericSpinButtonValueChanged, SettingsKeys.AUTO_SAVE_NO_CHANGES_DELAY)
        self.saveOnQuit.connect("toggled", self._genericToggleButtonToggled, SettingsKeys.SAVE_ON_QUIT)
        self.saveToZip.connect("toggled", self._genericToggleButtonToggled, SettingsKeys.SAVE_TO_ZIP)

    def _generalLanguageChanged(self, combo: Gtk.ComboBox):
        tree_iter = combo.get_active_iter()

        if tree_iter is None:
            return

        model = combo.get_model()
        value = model[tree_iter][0]

        self.appSettings.setValue(AppSettingsKeys.GENERAL_LANGUAGE, value)

    def _generalFontSizeChanged(self, button: Gtk.SpinButton):
        self.appSettings.setValue(AppSettingsKeys.GENERAL_FONTSIZE, button.get_value_as_int())

    def _automaticLoadToggled(self, button: Gtk.ToggleButton):
        self.appSettings.setValue(AppSettingsKeys.AUTOMATIC_LOAD, button.get_active())
