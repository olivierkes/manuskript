#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from manuskript.data import World, WorldItem
from manuskript.util import validString, invalidString, validInt, invalidInt


class WorldView:

    def __init__(self, world: World):
        self.world = world
        self.worldItem = None

        builder = Gtk.Builder()
        builder.add_from_file("ui/world.glade")

        self.widget = builder.get_object("world_view")
        self.notebook = builder.get_object("world_notebook")

        self.worldTreeView = builder.get_object("world_tree_view")

        self.worldStore = builder.get_object("world_store")
        self.refreshWorldStore()

        self.filteredWorldStore = builder.get_object("filtered_world_store")
        self.filterWorldBuffer = builder.get_object("filter_world")

        self.filterWorldBuffer.connect("deleted-text", self.filterWorldDeletedText)
        self.filterWorldBuffer.connect("inserted-text", self.filterWorldInsertedText)

        self.filteredWorldStore.set_visible_func(self.filterWorld)
        self.filteredWorldStore.refilter()

        self.worldSelection = builder.get_object("world_selection")

        self.worldSelection.connect("changed", self.worldSelectionChanged)

        self.addToWorldButton = builder.get_object("add_to_world")
        self.removeFromWorldButton = builder.get_object("remove_from_world")

        self.addToWorldButton.connect("clicked", self.addToWorldClicked)
        self.removeFromWorldButton.connect("clicked", self.removeFromWorldClicked)

        self.nameBuffer = builder.get_object("name")
        self.descriptionBuffer = builder.get_object("description")
        self.sourceOfPassionBuffer = builder.get_object("source_of_passion")
        self.sourceOfConflictBuffer = builder.get_object("source_of_conflict")

        self.nameBuffer.connect("deleted-text", self.nameDeletedText)
        self.nameBuffer.connect("inserted-text", self.nameInsertedText)

        self.descriptionBuffer.connect("changed", self.descriptionChanged)
        self.sourceOfPassionBuffer.connect("changed", self.sourceOfPassionChanged)
        self.sourceOfConflictBuffer.connect("changed", self.sourceOfConflictChanged)

        self.unloadWorldData()

    def __appendWorldItem(self, worldItem: WorldItem, parent_iter=None):
        tree_iter = self.worldStore.append(parent_iter)

        if tree_iter is None:
            return

        self.worldStore.set_value(tree_iter, 0, worldItem.UID.value)
        self.worldStore.set_value(tree_iter, 1, validString(worldItem.name))

        for item in worldItem:
            self.__appendWorldItem(item, tree_iter)

    def refreshWorldStore(self):
        self.worldStore.clear()

        for item in self.world.top:
            self.__appendWorldItem(item)

        self.worldTreeView.expand_all()

    def loadWorldData(self, worldItem: WorldItem):
        self.worldItem = None

        self.nameBuffer.set_text(validString(worldItem.name), -1)
        self.descriptionBuffer.set_text(validString(worldItem.description), -1)
        self.sourceOfPassionBuffer.set_text(validString(worldItem.passion), -1)
        self.sourceOfConflictBuffer.set_text(validString(worldItem.conflict), -1)

        self.worldItem = worldItem
        self.notebook.set_sensitive(True)

    def unloadWorldData(self):
        self.worldItem = None
        self.notebook.set_sensitive(False)

        self.nameBuffer.set_text("", -1)
        self.descriptionBuffer.set_text("", -1)
        self.sourceOfPassionBuffer.set_text("", -1)
        self.sourceOfConflictBuffer.set_text("", -1)

    def worldSelectionChanged(self, selection: Gtk.TreeSelection):
        model, tree_iter = selection.get_selected()

        if tree_iter is None:
            self.unloadWorldData()
            return

        worldItem = self.world.getItemByID(model[tree_iter][0])

        if worldItem is None:
            self.unloadWorldData()
        else:
            self.loadWorldData(worldItem)

    def addToWorldClicked(self, button: Gtk.Button):
        name = invalidString(self.filterWorldBuffer.get_text())
        worldItem = self.world.addItem(name, self.worldItem)

        if worldItem is None:
            return

        self.refreshWorldStore()

    def removeFromWorldClicked(self, button: Gtk.Button):
        if self.worldItem is None:
            return

        self.worldItem.remove()
        self.refreshWorldStore()

    def __matchWorldItemByText(self, worldItem: WorldItem, text: str):
        for item in worldItem:
            if self.__matchWorldItemByText(item, text):
                return True

        name = validString(worldItem.name)
        return text in name.lower()

    def filterWorld(self, model, iter, userdata):
        worldItem = self.world.getItemByID(model[iter][0])

        if worldItem is None:
            return False

        text = validString(self.filterWorldBuffer.get_text())
        return self.__matchWorldItemByText(worldItem, text.lower())

    def filterWorldChanged(self, buffer: Gtk.EntryBuffer):
        self.filteredWorldStore.refilter()

    def filterWorldDeletedText(self, buffer: Gtk.EntryBuffer, position: int, n_chars: int):
        self.filterWorldChanged(buffer)

    def filterWorldInsertedText(self, buffer: Gtk.EntryBuffer, position: int, chars: str, n_chars: int):
        self.filterWorldChanged(buffer)

    def nameChanged(self, buffer: Gtk.EntryBuffer):
        if self.worldItem is None:
            return

        text = buffer.get_text()
        name = invalidString(text)

        self.worldItem.name = name

        world_id = self.worldItem.UID.value

        for row in self.worldStore:
            if row[0] == world_id:
                row[1] = validString(name)
                break

    def nameDeletedText(self, buffer: Gtk.EntryBuffer, position: int, n_chars: int):
        self.nameChanged(buffer)

    def nameInsertedText(self, buffer: Gtk.EntryBuffer, position: int, chars: str, n_chars: int):
        self.nameChanged(buffer)

    def descriptionChanged(self, buffer: Gtk.TextBuffer):
        if self.worldItem is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.worldItem.description = invalidString(text)

    def sourceOfPassionChanged(self, buffer: Gtk.TextBuffer):
        if self.worldItem is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.worldItem.passion = invalidString(text)

    def sourceOfConflictChanged(self, buffer: Gtk.TextBuffer):
        if self.worldItem is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.worldItem.conflict = invalidString(text)

    def show(self):
        self.widget.show_all()
