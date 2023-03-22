#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Handy", "1")

from gi.repository import GObject, Gtk, Handy

Handy.init()

from manuskript.data import Project
from manuskript.ui.views import *

from manuskript.ui.chooser import openFileDialog, saveFileDialog, FileFilter
from manuskript.ui.tools import *
from manuskript.ui.aboutDialog import AboutDialog
from manuskript.ui.settingsWindow import SettingsWindow
from manuskript.ui.startupWindow import StartupWindow
from manuskript.ui.util import bindMenuItem, packViewIntoSlot, unpackFromSlot
from manuskript.util import parseFilenameFromURL


class MainWindow:

    def __init__(self):
        self.project = None

        builder = Gtk.Builder()
        builder.add_from_file("ui/main.glade")

        self.window = builder.get_object("main_window")
        self.window.connect("destroy", Gtk.main_quit)

        self.headerBar = builder.get_object("header_bar")
        self.leaflet = builder.get_object("leaflet")
        self.viewSwitcherBar = builder.get_object("view_switcher_bar")

        self.leaflet.bind_property("folded", self.viewSwitcherBar, "reveal", GObject.BindingFlags.SYNC_CREATE)
        self.leaflet.bind_property("folded", self.headerBar, "show-close-button", GObject.BindingFlags.SYNC_CREATE |
                                   GObject.BindingFlags.INVERT_BOOLEAN)

        self.generalSlot = builder.get_object("general_slot")
        self.summarySlot = builder.get_object("summary_slot")
        self.charactersSlot = builder.get_object("characters_slot")
        self.plotSlot = builder.get_object("plot_slot")
        self.worldSlot = builder.get_object("world_slot")
        self.outlineSlot = builder.get_object("outline_slot")
        self.editorSlot = builder.get_object("editor_slot")

        self.generalView = None
        self.summaryView = None
        self.charactersView = None
        self.plotView = None
        self.worldView = None
        self.outlineView = None
        self.editorView = None

        self.startupWindow = StartupWindow(self)
        self.aboutDialog = AboutDialog(self)
        self.frequencyWindow = FrequencyWindow(self)
        self.settingsWindow = SettingsWindow(self)

        self.windows = [
            self.startupWindow,
            self.aboutDialog,
            self.frequencyWindow,
            self.settingsWindow
        ]

        self.recentChooserMenu = builder.get_object("recent_chooser_menu")
        self.recentChooserMenu.connect("item-activated", self._recentAction)

        bindMenuItem(builder, "open_menu_item", self._openAction)
        bindMenuItem(builder, "save_menu_item", self._saveAction)
        bindMenuItem(builder, "saveas_menu_item", self._saveAsAction)
        bindMenuItem(builder, "close_menu_item", self._closeAction)
        bindMenuItem(builder, "quit_menu_item", self._quitAction)

        bindMenuItem(builder, "settings_menu_item", self._settingsAction)
        bindMenuItem(builder, "frequency_menu_item", self._frequencyAction)
        bindMenuItem(builder, "character_details_template_editor", self._characterDetailsTemplateEditorAction)
        bindMenuItem(builder, "about_menu_item", self._aboutAction)

        self.hide()

    def getProject(self):
        return self.project

    def openProject(self, path=None):
        if self.project is not None:
            self.closeProject()

        if path is None:
            return

        self.project = Project(path)
        self.project.load()

        self.headerBar.set_subtitle(self.project.info.title)

        self.generalView = packViewIntoSlot(self.generalSlot, GeneralView, self.project.info)
        self.summaryView = packViewIntoSlot(self.summarySlot, SummaryView, self.project.summary)
        self.charactersView = packViewIntoSlot(self.charactersSlot, CharactersView, self.project.characters)
        self.plotView = packViewIntoSlot(self.plotSlot, PlotView, self.project.plots)
        self.worldView = packViewIntoSlot(self.worldSlot, WorldView, self.project.world)
        self.outlineView = packViewIntoSlot(self.outlineSlot, OutlineView, self.project.outline)
        self.editorView = packViewIntoSlot(self.editorSlot, EditorView, self.project)

        self.startupWindow.hide()
        self.show()

    def closeProject(self):
        if self.project is not None:
            self.generalView = unpackFromSlot(self.generalSlot, self.generalView)
            self.summaryView = unpackFromSlot(self.summarySlot, self.summaryView)
            self.charactersView = unpackFromSlot(self.charactersSlot, self.charactersView)
            self.plotView = unpackFromSlot(self.plotSlot, self.plotView)
            self.worldView = unpackFromSlot(self.worldSlot, self.worldView)
            self.outlineView = unpackFromSlot(self.outlineSlot, self.outlineView)
            self.editorView = unpackFromSlot(self.editorSlot, self.editorView)

            del self.project
            self.project = None

        self.hide()
        self.startupWindow.show()

    def _openAction(self, menuItem: Gtk.MenuItem):
        path = openFileDialog(self.window, FileFilter("Manuskript project", "msk"))
        if path is None:
            return

        self.openProject(path)

    def _recentAction(self, recentChooser: Gtk.RecentChooser):
        uri = recentChooser.get_current_uri()
        if uri is None:
            return

        path = parseFilenameFromURL(uri)
        if path is None:
            return

        self.openProject(path)

    def _saveAction(self, menuItem: Gtk.MenuItem):
        self.project.save()

    def _saveAsAction(self, menuItem: Gtk.MenuItem):
        path = saveFileDialog(self.window, FileFilter("Manuskript project", "msk"))
        if path is None:
            return

        self.project.changePath(path)
        self.project.save()

    def _closeAction(self, menuItem: Gtk.MenuItem):
        self.closeProject()

    def _quitAction(self, menuItem: Gtk.MenuItem):
        self.exit(True)

    def getSettings(self):
        return self.project.settings

    def _settingsAction(self, menuItem: Gtk.MenuItem):
        self.settingsWindow.show()

    def _frequencyAction(self, menuItem: Gtk.MenuItem):
        self.frequencyWindow.show()
        
    def _characterDetailsTemplateEditorAction(self, menuItem: Gtk.MenuItem):
        self.characterTemplateWindow.show()

    def _aboutAction(self, menuItem: Gtk.MenuItem):
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

    def exit(self, force=False):
        if force:
            for window in self.windows:
                window.hide()

        for window in self.windows:
            if window.isVisible():
                self.hide()
                return

        self.window.destroy()

    def _notify(self, obj: GObject.Object, pspec: GObject.ParamSpec):
        print(pspec.name + " = " + str(obj.get_property(pspec.name)))
