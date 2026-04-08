#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk, Handy

from manuskript.data import Settings, SettingsKeys
from manuskript.ui.settings.abstractPage import AbstractPage


class RevisionsPage(AbstractPage):

    def __init__(self, settings: Settings):
        self.settings = settings

        builder = Gtk.Builder()
        builder.add_from_file("ui/settings/revisions.glade")

        self.widget = builder.get_object("revisions_page")

        self.revisionsKeep: Gtk.ToggleButton = builder.get_object("revisions_keep")
        self.revisionsSmartremove: Gtk.ToggleButton = builder.get_object("revisions_smartremove")
        self.revisionPerMinute: Gtk.SpinButton = builder.get_object("revisions_per_minute")
        self.revisionPer10Minutes: Gtk.SpinButton = builder.get_object("revisions_per_10_minutes")
        self.revisionPerHour: Gtk.SpinButton = builder.get_object("revisions_per_hour")
        self.revisionPerDay: Gtk.SpinButton = builder.get_object("revisions_per_day")
        self.revisionPerWeek: Gtk.SpinButton = builder.get_object("revisions_per_week")

        self.revisionsKeep.set_active(self.settings.get(SettingsKeys.Revisions.KEEP))
        self.revisionsSmartremove.set_active(self.settings.get(SettingsKeys.Revisions.SMARTREMOVE))
        self.revisionPerMinute.set_value(self.settings.get(SettingsKeys.Revisions.Rules.DELAY_PER_MINUTE))
        self.revisionPer10Minutes.set_value(self.settings.get(SettingsKeys.Revisions.Rules.DELAY_PER_10_MINUTES))
        self.revisionPerHour.set_value(self.settings.get(SettingsKeys.Revisions.Rules.DELAY_PER_HOUR))
        self.revisionPerDay.set_value(self.settings.get(SettingsKeys.Revisions.Rules.DELAY_PER_DAY))
        self.revisionPerWeek.set_value(self.settings.get(SettingsKeys.Revisions.Rules.DELAY_PER_WEEK))

        self.revisionsKeep.connect("toggled", self._genericToggleButtonToggled, SettingsKeys.Revisions.KEEP)
        self.revisionsSmartremove.connect("toggled", self._genericToggleButtonToggled, SettingsKeys.Revisions.SMARTREMOVE)
        self.revisionPerMinute.connect("value-changed", self._genericSpinButtonValueChanged, SettingsKeys.Revisions.Rules.DELAY_PER_MINUTE)
        self.revisionPer10Minutes.connect("value-changed", self._genericSpinButtonValueChanged, SettingsKeys.Revisions.Rules.DELAY_PER_10_MINUTES)
        self.revisionPerHour.connect("value-changed", self._genericSpinButtonValueChanged, SettingsKeys.Revisions.Rules.DELAY_PER_HOUR)
        self.revisionPerDay.connect("value-changed", self._genericSpinButtonValueChanged, SettingsKeys.Revisions.Rules.DELAY_PER_DAY)
        self.revisionPerWeek.connect("value-changed", self._genericSpinButtonValueChanged, SettingsKeys.Revisions.Rules.DELAY_PER_WEEK)
