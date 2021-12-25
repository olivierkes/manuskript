#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from manuskript.data import Characters, Character, Importance, Color
from manuskript.ui.util import rgbaFromColor, pixbufFromColor
from manuskript.util import validString, invalidString, validInt, invalidInt


class CharactersView:

    def __init__(self, characters: Characters):
        self.characters = characters
        self.character = None

        builder = Gtk.Builder()
        builder.add_from_file("ui/characters.glade")

        self.widget = builder.get_object("characters_view")

        self.charactersStore = builder.get_object("characters_store")

        for character in self.characters:
            tree_iter = self.charactersStore.append()

            if tree_iter is None:
                continue

            self.charactersStore.set_value(tree_iter, 0, character.UID.value)
            self.charactersStore.set_value(tree_iter, 1, validString(character.name))
            self.charactersStore.set_value(tree_iter, 2, pixbufFromColor(character.color))
            self.charactersStore.set_value(tree_iter, 3, Importance.asValue(character.importance))

        self.mainCharactersStore = builder.get_object("main_characters_store")
        self.secondaryCharactersStore = builder.get_object("secondary_characters_store")
        self.minorCharactersStore = builder.get_object("minor_characters_store")

        self.mainCharactersStore.set_visible_func(lambda model, iter, userdata: model[iter][3] == Importance.MAIN.value)
        self.secondaryCharactersStore.set_visible_func(lambda model, iter, userdata: model[iter][3] == Importance.SECONDARY.value)
        self.minorCharactersStore.set_visible_func(lambda model, iter, userdata: model[iter][3] == Importance.MINOR.value)

        self.mainCharactersStore.refilter()
        self.secondaryCharactersStore.refilter()
        self.minorCharactersStore.refilter()

        self.characterSelections = [
            builder.get_object("minor_character_selection"),
            builder.get_object("secondary_character_selection"),
            builder.get_object("main_character_selection")
        ]

        for selection in self.characterSelections:
            selection.connect("changed", self.characterSelectionChanged)

        self.colorButton = builder.get_object("color")
        self.importanceCombo = builder.get_object("importance")
        self.allowPOVCheck = builder.get_object("allow_POV")

        self.colorSetSignal = self.colorButton.connect("color-set", self.colorSet)
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

        self.nameBuffer.connect("deleted-text", self.nameDeletedText)
        self.nameBuffer.connect("inserted-text", self.nameInsertedText)

        self.motivationBuffer.connect("changed", self.motivationChanged)
        self.goalBuffer.connect("changed", self.goalChanged)
        self.conflictBuffer.connect("changed", self.conflictChanged)
        self.epiphanyBuffer.connect("changed", self.epiphanyChanged)
        self.oneSentenceBuffer.connect("changed", self.oneSentenceChanged)
        self.oneParagraphBuffer.connect("changed", self.oneParagraphChanged)
        self.summaryBuffer.connect("changed", self.summaryChanged)
        self.notesBuffer.connect("changed", self.notesChanged)

        self.unloadCharacterData()

    def loadCharacterData(self, character: Character):
        self.character = None

        self.colorButton.set_rgba(rgbaFromColor(character.color))
        self.importanceCombo.set_active(Importance.asValue(character.importance))
        self.allowPOVCheck.set_active(character.allowPOV())

        self.nameBuffer.set_text(validString(character.name), -1)
        self.motivationBuffer.set_text(validString(character.motivation), -1)
        self.goalBuffer.set_text(validString(character.goal), -1)
        self.conflictBuffer.set_text(validString(character.conflict), -1)
        self.epiphanyBuffer.set_text(validString(character.epiphany), -1)
        self.oneSentenceBuffer.set_text(validString(character.summarySentence), -1)
        self.oneParagraphBuffer.set_text(validString(character.summaryParagraph), -1)
        self.summaryBuffer.set_text(validString(character.summaryFull), -1)
        self.notesBuffer.set_text(validString(character.notes), -1)

        self.detailsStore.clear()

        for (key, value) in character.details.items():
            tree_iter = self.detailsStore.append()

            if tree_iter is None:
                continue

            self.detailsStore.set_value(tree_iter, 0, str(key))
            self.detailsStore.set_value(tree_iter, 1, str(value))

        self.character = character

    def unloadCharacterData(self):
        self.character = None

        self.colorButton.set_rgba(rgbaFromColor(Color(0, 0, 0)))
        self.allowPOVCheck.set_active(False)

        self.nameBuffer.set_text("", -1)
        self.motivationBuffer.set_text("", -1)
        self.goalBuffer.set_text("", -1)
        self.conflictBuffer.set_text("", -1)
        self.epiphanyBuffer.set_text("", -1)
        self.oneSentenceBuffer.set_text("", -1)
        self.oneParagraphBuffer.set_text("", -1)
        self.summaryBuffer.set_text("", -1)
        self.notesBuffer.set_text("", -1)

        self.detailsStore.clear()

    def characterSelectionChanged(self, selection: Gtk.TreeSelection):
        model, tree_iter = selection.get_selected()

        if tree_iter is None:
            self.unloadCharacterData()
            return

        for other in self.characterSelections:
            if other != selection:
                other.unselect_all()

        character = self.characters.getByID(model[tree_iter][0])

        if character is None:
            self.unloadCharacterData()
        else:
            self.loadCharacterData(character)

    def colorSet(self, button: Gtk.ColorButton):
        if self.character is None:
            return

        color = button.get_rgba()

        red = int(color.red * 255)
        green = int(color.green * 255)
        blue = int(color.blue * 255)

        color = Color(red, green, blue)

        self.character.color = color

        character_id = self.character.UID.value

        for row in self.charactersStore:
            if row[0] == character_id:
                row[2] = pixbufFromColor(color)
                break

    def importanceChanged(self, combo: Gtk.ComboBox):
        if self.character is None:
            return

        tree_iter = combo.get_active_iter()

        if tree_iter is None:
            return

        model = combo.get_model()
        value = model[tree_iter][1]

        importance = Importance.fromValue(value)

        if (importance is None) or (self.character.importance == importance):
            return

        self.character.importance = importance

        character_id = self.character.UID.value

        for row in self.charactersStore:
            if row[0] == character_id:
                row[3] = Importance.asValue(importance)
                break

        self.mainCharactersStore.refilter()
        self.secondaryCharactersStore.refilter()
        self.minorCharactersStore.refilter()

        selection = self.characterSelections[importance.value]
        tree_view = selection.get_tree_view()
        model = tree_view.get_model()

        for row in model:
            if row[0] == character_id:
                selection.select_iter(row.iter)
                break

    def allowPOVToggled(self, button: Gtk.ToggleButton):
        if self.character is None:
            return

        self.character.POV = button.get_active()

    def addDetailsClicked(self, button: Gtk.Button):
        if self.character is None:
            return

        tree_iter = self.detailsStore.append()

        if tree_iter is None:
            return

        name = "Description"
        value = "Value"

        self.detailsStore.set_value(tree_iter, 0, name)
        self.detailsStore.set_value(tree_iter, 1, value)

        self.character.details[name] = value

    def removeDetailsClicked(self, button: Gtk.Button):
        if self.character is None:
            return

        model, tree_iter = self.detailsSelection.get_selected()

        if (model is None) or (tree_iter is None):
            return

        name = model.get_value(tree_iter, 0)
        model.remove(tree_iter)

        self.character.details.pop(name)

    def detailsNameEdited(self, renderer: Gtk.CellRendererText, path: str, text: str):
        if self.character is None:
            return

        model, tree_iter = self.detailsSelection.get_selected()

        if (model is None) or (tree_iter is None):
            return

        name = model.get_value(tree_iter, 0)
        model.set_value(tree_iter, 0, text)

        self.character.details[text] = self.character.details.pop(name)

    def detailsValueEdited(self, renderer: Gtk.CellRendererText, path: str, text: str):
        if self.character is None:
            return

        model, tree_iter = self.detailsSelection.get_selected()

        if (model is None) or (tree_iter is None):
            return

        name = model.get_value(tree_iter, 0)
        model.set_value(tree_iter, 1, text)

        self.character.details[name] = text

    def nameChanged(self, buffer: Gtk.EntryBuffer):
        if self.character is None:
            return

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

    def motivationChanged(self, buffer: Gtk.TextBuffer):
        if self.character is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.character.motivation = invalidString(text)

    def goalChanged(self, buffer: Gtk.TextBuffer):
        if self.character is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.character.goal = invalidString(text)

    def conflictChanged(self, buffer: Gtk.TextBuffer):
        if self.character is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.character.conflict = invalidString(text)

    def epiphanyChanged(self, buffer: Gtk.TextBuffer):
        if self.character is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.character.epiphany = invalidString(text)

    def oneSentenceChanged(self, buffer: Gtk.TextBuffer):
        if self.character is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.character.summarySentence = invalidString(text)

    def oneParagraphChanged(self, buffer: Gtk.TextBuffer):
        if self.character is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.character.summaryParagraph = invalidString(text)

    def summaryChanged(self, buffer: Gtk.TextBuffer):
        if self.character is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.character.summaryFull = invalidString(text)

    def notesChanged(self, buffer: Gtk.TextBuffer):
        if self.character is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.character.notes = invalidString(text)

    def show(self):
        self.widget.show_all()
