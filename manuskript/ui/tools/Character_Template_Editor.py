#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Imports
# Gi
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk, Handy

# Manuskript
from manuskript.ui.abstractDialog import AbstractDialog

# I lifted a lot of this code from frequencyWindow
# With a bit more stuff from charactersView

class CharacterTemplateEditorWindow(AbstractDialog):

    def __init__(self, mainWindow):
        AbstractDialog.__init__(self, mainWindow, "ui/character_details_template_editor.glade", "character_details_template_editor")

        self.headerBar = None
        self.back = None
        self.wordLeaflet = None
        self.analyzeWords = None
        self.analyzePhrases = None

    def initWindow(self, builder, window):
        self.headerBar = builder.get_object("header_bar")
        self.back = builder.get_object("back")
        
        self.character_leaflet = builder.get_object("character_details_leaflet")

        self.character_leaflet.bind_property("folded", self.back, "visible", GObject.BindingFlags.SYNC_CREATE)
        self.character_leaflet.bind_property("folded", self.headerBar, "show-close-button", GObject.BindingFlags.SYNC_CREATE |
                                       GObject.BindingFlags.INVERT_BOOLEAN)


        self.back.connect("clicked", self._backClicked)
        
        #Liking Stuff stole from charactersView
        self.detailsStore = builder.get_object("details_store")
        self.detailsSelection = builder.get_object("details_selection")
        self.addDetailsButton = builder.get_object("add_details")
        self.removeDetailsButton = builder.get_object("remove_details")
        self.append_details_template_button = builder.get_object("appened_details_template")
        self.detailsNameRenderer = builder.get_object("details_name")
        self.detailsValueRenderer = builder.get_object("details_value")
        
        self.addDetailsButton.connect("clicked", self.addDetailsClicked)
        self.removeDetailsButton.connect("clicked", self.removeDetailsClicked)

        self.detailsNameRenderer.connect("edited", self.detailsNameEdited)
        self.detailsValueRenderer.connect("edited", self.detailsValueEdited)
        
        self.populate_tree()
        


    def _backClicked(self, button: Gtk.Button):
        if self.wordLeaflet.get_visible_child_name() == "wordlist_view":
            self.wordLeaflet.set_visible_child_name("wordfilter_view")
        else:
            self.hide()
            
    # So this adds any previously added parts to the template
    def populate_tree(self):
        for name, value in self.mainWindow.project.character_template.details.items():
            tree_iter = self.detailsStore.append()
            
            if tree_iter is None:
                return


            self.detailsStore.set_value(tree_iter, 0, name)
            self.detailsStore.set_value(tree_iter, 1, value)            
    
# Functions stole From charactersView
    def addDetailsClicked(self, button: Gtk.Button):

        tree_iter = self.detailsStore.append()

        if tree_iter is None:
            return

        name = "Description"
        value = "Value"

        self.detailsStore.set_value(tree_iter, 0, name)
        self.detailsStore.set_value(tree_iter, 1, value)
        
        self.mainWindow.project.character_template.details[name] = value

    def removeDetailsClicked(self, button: Gtk.Button):

        model, tree_iter = self.detailsSelection.get_selected()

        if (model is None) or (tree_iter is None):
            return

        name = model.get_value(tree_iter, 0)
        model.remove(tree_iter)

        self.mainWindow.project.character_template.details.pop(name)

    def detailsNameEdited(self, renderer: Gtk.CellRendererText, path: str, text: str):

        model, tree_iter = self.detailsSelection.get_selected()

        if (model is None) or (tree_iter is None):
            return

        name = model.get_value(tree_iter, 0)
        model.set_value(tree_iter, 0, text)
        # There was an error with this line but it didn't seem to do anything bad.
        self.mainWindow.project.character_template.details[text] = self.mainWindow.project.character_template.details.pop(name)

    def detailsValueEdited(self, renderer: Gtk.CellRendererText, path: str, text: str):

        model, tree_iter = self.detailsSelection.get_selected()

        if (model is None) or (tree_iter is None):
            return

        name = model.get_value(tree_iter, 0)
        model.set_value(tree_iter, 1, text)

        self.mainWindow.project.character_template.details[name] = text

    def nameChanged(self, buffer: Gtk.EntryBuffer):

        text = buffer.get_text()
        name = invalidString(text)

        self.character.name = name

        character_id = self.character.UID.value

        for row in self.charactersStore:
            if row[0] == character_id:
                row[1] = validString(name)
                break

    def nameDeletedText(self, buffer: Gtk.EntryBuffer, position: int, n_chars: int):
        self.nameChanged(buffer)

    def nameInsertedText(self, buffer: Gtk.EntryBuffer, position: int, chars: str, n_chars: int):
        self.nameChanged(buffer)
