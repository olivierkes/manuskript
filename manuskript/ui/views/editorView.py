#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from manuskript.data import Project, Outline, OutlineFolder, OutlineText, OutlineItem, OutlineState, Plots, PlotLine, Characters, Character, Importance, Goal
from manuskript.ui.util import rgbaFromColor, pixbufFromColor
from manuskript.util import validString, invalidString, validInt, invalidInt, CounterKind, countText


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

    def __appendOutlineItem(self, outlineItem: OutlineItem, parent_iter=None):
        tree_iter = self.outlineStore.append(parent_iter)

        if tree_iter is None:
            return

        if outlineItem.state != OutlineState.COMPLETE:
            outlineItem.load(False)

        if type(outlineItem) is OutlineFolder:
            icon = "folder-symbolic"

            for item in outlineItem:
                self.__appendOutlineItem(item, tree_iter)
        elif type(outlineItem) is OutlineText:
            icon = "emblem-documents-symbolic"
        else:
            icon = "folder-documents-symbolic"

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

    def show(self):
        self.widget.show_all()
