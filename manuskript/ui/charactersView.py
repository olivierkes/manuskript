#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class CharactersView:

    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file("ui/characters.glade")

        self.widget = builder.get_object("characters_view")

        self.colorButton = builder.get_object("color")
        self.importanceCombo = builder.get_object("importance")
        self.allowPOVCheck = builder.get_object("allow_POV")

        self.colorButton.connect("color-set", self.colorSet)
        self.importanceCombo.connect("changed", self.importanceChanged)
        self.allowPOVCheck.connect("toggled", self.allowPOVToggled)

        self.detailsStore = builder.get_object("details_store")
        self.detailsSelection = builder.get_object("details_selection")
        self.addDetailsButton = builder.get_object("add_details")
        self.removeDetailsButton = builder.get_object("remove_details")
        self.detailsNameRenderer = builder.get_object("details_name")
        self.detailsValueRenderer = builder.get_object("details_value")

        self.addDetailsButton.connect("clicked", self.addDetailsClicked)
        self.removeDetailsButton.connect("clicked", self.removeDetailsClicked)
        self.detailsNameRenderer.connect("edited", self.detailsNameEdited)
        self.detailsValueRenderer.connect("edited", self.detailsValueEdited)

        self.nameBuffer = builder.get_object("name")
        self.motivationBuffer = builder.get_object("motivation")
        self.goalBuffer = builder.get_object("goal")
        self.conflictBuffer = builder.get_object("conflict")
        self.epiphanyBuffer = builder.get_object("epiphany")
        self.oneSentenceBuffer = builder.get_object("one_sentence_summary")
        self.oneParagraphBuffer = builder.get_object("one_paragraph_summary")
        self.summaryBuffer = builder.get_object("summary")
        self.notesBuffer = builder.get_object("notes")

    def colorSet(self, button: Gtk.ColorButton):
        color = button.get_rgba()

        print("{} {} {} {}".format(color.red, color.green, color.blue, color.alpha))

    def importanceChanged(self, combo: Gtk.ComboBox):
        tree_iter = combo.get_active_iter()

        if tree_iter is None:
            return

        model = combo.get_model()
        name = model[tree_iter][0]

        print("blub " + name)

    def allowPOVToggled(self, button: Gtk.ToggleButton):
        state = button.get_active()

        print("OK: {}".format(state))

    def addDetailsClicked(self, button: Gtk.Button):
        tree_iter = self.detailsStore.append()

        if tree_iter is None:
            return

        self.detailsStore.set_value(tree_iter, 0, "Description")
        self.detailsStore.set_value(tree_iter, 1, "Value")

    def removeDetailsClicked(self, button: Gtk.Button):
        model, tree_iter = self.detailsSelection.get_selected()

        if (model is None) or (tree_iter is None):
            return

        model.remove(tree_iter)

    def detailsNameEdited(self, renderer: Gtk.CellRendererText, path: str, text: str):
        model, tree_iter = self.detailsSelection.get_selected()

        if (model is None) or (tree_iter is None):
            return

        model.set_value(tree_iter, 0, text)

    def detailsValueEdited(self, renderer: Gtk.CellRendererText, path: str, text: str):
        model, tree_iter = self.detailsSelection.get_selected()

        if (model is None) or (tree_iter is None):
            return

        model.set_value(tree_iter, 1, text)

    def show(self):
        self.widget.show_all()
