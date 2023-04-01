#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from manuskript.data import Characters, Character, Importance, Color
from manuskript.ui.util import rgbaFromColor, pixbufFromColor
from manuskript.util import validString, invalidString, validInt, invalidInt, unique_name_checker


class CharactersView:

    def __init__(self, project):
        self.characterTemplates = project.character_templates # The template for detailed info
        self.characters = project.characters
        self.character = None

        builder = Gtk.Builder()
        builder.add_from_file("ui/characters.glade")

        self.widget = builder.get_object("characters_view")
        self.notebook = builder.get_object("character_notebook")

        self.charactersStore = builder.get_object("characters_store")
        self.refreshCharacterStore()

        self.filteredCharactersStore = builder.get_object("filtered_characters_store")
        self.mainCharactersStore = builder.get_object("main_characters_store")
        self.secondaryCharactersStore = builder.get_object("secondary_characters_store")
        self.minorCharactersStore = builder.get_object("minor_characters_store")

        self.filterCharactersBuffer = builder.get_object("filter_characters")

        self.filterCharactersBuffer.connect("deleted-text", self._filterCharactersDeletedText)
        self.filterCharactersBuffer.connect("inserted-text", self._filterCharactersInsertedText)

        self.filteredCharactersStore.set_visible_func(self._filterCharacters)
        self.filteredCharactersStore.refilter()

        self.mainCharactersStore.set_visible_func(lambda model, iterator, userdata:
                                                  model[iterator][3] == Importance.MAIN.value)
        self.secondaryCharactersStore.set_visible_func(lambda model, iterator, userdata:
                                                       model[iterator][3] == Importance.SECONDARY.value)
        self.minorCharactersStore.set_visible_func(lambda model, iterator, userdata:
                                                   model[iterator][3] == Importance.MINOR.value)

        self.mainCharactersStore.refilter()
        self.secondaryCharactersStore.refilter()
        self.minorCharactersStore.refilter()

        self.characterSelections = [
            builder.get_object("minor_character_selection"),
            builder.get_object("secondary_character_selection"),
            builder.get_object("main_character_selection")
        ]

        for selection in self.characterSelections:
            selection.connect("changed", self._characterSelectionChanged)

        self.addCharacterButton = builder.get_object("add_character")
        self.removeCharacterButton = builder.get_object("remove_character")

        self.addCharacterButton.connect("clicked", self._addCharacterClicked)
        self.removeCharacterButton.connect("clicked", self._removeCharacterClicked)

        self.colorButton = builder.get_object("color")
        self.importanceCombo = builder.get_object("importance")
        self.allowPOVCheck = builder.get_object("allow_POV")

        self.colorButton.connect("color-set", self._colorSet)
        self.importanceCombo.connect("changed", self._importanceChanged)
        self.allowPOVCheck.connect("toggled", self._allowPOVToggled)

        self.detailsStore = builder.get_object("details_store")
        self.detailsSelection = builder.get_object("details_selection")
        self.addDetailsButton = builder.get_object("add_details")
        self.removeDetailsButton = builder.get_object("remove_details")
        self.charecterDetailsMenuButton = builder.get_object("characters_details_menu_button")
        self.newTemplateButton = builder.get_object("new_template_button")
        self.newTemplateEntry = builder.get_object("new_template_entry")
        self.newTemplateEntryBuffer = builder.get_object("new_template_entry_buffer")
        self.charecterDetailsMenuAppendBox = builder.get_object("template_select_box")
        self.charecterDetailsMenuTemplateBox = builder.get_object("template_select_box2")
        self.detailsNameRenderer = builder.get_object("details_name")
        self.detailsValueRenderer = builder.get_object("details_value")

        self.addDetailsButton.connect("clicked", self._addDetailsClicked)
        self.removeDetailsButton.connect("clicked", self._removeDetailsClicked)
        self.charecterDetailsMenuButton.connect("clicked", self._onCharecterDetailsMenuClicked)
        self.newTemplateButton.connect("clicked", self._onNewTemplateButtonClicked)
        self.detailsNameRenderer.connect("edited", self._detailsNameEdited)
        self.detailsValueRenderer.connect("edited", self._detailsValueEdited)

        self.nameBuffer = builder.get_object("name")
        self.motivationBuffer = builder.get_object("motivation")
        self.goalBuffer = builder.get_object("goal")
        self.conflictBuffer = builder.get_object("conflict")
        self.epiphanyBuffer = builder.get_object("epiphany")
        self.oneSentenceBuffer = builder.get_object("one_sentence_summary")
        self.oneParagraphBuffer = builder.get_object("one_paragraph_summary")
        self.summaryBuffer = builder.get_object("summary")
        self.notesBuffer = builder.get_object("notes")

        self.nameBuffer.connect("deleted-text", self._nameDeletedText)
        self.nameBuffer.connect("inserted-text", self._nameInsertedText)

        self.motivationBuffer.connect("changed", self._motivationChanged)
        self.goalBuffer.connect("changed", self._goalChanged)
        self.conflictBuffer.connect("changed", self._conflictChanged)
        self.epiphanyBuffer.connect("changed", self._epiphanyChanged)
        self.oneSentenceBuffer.connect("changed", self._oneSentenceChanged)
        self.oneParagraphBuffer.connect("changed", self._oneParagraphChanged)
        self.summaryBuffer.connect("changed", self._summaryChanged)
        self.notesBuffer.connect("changed", self._notesChanged)

        self.unloadCharacterData()
        

    def refreshCharacterStore(self):
        self.charactersStore.clear()

        for character in self.characters:
            tree_iter = self.charactersStore.append()

            if tree_iter is None:
                continue

            self.charactersStore.set_value(tree_iter, 0, character.UID.value)
            self.charactersStore.set_value(tree_iter, 1, validString(character.name))
            self.charactersStore.set_value(tree_iter, 2, pixbufFromColor(character.color))
            self.charactersStore.set_value(tree_iter, 3, Importance.asValue(character.importance))

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

            self.detailsStore.set_value(tree_iter, 0, validString(key))
            self.detailsStore.set_value(tree_iter, 1, validString(value))

        self.character = character
        self.notebook.set_sensitive(True)

    def unloadCharacterData(self):
        self.character = None
        self.notebook.set_sensitive(False)

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

    def _characterSelectionChanged(self, selection: Gtk.TreeSelection):
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

    def _addCharacterClicked(self, button: Gtk.Button):
        name = invalidString(self.filterCharactersBuffer.get_text())
        character = self.characters.add(name)

        if character is None:
            return

        if self.character is not None:
            character.importance = self.character.importance

        self.refreshCharacterStore()

    def _removeCharacterClicked(self, button: Gtk.Button):
        if self.character is None:
            return

        self.character.remove()
        self.refreshCharacterStore()

    def _filterCharacters(self, model, iterator, userdata):
        name = validString(model[iterator][1])
        text = validString(self.filterCharactersBuffer.get_text())

        return text.lower() in name.lower()

    def __filterCharactersChanged(self, buffer: Gtk.EntryBuffer):
        self.filteredCharactersStore.refilter()

    def _filterCharactersDeletedText(self, buffer: Gtk.EntryBuffer, position: int, n_chars: int):
        self.__filterCharactersChanged(buffer)

    def _filterCharactersInsertedText(self, buffer: Gtk.EntryBuffer, position: int, chars: str, n_chars: int):
        self.__filterCharactersChanged(buffer)

    def _colorSet(self, button: Gtk.ColorButton):
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

    def _importanceChanged(self, combo: Gtk.ComboBox):
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

    def _allowPOVToggled(self, button: Gtk.ToggleButton):
        if self.character is None:
            return

        self.character.POV = button.get_active()

    def _addDetailsClicked(self, button: Gtk.Button):
        if self.character is None:
            return

        tree_iter = self.detailsStore.append()

        if tree_iter is None:
            return

        name = unique_name_checker.get_unique_name_for_dictionary(self.character.details, "Description")
        value = "Value"

        self.detailsStore.set_value(tree_iter, 0, name)
        self.detailsStore.set_value(tree_iter, 1, value)

        self.character.details[name] = value

    def _removeDetailsClicked(self, button: Gtk.Button):
        if self.character is None:
            return

        model, tree_iter = self.detailsSelection.get_selected()

        if (model is None) or (tree_iter is None):
            return

        name = model.get_value(tree_iter, 0)
        model.remove(tree_iter)

        self.character.details.pop(name)
        
    def _updateCharecterDetailsMenu(self):
        def clear_container(container):
            data = container.get_children()
            for d in data:
                container.remove(d)
        clear_container( self.charecterDetailsMenuAppendBox)
        clear_container(self.charecterDetailsMenuTemplateBox)
        for x in self.characterTemplates.templates:
            button = Gtk.Button(label=x,) # TODO: turn into ModelButton
            button.connect("clicked", self._appendTemplateClicked, x)
            self.charecterDetailsMenuAppendBox.add(button)
            # Now we do the buttons for charecterDetailsMenuTemplateBox
            box = Gtk.Box()
            label = Gtk.Label(label=x)
            box.pack_start(label, False, False, 0)
            overwrite_button = Gtk.Button()
            overwrite_button.add(Gtk.Image(icon_name='emblem-insync-syncing'))
            overwrite_button.connect("clicked", self._updateTemplateClicked, x)
            overwrite_button.set_tooltip_markup ('Overwrite template with text of current file') # TODO: This might be an issue when it comes to translating
            delete_button = Gtk.Button() 
            delete_button.add(Gtk.Image(icon_name='app-remove-symbolic'))
            delete_button.set_tooltip_markup ('Delete') # TODO: This might be an issue when it comes to translating
            delete_button.connect("clicked", self._deleteTemplateClicked, x)
            box.pack_start(overwrite_button, False, False, 0)            
            box.pack_start(delete_button, False, False, 0)
            self.charecterDetailsMenuTemplateBox.add(box)

        self.charecterDetailsMenuAppendBox.show_all()
        self.charecterDetailsMenuTemplateBox.show_all()
        
    def _onCharecterDetailsMenuClicked(self, button: Gtk.MenuButton):
        self._updateCharecterDetailsMenu()
        
    def _updateTemplateClicked(self, button: Gtk.ModelButton, template):
        if self.character is None:
            return
        self.characterTemplates.templates[template] = self.character.details  # TODO: Add A warning? Or should there be undo/ redo when revisions are written.

    def _deleteTemplateClicked(self, button: Gtk.ModelButton, template):
        del self.characterTemplates.templates[template]
        self._updateCharecterDetailsMenu()

    def _appendTemplateClicked(self, button: Gtk.ModelButton, template):
        if self.character is None:
            return
        self.character.details.update(self.characterTemplates.templates[template])

       # We have to reload the character
        self.loadCharacterData(self.character)

    def _onNewTemplateButtonClicked(self, button: Gtk.Button):
        text = self.newTemplateEntryBuffer.get_text()
        if text == "":
            return
        if text in self.characterTemplates.templates:
            new_text = unique_name_checker.get_unique_name_for_dictionary(self.characterTemplates.templates, text)
            self.newTemplateEntryBuffer.set_text(new_text, -1)  # TODO: Add a warning
            return
        else:
            self.characterTemplates.templates[text] = self.character.details
            self._updateCharecterDetailsMenu()

    def _detailsNameEdited(self, renderer: Gtk.CellRendererText, path: str, text: str):
        if self.character is None:
            return

        model, tree_iter = self.detailsSelection.get_selected()

        if (model is None) or (tree_iter is None):
            return
        
        text_to_set = unique_name_checker.get_unique_name_for_dictionary(self.character.details, text)
        name = model.get_value(tree_iter, 0)
        model.set_value(tree_iter, 0, text_to_set)

        self.character.details[text_to_set] = self.character.details.pop(name)

    def _detailsValueEdited(self, renderer: Gtk.CellRendererText, path: str, text: str):
        if self.character is None:
            return

        model, tree_iter = self.detailsSelection.get_selected()

        if (model is None) or (tree_iter is None):
            return

        name = model.get_value(tree_iter, 0)
        model.set_value(tree_iter, 1, text)

        self.character.details[name] = text

    def __nameChanged(self, buffer: Gtk.EntryBuffer):
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

    def _nameDeletedText(self, buffer: Gtk.EntryBuffer, position: int, n_chars: int):
        self.__nameChanged(buffer)

    def _nameInsertedText(self, buffer: Gtk.EntryBuffer, position: int, chars: str, n_chars: int):
        self.__nameChanged(buffer)

    def _motivationChanged(self, buffer: Gtk.TextBuffer):
        if self.character is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.character.motivation = invalidString(text)

    def _goalChanged(self, buffer: Gtk.TextBuffer):
        if self.character is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.character.goal = invalidString(text)

    def _conflictChanged(self, buffer: Gtk.TextBuffer):
        if self.character is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.character.conflict = invalidString(text)

    def _epiphanyChanged(self, buffer: Gtk.TextBuffer):
        if self.character is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.character.epiphany = invalidString(text)

    def _oneSentenceChanged(self, buffer: Gtk.TextBuffer):
        if self.character is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.character.summarySentence = invalidString(text)

    def _oneParagraphChanged(self, buffer: Gtk.TextBuffer):
        if self.character is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.character.summaryParagraph = invalidString(text)

    def _summaryChanged(self, buffer: Gtk.TextBuffer):
        if self.character is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.character.summaryFull = invalidString(text)

    def _notesChanged(self, buffer: Gtk.TextBuffer):
        if self.character is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.character.notes = invalidString(text)

    def show(self):
        self.widget.show_all()

