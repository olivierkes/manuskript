#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Handy", "1")

from gi.repository import GObject, Gtk, Handy

Handy.init()

from manuskript.data import Project
from manuskript.ui.views import *

from manuskript.ui.tools import *
from manuskript.ui.aboutDialog import AboutDialog
from manuskript.ui.settingsWindow import SettingsWindow


class MainWindow:

    @classmethod
    def packViewIntoSlot(cls, builder, id, view_cls, data=None):
        slot = builder.get_object(id)

        if slot is None:
            return None

        try:
            if data is None:
                view = view_cls()
            else:
                view = view_cls(data)
        except Exception:
            return None

        if view.widget is None:
            return None

        slot.pack_start(view.widget, True, True, 0)
        return view

    @classmethod
    def bindMenuItem(cls, builder, id, action):
        menuItem = builder.get_object(id)

        if menuItem is None:
            return

        menuItem.connect("activate", action)

    def __init__(self, path):
        self.project = Project(path)
        self.project.load()

        builder = Gtk.Builder()
        builder.add_from_file("ui/main.glade")

        self.window = builder.get_object("main_window")
        self.window.connect("destroy", Gtk.main_quit)

        self.headerBar = builder.get_object("header_bar")
        self.leaflet = builder.get_object("leaflet")
        self.viewSwitcherBar = builder.get_object("view_switcher_bar")

        self.headerBar.set_subtitle(self.project.info.title)

        self.leaflet.bind_property("folded", self.viewSwitcherBar, "reveal", GObject.BindingFlags.SYNC_CREATE)
        self.leaflet.bind_property("folded", self.headerBar, "show-close-button", GObject.BindingFlags.SYNC_CREATE |
                                   GObject.BindingFlags.INVERT_BOOLEAN)

        self.generalView = MainWindow.packViewIntoSlot(builder, "general_slot", GeneralView, self.project.info)
        self.summaryView = MainWindow.packViewIntoSlot(builder, "summary_slot", SummaryView, self.project.summary)
        self.charactersView = MainWindow.packViewIntoSlot(builder, "characters_slot", CharactersView, self.project.characters)
        self.plotView = MainWindow.packViewIntoSlot(builder, "plot_slot", PlotView)
        self.worldView = MainWindow.packViewIntoSlot(builder, "world_slot", WorldView)
        self.outlineView = MainWindow.packViewIntoSlot(builder, "outline_slot", OutlineView)
        self.editorView = MainWindow.packViewIntoSlot(builder, "editor_slot", EditorView)

        self.aboutDialog = AboutDialog(self)
        self.frequencyWindow = FrequencyWindow(self)
        self.settingsWindow = SettingsWindow(self)

        MainWindow.bindMenuItem(builder, "settings_menu_item", self.openSettings)
        MainWindow.bindMenuItem(builder, "frequency_menu_item", self.openFrequency)
        MainWindow.bindMenuItem(builder, "about_menu_item", self.openAbout)

    def getProject(self):
        return self.project

    def getSettings(self):
        return self.getProject().settings

    def openSettings(self, menuItem: Gtk.MenuItem):
        self.settingsWindow.show()

    def openFrequency(self, menuItem: Gtk.MenuItem):
        self.frequencyWindow.show()

    def openAbout(self, menuItem: Gtk.MenuItem):
        self.aboutDialog.show()

    def show(self):
        self.window.show_all()

    def hide(self):
        self.window.hide()

    def run(self):
        self.show()
        Gtk.main()

    def _notifyProperty(self, window, property):
        print(property.name)
