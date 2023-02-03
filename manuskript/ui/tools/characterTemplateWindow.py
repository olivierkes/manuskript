#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Imports
# Gi
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk, Handy

# Manuskript
from manuskript.ui.abstractDialog import AbstractDialog
from manuskript.util import unique_name_checker, invalidString, validString


# I lifted a lot of this code from frequencyWindow
# With a bit more stuff from charactersView

class CharacterTemplateWindow(AbstractDialog):

    def __init__(self, mainWindow):
        AbstractDialog.__init__(self, mainWindow, "ui/character_details_template_editor.glade",
                                "character_details_template_editor")

        self.headerBar = None
        self.back = None

        self.detailsStore = None
        self.detailsSelection = None
        self.addDetailsButton = None
        self.removeDetailsButton = None
        self.appendDetailsTemplateButton = None
        self.detailsNameRenderer = None
        self.detailsValueRenderer = None

    def initWindow(self, builder, window):
        self.headerBar = builder.get_object("header_bar")
        self.back = builder.get_object("back")

        self.back.connect("clicked", self._backClicked)
        
        # Liking Stuff stole from charactersView
        self.detailsStore = builder.get_object("details_store")
        self.detailsSelection = builder.get_object("details_selection")
        self.addDetailsButton = builder.get_object("add_details")
        self.removeDetailsButton = builder.get_object("remove_details")
        self.appendDetailsTemplateButton = builder.get_object("appened_details_template")
        self.detailsNameRenderer = builder.get_object("details_name")
        self.detailsValueRenderer = builder.get_object("details_value")
        
        self.addDetailsButton.connect("clicked", self._addDetailsClicked)
        self.removeDetailsButton.connect("clicked", self._removeDetailsClicked)

        self.detailsNameRenderer.connect("edited", self._detailsNameEdited)
        self.detailsValueRenderer.connect("edited", self._detailsValueEdited)
        
        self.loadCharacterTemplate()

    def _backClicked(self, button: Gtk.Button):
        self.hide()
            
    # So this adds any previously added parts to the template
    def loadCharacterTemplate(self):
        for name, value in self.mainWindow.project.character_template.details.items():
            tree_iter = self.detailsStore.append()
            
            if tree_iter is None:
                return

            self.detailsStore.set_value(tree_iter, 0, name)
            self.detailsStore.set_value(tree_iter, 1, value)            
    
# Functions stole From charactersView
    def _addDetailsClicked(self, button: Gtk.Button):
        tree_iter = self.detailsStore.append()

        if tree_iter is None:
            return

        name = unique_name_checker.get_unique_name_for_dictionary(self.mainWindow.project.character_template.details,
                                                                  "Description")
        value = "Value"

        self.detailsStore.set_value(tree_iter, 0, name)
        self.detailsStore.set_value(tree_iter, 1, value)
        
        self.mainWindow.project.character_template.details[name] = value

    def _removeDetailsClicked(self, button: Gtk.Button):
        model, tree_iter = self.detailsSelection.get_selected()

        if (model is None) or (tree_iter is None):
            return

        name = model.get_value(tree_iter, 0)
        model.remove(tree_iter)

        self.mainWindow.project.character_template.details.pop(name)

    def _detailsNameEdited(self, renderer: Gtk.CellRendererText, path: str, text: str):
        model, tree_iter = self.detailsSelection.get_selected()

        if (model is None) or (tree_iter is None):
            return
        text_to_set = unique_name_checker.get_unique_name_for_dictionary(
            self.mainWindow.project.character_template.details, text)
        name = model.get_value(tree_iter, 0)
        model.set_value(tree_iter, 0, text_to_set)
        # There was an error with this line but it didn't seem to do anything bad.
        self.mainWindow.project.character_template.details[text_to_set] = \
            self.mainWindow.project.character_template.details.pop(name)

    def _detailsValueEdited(self, renderer: Gtk.CellRendererText, path: str, text: str):
        model, tree_iter = self.detailsSelection.get_selected()

        if (model is None) or (tree_iter is None):
            return

        name = model.get_value(tree_iter, 0)
        model.set_value(tree_iter, 1, text)

        self.mainWindow.project.character_template.details[name] = text
