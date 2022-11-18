#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Handy

Handy.init()

from manuskript.data import Settings, StatusHost, Status


class StatusPage:

    def __init__(self, settings: Settings, statuses: StatusHost):
        self.settings = settings
        self.statuses = statuses
        self.status = None

        builder = Gtk.Builder()
        builder.add_from_file("ui/settings/status.glade")

        self.widget = builder.get_object("status_page")

        self.statusStore = builder.get_object("status_store")
        self.refreshStatusStore()

        self.statusSelection = builder.get_object("status_selection")
        self.statusSelection.connect("changed", self.statusSelectionChanged)

        self.addButton = builder.get_object("add_status")
        self.removeButton = builder.get_object("remove_status")

        self.addButton.connect("clicked", self.addClicked)
        self.removeButton.connect("clicked", self.removeClicked)

        self.unloadStatusData()

    def refreshStatusStore(self):
        self.statusStore.clear()

        for status in self.statuses:
            tree_iter = self.statusStore.append()

            if tree_iter is None:
                continue

            self.statusStore.set_value(tree_iter, 0, status.name)

    def loadStatusData(self, status: Status):
        self.status = status

    def unloadStatusData(self):
        self.status = None

    def statusSelectionChanged(self, selection: Gtk.TreeSelection):
        model, tree_iter = selection.get_selected()

        if tree_iter is None:
            self.unloadStatusData()
            return

        status = self.statuses.getStatus(model[tree_iter][0])

        if status is None:
            self.unloadStatusData()
        else:
            self.loadStatusData(status)

    def addClicked(self, button: Gtk.Button):
        status = self.statuses.addStatus()

        if status is None:
            return

        tree_iter = self.statusStore.append()

        if tree_iter is None:
            return

        self.statusStore.set_value(tree_iter, 0, status.name)

    def removeClicked(self, button: Gtk.Button):
        if self.status is None:
            return

        model, tree_iter = self.statusSelection.get_selected()

        if (model is None) or (tree_iter is None):
            return

        name = model.get_value(tree_iter, 0)
        model.remove(tree_iter)

        self.statuses.removeStatus(name)
