#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from manuskript.data import Project, Outline, OutlineFolder, OutlineText, OutlineItem, OutlineState, Plots, PlotLine, Characters, Character, Importance, Goal
from manuskript.ui.util import rgbaFromColor, pixbufFromColor
from manuskript.util import validString, invalidString, validInt, invalidInt, CounterKind, countText

import inspect


class EditorView:

    def __init__(self, project: Project):
        self.project = project

        builder = Gtk.Builder()
        builder.add_from_file("ui/editor.glade")

        self.widget = builder.get_object("editor_view")

        self.labelStore = builder.get_object("label_store")
        self.refreshLabelStore()

        self.statusStore = builder.get_object("status_store")
        self.refreshStatusStore()

        self.outlineStore = builder.get_object("outline_store")
        self.refreshOutlineStore()

        self.editorTextBuffer = builder.get_object("editor_text")

        self.editorFlowbox = builder.get_object("editor_flowbox")
        self.loadEditorData(None)

    def refreshLabelStore(self):
        self.labelStore.clear()

        for label in self.project.labels:
            tree_iter = self.labelStore.append()

            if tree_iter is None:
                continue

            self.labelStore.set_value(tree_iter, 0, validString(label.name))
            self.labelStore.set_value(tree_iter, 1, pixbufFromColor(label.color))

    def refreshStatusStore(self):
        self.statusStore.clear()

        for status in self.project.statuses:
            tree_iter = self.statusStore.append()

            if tree_iter is None:
                continue

            self.statusStore.set_value(tree_iter, 0, validString(status.name))

    @classmethod
    def __getIconByOutlineType(cls, outlineItem: OutlineItem):
        if type(outlineItem) is OutlineFolder:
            return "folder-symbolic"
        elif type(outlineItem) is OutlineText:
            return "emblem-documents-symbolic"
        else:
            return "folder-documents-symbolic"

    def __appendOutlineItem(self, outlineItem: OutlineItem, parent_iter=None):
        tree_iter = self.outlineStore.append(parent_iter)

        if tree_iter is None:
            return

        if outlineItem.state != OutlineState.COMPLETE:
            outlineItem.load(False)

        icon = EditorView.__getIconByOutlineType(outlineItem)

        if type(outlineItem) is OutlineFolder:
            for item in outlineItem:
                self.__appendOutlineItem(item, tree_iter)

        wordCount = validInt(outlineItem.textCount())
        goal = validInt(outlineItem.goalCount())
        progress = 0

        if goal > wordCount:
            progress = 100 * wordCount / goal
        elif goal > 0:
            progress = 100

        self.outlineStore.set_value(tree_iter, 0, outlineItem.UID.value)
        self.outlineStore.set_value(tree_iter, 1, validString(outlineItem.title))
        self.outlineStore.set_value(tree_iter, 2, validString(outlineItem.label))
        self.outlineStore.set_value(tree_iter, 3, validString(outlineItem.status))
        self.outlineStore.set_value(tree_iter, 4, outlineItem.compile)
        self.outlineStore.set_value(tree_iter, 5, wordCount)
        self.outlineStore.set_value(tree_iter, 6, goal)
        self.outlineStore.set_value(tree_iter, 7, progress)
        self.outlineStore.set_value(tree_iter, 8, icon)

    def refreshOutlineStore(self):
        self.outlineStore.clear()

        for item in self.project.outline.items:
            self.__appendOutlineItem(item)

    def __appendOutlineItemText(self, outlineItem: OutlineItem):
        end_iter = self.editorTextBuffer.get_end_iter()

        if type(outlineItem) is OutlineFolder:
            if self.editorTextBuffer.get_line_count() > 1:
                self.editorTextBuffer.insert_with_tags_by_name(end_iter, "\n", "none")

            end_iter = self.editorTextBuffer.get_end_iter()

            self.editorTextBuffer.insert_with_tags_by_name(end_iter, outlineItem.title + "\n", "h1")

            for item in outlineItem:
                self.__appendOutlineItemText(item)

            return True
        elif type(outlineItem) is OutlineText:
            outlineText: OutlineText = outlineItem

            if (outlineText.text is None) or (len(outlineText.text) <= 0):
                return False

            self.editorTextBuffer.insert(end_iter, outlineText.text)
            return True
        else:
            return False

    def loadEditorData(self, outlineItem: OutlineItem | None):
        self.editorTextBuffer.set_text("")

        for item in self.project.outline.items:
            self.__appendOutlineItemText(item)

        for item in self.project.outline.items:
            child = Gtk.FlowBoxChild()

            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

            icon = EditorView.__getIconByOutlineType(item)

            iconImage = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU)
            titleLabel = Gtk.Label(item.title)
            summaryLabel = Gtk.Label(item.summaryFull)

            titleLabel.set_ellipsize(Pango.EllipsizeMode.END)
            summaryLabel.set_ellipsize(Pango.EllipsizeMode.END)
            summaryLabel.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
            summaryLabel.set_line_wrap(True)
            summaryLabel.set_max_width_chars(20)

            hbox.pack_start(iconImage, False, True, 4)
            hbox.pack_start(titleLabel, False, True, 4)

            vbox.pack_start(hbox, False, True, 4)
            vbox.pack_start(summaryLabel, False, True, 4)

            child.add(vbox)

            self.editorFlowbox.add(child)

    def show(self):
        self.widget.show_all()
