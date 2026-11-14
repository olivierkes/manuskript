#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import Any, Optional

from gi.repository import GLib, GObject, Gtk, Gdk

from manuskript.data import Project, Settings
from manuskript.editor import AbstractRegioner, AbstractSplitter, getRegioners, getSplitters
from manuskript.plugin import AbstractPlugin, findPlugins, loadPlugins
from manuskript.spellchecker import AbstractSpellchecker, getSpellcheckers
from manuskript.ui.dialog import RenameDialog
from manuskript.ui.views import *

from manuskript.ui.chooser import openFileDialog, saveFileDialog, FileFilter
from manuskript.ui.tools import *
from manuskript.ui.aboutDialog import AboutDialog
from manuskript.ui.compileWindow import CompileWindow
from manuskript.ui.importWindow import ImportWindow
from manuskript.ui.settingsWindow import SettingsWindow
from manuskript.ui.startupWindow import StartupWindow
from manuskript.ui.util import bindMenuItem, packViewIntoSlot, unpackFromSlot
from manuskript.util import parseFilenameFromURL, validString


class MainWindow:
    def __init__(self) -> None:
        self.initIconTheme()

        self.plugins: list[AbstractPlugin] = findPlugins()
        self.project: Optional[Project] = None
        self.regioner: Optional[AbstractRegioner] = None
        self.spellchecker: Optional[AbstractSpellchecker] = None

        builder = Gtk.Builder()
        builder.add_from_file("ui/main.glade")

        self.window = builder.get_object("main_window")
        self.window.connect("destroy", Gtk.main_quit)

        self.headerBar = builder.get_object("header_bar")
        self.leaflet = builder.get_object("leaflet")
        self.viewSwitcherBar = builder.get_object("view_switcher_bar")
        self.mainStack = builder.get_object("main_stack")

        self.leaflet.bind_property(
            "folded", self.viewSwitcherBar, "reveal", GObject.BindingFlags.SYNC_CREATE
        )
        self.leaflet.bind_property(
            "folded",
            self.headerBar,
            "show-close-button",
            GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.INVERT_BOOLEAN,
        )

        self.generalSlot = builder.get_object("general_slot")
        self.summarySlot = builder.get_object("summary_slot")
        self.charactersSlot = builder.get_object("characters_slot")
        self.plotSlot = builder.get_object("plot_slot")
        self.worldSlot = builder.get_object("world_slot")
        self.outlineSlot = builder.get_object("outline_slot")
        self.editorSlot = builder.get_object("editor_slot")

        self.metadataSlot = builder.get_object("metadata_slot")
        self.searchSlot = builder.get_object("search_slot")

        self.dictionaryMenuItem = builder.get_object("dictionary_menu_item")
        self.dictionaryMenu = builder.get_object("dictionary_menu")
        self.dictionaryMenuGroup = []

        self.generalView: Optional[GeneralView] = None
        self.summaryView: Optional[SummaryView] = None
        self.charactersView: Optional[CharactersView] = None
        self.plotView: Optional[PlotView] = None
        self.worldView: Optional[WorldView] = None
        self.outlineView: Optional[OutlineView] = None
        self.editorView: Optional[EditorView] = None

        self.metadataView: Optional[MetadataView] = None
        self.searchView: Optional[SearchView] = None

        self.viewDictionary: dict[Gtk.Widget, Optional[AbstractView]] = dict()

        self.idleStackSelection = 0

        self.startupWindow = StartupWindow(self)
        self.aboutDialog = AboutDialog(self)
        self.frequencyWindow = FrequencyWindow(self)
        self.settingsWindow = SettingsWindow(self)
        self.importWindow = ImportWindow(self)
        self.compileWindow = CompileWindow(self)

        self.windows = [
            self.startupWindow,
            self.aboutDialog,
            self.frequencyWindow,
            self.settingsWindow,
        ]

        self.recentChooserMenu = builder.get_object("recent_chooser_menu")
        self.recentChooserMenu.connect("item-activated", self._recentAction)

        bindMenuItem(builder, "open_menu_item", self._openAction)
        bindMenuItem(builder, "save_menu_item", self._saveAction)
        bindMenuItem(builder, "saveas_menu_item", self._saveAsAction)
        bindMenuItem(builder, "close_menu_item", self._closeAction)
        bindMenuItem(builder, "import_menu_item", self._importAction)
        bindMenuItem(builder, "compile_menu_item", self._compileAction)
        bindMenuItem(builder, "quit_menu_item", self._quitAction)

        bindMenuItem(builder, "cut_menu_item", self._cutAction)
        bindMenuItem(builder, "copy_menu_item", self._copyAction)
        bindMenuItem(builder, "paste_menu_item", self._pasteAction)
        bindMenuItem(builder, "delete_menu_item", self._deleteAction)
        bindMenuItem(builder, "rename_menu_item", self._renameAction)

        bindMenuItem(builder, "header1_atx_menu_item", self._h1EditorAction)
        bindMenuItem(builder, "header2_atx_menu_item", self._h2EditorAction)
        bindMenuItem(builder, "header3_atx_menu_item", self._h3EditorAction)
        bindMenuItem(builder, "header4_atx_menu_item", self._h4EditorAction)
        bindMenuItem(builder, "header5_atx_menu_item", self._h5EditorAction)
        bindMenuItem(builder, "header6_atx_menu_item", self._h6EditorAction)

        bindMenuItem(builder, "bold_menu_item", self._boldEditorAction)
        bindMenuItem(builder, "italic_menu_item", self._italicEditorAction)
        bindMenuItem(builder, "strike_menu_item", self._strikeEditorAction)

        bindMenuItem(builder, "settings_menu_item", self._settingsAction)
        bindMenuItem(builder, "frequency_menu_item", self._frequencyAction)
        bindMenuItem(builder, "about_menu_item", self._aboutAction)

        # Keyboard shortcuts
        self.accelGroup = Gtk.AccelGroup()
        self.window.add_accel_group(self.accelGroup)

        shortcuts = {
            "open_menu_item": "<Control>o",
            "save_menu_item": "<Control>s",
            "saveas_menu_item": "<Control><Shift>s",
            "close_menu_item": "<Control>w",
            "quit_menu_item": "<Control>q",
            "rename_menu_item": "F2",
        }

        for menu_id, shortcut in shortcuts.items():
            menu_item = builder.get_object(menu_id)

            if menu_item is None:
                continue

            key, modifiers = Gtk.accelerator_parse(shortcut)

            menu_item.add_accelerator(
                "activate",
                self.accelGroup,
                key,
                modifiers,
                Gtk.AccelFlags.VISIBLE,
            )

        loadPlugins(self.plugins)

        self.reloadDictionaries()
        self.hide()

    def initIconTheme(self) -> None:
        realpath = os.path.realpath(__file__)
        app_path = os.path.join(os.path.dirname(realpath), "../..")
        icons_dir = os.path.realpath(os.path.join(app_path, "icons"))

        theme: Gtk.IconTheme = Gtk.IconTheme.get_default()
        theme.append_search_path(icons_dir)

        settings: Gtk.Settings = Gtk.Settings.get_default()
        settings.set_property("gtk-icon-theme-name", "NumixMsk")

    def getProject(self) -> Project | None:
        return self.project

    def reloadDictionaries(self) -> None:
        def clearMenuItem(item: Gtk.RadioMenuItem) -> None:
            item.disconnect("toggled", self._toggledSpellcheckerItem)
            self.dictionaryMenu.remove(item)

        self.dictionaryMenu.foreach(lambda item: self.dictionaryMenu.remove(item))
        self.dictionaryMenuGroup = []

        selectedRadioMenuItem: Gtk.RadioMenuItem = None

        self.regioner = None

        for regioner in getRegioners():
            if not regioner.isValid():
                continue

            self.regioner = regioner

        for spellchecker in getSpellcheckers():
            menuItem = Gtk.RadioMenuItem.new_with_label(
                self.dictionaryMenuGroup, spellchecker.getTitle()
            )
            menuItem.connect("toggled", self._toggledSpellcheckerItem)
            menuItem.set_active(len(self.dictionaryMenuGroup) == 0)
            menuItem.spellchecker = spellchecker

            if menuItem.get_active():
                selectedRadioMenuItem = menuItem

            self.dictionaryMenuGroup = menuItem.get_group()
            self.dictionaryMenu.append(menuItem)

        self.dictionaryMenuItem.set_sensitive(len(self.dictionaryMenuGroup) > 0)

        if selectedRadioMenuItem:
            self._toggledSpellcheckerItem(selectedRadioMenuItem)

    def _toggledSpellcheckerItem(self, item: Gtk.CheckMenuItem) -> None:
        if not hasattr(item, "spellchecker"):
            return

        self.spellchecker = item.spellchecker

        if self.spellchecker is None:
            return

        splitter: Optional[AbstractSplitter] = None
        for s in getSplitters():
            splitter = s

        if (self.regioner is None) or (splitter is None):
            return

        if self.project is None:
            return
        if self.project.outline is None:
            return

        if not item.get_active():
            return

        mistakes = 0

        for outlineItem in self.project.outline.all():
            if not hasattr(outlineItem, "text"):
                continue

            text = outlineItem.text
            regions = self.regioner.splitText(text)

            for t in splitter.splitRegions(regions).tuples:
                if self.spellchecker.isMisspelled(text[t.begin : t.end]):
                    mistakes += 1

        print(mistakes)

    def __checkStackSelection(self, selected: Any = None) -> bool:
        slot: Gtk.Widget = self.mainStack.get_visible_child()

        self.idleStackSelection = GLib.timeout_add(
            100, self.__checkStackSelection, slot, priority=GLib.PRIORITY_HIGH_IDLE
        )

        if selected == slot:
            return False

        selected_view: Optional[AbstractView] = self.viewDictionary.get(selected)
        current_view: Optional[AbstractView] = self.viewDictionary.get(slot)

        if selected_view is not None:
            selected_view.deactivate()

        if current_view is not None:
            current_view.activate()

        return False

    def openProject(self, path: str | None = None) -> None:
        if self.project is not None:
            self.closeProject()

        if path is None:
            return

        self.project = Project(path)
        self.project.load()

        self.headerBar.set_subtitle(self.project.info.title)

        self.generalView = packViewIntoSlot(self.generalSlot, GeneralView, self.project.info)
        self.summaryView = packViewIntoSlot(self.summarySlot, SummaryView, self.project.summary)
        self.charactersView = packViewIntoSlot(
            self.charactersSlot, CharactersView, self.project.characters
        )
        self.plotView = packViewIntoSlot(
            self.plotSlot, PlotView, self.project.plots, self.project.characters
        )
        self.worldView = packViewIntoSlot(self.worldSlot, WorldView, self.project.world)
        self.outlineView = packViewIntoSlot(self.outlineSlot, OutlineView, self.project.outline)
        self.editorView = packViewIntoSlot(self.editorSlot, EditorView, self.project)

        self.metadataView = packViewIntoSlot(self.metadataSlot, MetadataView, self.project, self.editorView)
        self.searchView = packViewIntoSlot(self.searchSlot, SearchView)

        self.viewDictionary = {
          self.generalSlot: self.generalView,
          self.summarySlot: self.summaryView,
          self.charactersSlot: self.charactersView,
          self.plotSlot: self.plotView,
          self.worldSlot: self.worldView,
          self.outlineSlot: self.outlineView,
          self.editorSlot: self.editorView
        }

        if 0 != self.idleStackSelection:
            GLib.source_remove(self.idleStackSelection)

        self.idleStackSelection = GLib.idle_add(
            self.__checkStackSelection, priority=GLib.PRIORITY_HIGH_IDLE
        )

        self.startupWindow.hide()
        self.show()

    def closeProject(self) -> None:
        if 0 != self.idleStackSelection:
            GLib.source_remove(self.idleStackSelection)
            self.idleStackSelection = 0

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

    def _openAction(self, menuItem: Gtk.MenuItem) -> None:
        path = openFileDialog(self.window, FileFilter("Manuskript project", "msk"))
        if path is None:
            return

        self.openProject(path)

    def _recentAction(self, recentChooser: Gtk.RecentChooser) -> None:
        uri = recentChooser.get_current_uri()
        if uri is None:
            return

        path = parseFilenameFromURL(uri)
        if path is None:
            return

        self.openProject(path)

    def _saveAction(self, menuItem: Gtk.MenuItem) -> None:
        if self.project is None:
            return

        self.project.save()

    def _saveAsAction(self, menuItem: Gtk.MenuItem) -> None:
        if self.project is None:
            return

        path = saveFileDialog(self.window, FileFilter("Manuskript project", "msk"))
        if path is None:
            return

        self.project.changePath(path)
        self.project.save()

    def _closeAction(self, menuItem: Gtk.MenuItem) -> None:
        self.closeProject()

    def _importAction(self, menuItem: Gtk.MenuItem) -> None:
        self.importWindow.show()

    def _compileAction(self, menuItem: Gtk.MenuItem) -> None:
        self.compileWindow.show()

    def _quitAction(self, menuItem: Gtk.MenuItem) -> None:
        self.exit(True)

    def _cutAction(self, menuItem: Gtk.MenuItem) -> None:
        if self.editorView is None:
            return

        self.editorView.cutSelection()

    def _copyAction(self, menuItem: Gtk.MenuItem) -> None:
        if self.editorView is None:
            return

        self.editorView.copySelection()

    def _pasteAction(self, menuItem: Gtk.MenuItem) -> None:
        if self.editorView is None:
            return

        self.editorView.pasteClipboard()

    def _deleteAction(self, menuItem: Gtk.MenuItem) -> None:
        if self.editorView is None:
            return

        self.editorView.deleteSelection()

    def _renameAction(self, menuItem: Gtk.MenuItem) -> None:
        currentSlot = self.mainStack.get_visible_child()

        if currentSlot == self.outlineSlot:
            currentView = self.outlineView
        elif currentSlot == self.editorSlot:
            currentView = self.editorView
        else:
            currentView = None

        if (currentView is None) or (currentView.outlineItem is None):
            return

        def __renameEditorItem(name: str, mainWindow: MainWindow) -> None:
            currentSlot = mainWindow.mainStack.get_visible_child()

            if currentSlot == mainWindow.editorSlot:
                if mainWindow.editorView is not None:
                    mainWindow.editorView.renameItem(name)
                if mainWindow.outlineView is not None:
                    mainWindow.outlineView.refreshOutlineStore()
            elif currentSlot == mainWindow.outlineSlot:
                if mainWindow.outlineView is not None:
                    mainWindow.outlineView.renameItem(name)
                if mainWindow.editorView is not None:
                    mainWindow.editorView.refreshOutlineStore()

        dialog = RenameDialog(self, callback=__renameEditorItem, closure=self)
        dialog.show(text=currentView.outlineItem.title)

    def _h1EditorAction(self, menuItem: Gtk.MenuItem) -> None:
        if self.editorView is None:
            return

        self.editorView.toggleTagFromSelection("h1")

    def _h2EditorAction(self, menuItem: Gtk.MenuItem) -> None:
        if self.editorView is None:
            return

        self.editorView.toggleTagFromSelection("h2")

    def _h3EditorAction(self, menuItem: Gtk.MenuItem) -> None:
        if self.editorView is None:
            return

        self.editorView.toggleTagFromSelection("h3")

    def _h4EditorAction(self, menuItem: Gtk.MenuItem) -> None:
        if self.editorView is None:
            return

        self.editorView.toggleTagFromSelection("h4")

    def _h5EditorAction(self, menuItem: Gtk.MenuItem) -> None:
        if self.editorView is None:
            return

        self.editorView.toggleTagFromSelection("h5")

    def _h6EditorAction(self, menuItem: Gtk.MenuItem) -> None:
        if self.editorView is None:
            return

        self.editorView.toggleTagFromSelection("h6")

    def _boldEditorAction(self, menuItem: Gtk.MenuItem) -> None:
        if self.editorView is None:
            return

        self.editorView.toggleTagFromSelection("b")

    def _italicEditorAction(self, menuItem: Gtk.MenuItem) -> None:
        if self.editorView is None:
            return

        self.editorView.toggleTagFromSelection("i")

    def _strikeEditorAction(self, menuItem: Gtk.MenuItem) -> None:
        if self.editorView is None:
            return

        self.editorView.toggleTagFromSelection("s")

    def getSettings(self) -> Settings | None:
        if self.project is not None:
            return self.project.settings
        else:
            return None

    def _settingsAction(self, menuItem: Gtk.MenuItem) -> None:
        self.settingsWindow.show()

    def _frequencyAction(self, menuItem: Gtk.MenuItem) -> None:
        self.frequencyWindow.show()

    def _aboutAction(self, menuItem: Gtk.MenuItem) -> None:
        self.aboutDialog.show()

    def show(self) -> None:
        self.window.show_all()

    def hide(self) -> None:
        self.window.hide()

    def isVisible(self) -> bool:
        return self.window.get_property("visible")

    def run(self) -> None:
        self.show()
        Gtk.main()

    def exit(self, force: bool = False) -> None:
        if force:
            for window in self.windows:
                window.hide()

        for window in self.windows:
            if window.isVisible():
                self.hide()
                return

        self.window.destroy()

    def _notify(self, obj: GObject.Object, pspec: GObject.ParamSpec) -> None:
        print(pspec.name + " = " + str(obj.get_property(pspec.name)))
