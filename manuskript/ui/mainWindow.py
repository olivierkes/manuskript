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
from manuskript.ui.startupWindow import StartupWindow
from manuskript.ui.util import bindMenuItem


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
        self.charactersView = MainWindow.packViewIntoSlot(builder, "characters_slot", CharactersView, self.project) # Just project because we need it for characters and the template
        self.plotView = MainWindow.packViewIntoSlot(builder, "plot_slot", PlotView, self.project.plots)
        self.worldView = MainWindow.packViewIntoSlot(builder, "world_slot", WorldView, self.project.world)
        self.outlineView = MainWindow.packViewIntoSlot(builder, "outline_slot", OutlineView, self.project.outline)
        self.editorView = MainWindow.packViewIntoSlot(builder, "editor_slot", EditorView, self.project)

        self.startupWindow = StartupWindow(self)
        self.aboutDialog = AboutDialog(self)
        self.frequencyWindow = FrequencyWindow(self)
        self.character_template_window = CharacterTemplateEditorWindow(self)
        self.settingsWindow = SettingsWindow(self)

        self.windows = [
            self.startupWindow,
            self.aboutDialog,
            self.frequencyWindow,
            self.character_template_window,
            self.settingsWindow
        ]

        bindMenuItem(builder, "open_menu_item", self.openAction)
        bindMenuItem(builder, "save_menu_item", self.saveAction)
        bindMenuItem(builder, "close_menu_item", self.closeAction)
        bindMenuItem(builder, "quit_menu_item", self.quitAction)

        bindMenuItem(builder, "settings_menu_item", self.settingsAction)
        bindMenuItem(builder, "frequency_menu_item", self.frequencyAction)
        bindMenuItem(builder, "character_details_template_editor", self.character_details_template_editor_action)
        bindMenuItem(builder, "about_menu_item", self.aboutAction)

    def getProject(self):
        return self.project

    def openAction(self, menuItem: Gtk.MenuItem):
        pass

    def saveAction(self, menuItem: Gtk.MenuItem):
        self.getProject().save()

    def closeAction(self, menuItem: Gtk.MenuItem):
        self.hide()
        self.startupWindow.show()

    def quitAction(self, menuItem: Gtk.MenuItem):
        for window in self.windows:
            window.hide()

        self.exit()

    def getSettings(self):
        return self.getProject().settings

    def settingsAction(self, menuItem: Gtk.MenuItem):
        self.settingsWindow.show()

    def frequencyAction(self, menuItem: Gtk.MenuItem):
        self.frequencyWindow.show()
        
    def character_details_template_editor_action(self, menuItem: Gtk.MenuItem):
        self.character_template_window.show()

    def aboutAction(self, menuItem: Gtk.MenuItem):
        self.aboutDialog.show()

    def show(self):
        self.window.show_all()

    def hide(self):
        self.window.hide()

    def isVisible(self):
        return self.window.get_property("visible")

    def run(self):
        self.show()
        Gtk.main()

    def exit(self):
        for window in self.windows:
            if window.isVisible():
                self.hide()
                return

        self.window.destroy()

    def _notify(self, obj: GObject.Object, pspec: GObject.ParamSpec):
        print(pspec.name + " = " + str(obj.get_property(pspec.name)))
