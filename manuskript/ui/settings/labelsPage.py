#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Handy

Handy.init()

from manuskript.data import Settings, LabelHost, Label, Color
from manuskript.ui.util import rgbaFromColor, pixbufFromColor


class LabelsPage:

    def __init__(self, settings: Settings, labels: LabelHost):
        self.settings = settings
        self.labels = labels
        self.label = None

        builder = Gtk.Builder()
        builder.add_from_file("ui/settings/labels.glade")

        self.widget = builder.get_object("labels_page")

        self.labelStore = builder.get_object("label_store")
        self.refreshLabelStore()

        self.labelSelection = builder.get_object("label_selection")
        self.labelSelection.connect("changed", self._labelSelectionChanged)

        self.addButton = builder.get_object("add_label")
        self.removeButton = builder.get_object("remove_label")

        self.addButton.connect("clicked", self._addClicked)
        self.removeButton.connect("clicked", self._removeClicked)

        self.colorButton = builder.get_object("color")
        self.colorButton.connect("color-set", self._colorSet)

        self.labelNameRenderer = builder.get_object("label_name")
        self.labelNameRenderer.connect("edited", self._labelNameEdited)

        self.unloadLabelData()

    def refreshLabelStore(self):
        self.labelStore.clear()

        for label in self.labels:
            tree_iter = self.labelStore.append()

            if tree_iter is None:
                continue

            self.labelStore.set_value(tree_iter, 0, label.name)
            self.labelStore.set_value(tree_iter, 1, pixbufFromColor(label.color))

    def loadLabelData(self, label: Label):
        self.label = None

        self.colorButton.set_rgba(rgbaFromColor(label.color))

        self.label = label
        self.colorButton.set_sensitive(True)

    def unloadLabelData(self):
        self.label = None
        self.colorButton.set_sensitive(False)

        self.colorButton.set_rgba(rgbaFromColor(Color(0, 0, 0)))

    def _labelSelectionChanged(self, selection: Gtk.TreeSelection):
        model, tree_iter = selection.get_selected()

        if tree_iter is None:
            self.unloadLabelData()
            return

        label = self.labels.getLabel(model[tree_iter][0])

        if label is None:
            self.unloadLabelData()
        else:
            self.loadLabelData(label)

    def _addClicked(self, button: Gtk.Button):
        label = self.labels.addLabel()

        if label is None:
            return

        tree_iter = self.labelStore.append()

        if tree_iter is None:
            return

        self.labelStore.set_value(tree_iter, 0, label.name)
        self.labelStore.set_value(tree_iter, 1, pixbufFromColor(label.color))

    def _removeClicked(self, button: Gtk.Button):
        if self.label is None:
            return

        model, tree_iter = self.labelSelection.get_selected()

        if (model is None) or (tree_iter is None):
            return

        name = model.get_value(tree_iter, 0)
        model.remove(tree_iter)

        self.labels.removeLabel(name)

    def _colorSet(self, button: Gtk.ColorButton):
        if self.label is None:
            return

        color = button.get_rgba()

        red = int(color.red * 255)
        green = int(color.green * 255)
        blue = int(color.blue * 255)

        color = Color(red, green, blue)

        self.label.color = color

        character_name = self.label.name

        for row in self.labelStore:
            if row[0] == character_name:
                row[1] = pixbufFromColor(color)
                break

    def _labelNameEdited(self, renderer: Gtk.CellRendererText, path: str, text: str):
        if self.label is None:
            return

        model, tree_iter = self.labelSelection.get_selected()

        if (model is None) or (tree_iter is None):
            return

        name = model.get_value(tree_iter, 0)
        model.set_value(tree_iter, 0, text)

        self.labels.renameLabel(name, text)
