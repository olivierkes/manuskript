#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk
from manuskript.data import Settings
from manuskript.ui.util import rgbaToHex

class AbstractPage:
    settings: Settings

    def setActiveComboItem(self, combobox: Gtk.ComboBox, value: str, column: int):
        model = combobox.get_model()

        row: Gtk.TreeModelRow
        for i, row in enumerate(model):
            if row[column] == value:
                combobox.set_active(i)

    def getComboSelectedValue(self, combobox: Gtk.ComboBox, column: int):
        tree_iter = combobox.get_active_iter()

        if tree_iter is None:
            return

        model = combobox.get_model()
        return model[tree_iter][column]

    def connectRadioButton(self, signal, radioButtons: dict, handler):
        for radioButton in radioButtons:
            radioWidget = radioButtons[radioButton][0]
            
            radioWidget.connect(signal, handler)

    def setRadioButtonValue(self, radioButtons: dict, value):
        
        for radioButton in radioButtons:
            radioWidget = radioButtons[radioButton][0]
            radioSettingsValue = radioButtons[radioButton][1]
            
            if radioSettingsValue==value:
                radioWidget.set_active(True)

    def _genericSpinButtonValueChanged(self, button: Gtk.SpinButton, settingsKey: str):
        self.settings.set(settingsKey, button.get_value_as_int())

    def _genericComboChanged(self, combo: Gtk.ComboBox, userData: dict):
        value = self.getComboSelectedValue(combo, userData["column"])
        self.settings.set(userData["settingsKey"], value)

    def _genericToggleButtonGroupToggled(self, toggleButton: Gtk.ToggleButton, *args):
        if toggleButton.get_active():
            self.settings.set(args[1], args[0])

    def _genericToggleButtonToggled(self, toggleButton: Gtk.ToggleButton, settingsKey):
        self.settings.set(settingsKey, toggleButton.get_active())

    def _genericColorButtonColorSet(self, button: Gtk.ColorButton, settingsKey):
        self.settings.set(settingsKey, rgbaToHex(button.get_rgba()))

