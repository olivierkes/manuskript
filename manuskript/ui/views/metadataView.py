#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional

from gi.repository import Gtk

from manuskript.data import OutlineItem, Project
from manuskript.ui.util import pixbufFromColor
from manuskript.ui.views.editorView import EditorView
from manuskript.ui.views.reloadOutlineView import ReloadOutlineView
from manuskript.util import validString, validVariantValue


class MetadataView(ReloadOutlineView):
    def __init__(self, project: Project, editorView: EditorView) -> None:
        ReloadOutlineView.__init__(self, editorView.reloadOulineViews)

        self.project: Project = project

        builder = Gtk.Builder()
        builder.add_from_file("ui/metadata.glade")

        self.widget = builder.get_object("metadata_view")

        self.labelStore = builder.get_object("label_store")
        self.refreshLabelStore()

        self.statusStore = builder.get_object("status_store")
        self.refreshStatusStore()

        self.charactersStore = builder.get_object("characters_store")
        self.refreshCharactersStore()

        self.titleLabel: Gtk.Label = builder.get_object("title_label")
        self.povCombo: Gtk.ComboBox = builder.get_object("pov_combo")
        self.statusCombo: Gtk.ComboBox = builder.get_object("status_combo")
        self.labelCombo: Gtk.ComboBox = builder.get_object("label_combo")
        self.compileCheck: Gtk.CheckButton = builder.get_object("compile_check")
        self.goalBuffer: Gtk.EntryBuffer = builder.get_object("goal")

        self.oneLineEntry: Gtk.Entry = builder.get_object("one_line_entry")
        self.summaryBuffer: Gtk.TextBuffer = builder.get_object("summary")
        self.notesBuffer: Gtk.TextBuffer = builder.get_object("notes")

        self.reloadOutlineData(None)

    def refreshLabelStore(self) -> None:
        self.labelStore.clear()

        for label in self.project.outline.labels:
            tree_iter = self.labelStore.append()

            if tree_iter is None:
                continue

            self.labelStore.set_value(tree_iter, 0, validString(label.name))
            self.labelStore.set_value(tree_iter, 1, pixbufFromColor(label.color))

    def refreshStatusStore(self) -> None:
        self.statusStore.clear()

        for status in self.project.outline.statuses:
            tree_iter = self.statusStore.append()

            if tree_iter is None:
                continue

            self.statusStore.set_value(tree_iter, 0, validString(status.name))

    def refreshCharactersStore(self) -> None:
        self.charactersStore.clear()

        tree_iter = self.charactersStore.append()
        self.charactersStore.set_value(tree_iter, 0, -1)
        self.charactersStore.set_value(tree_iter, 1, validString("None"))

        theme = Gtk.IconTheme.get_default()
        pixbuf = theme.load_icon("dialog-error", 20, 0)
        self.charactersStore.set_value(tree_iter, 2, pixbuf)

        for character in self.project.characters:
            if (not character.POV) or (character.UID is None):
                continue

            tree_iter = self.charactersStore.append()

            if tree_iter is None:
                continue

            self.charactersStore.set_value(tree_iter, 0, validVariantValue(character.UID))
            self.charactersStore.set_value(tree_iter, 1, validString(character.name))
            self.charactersStore.set_value(tree_iter, 2, pixbufFromColor(character.color))

    def reloadOutlineData(self, outlineItem: Optional[OutlineItem]) -> None:
        if outlineItem is None:
            self.widget.set_sensitive(False)
            return

        self.titleLabel.set_text(validString(outlineItem.title))
        self.goalBuffer.set_text(validString(outlineItem.goalCount()), -1)

        self.oneLineEntry.set_text(validString(outlineItem.summarySentence))
        self.summaryBuffer.set_text(validString(outlineItem.summaryFull))
        self.notesBuffer.set_text(validString(outlineItem.notes))

        self.widget.set_sensitive(True)
