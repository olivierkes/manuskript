#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from manuskript.data import Project, OutlineFolder, OutlineText, OutlineItem, OutlineState, Goal
from manuskript.ui.editor import GridItem
from manuskript.ui.util import pixbufFromColor, iconByOutlineItemType
from manuskript.util import validString, validInt, safeFraction


class EditorView:

    def __init__(self, project: Project):
        self.project = project
        self.outlineItem = None
        self.editorItems = list()

        builder = Gtk.Builder()
        builder.add_from_file("ui/editor.glade")

        self.widget = builder.get_object("editor_view")

        self.labelStore = builder.get_object("label_store")
        self.refreshLabelStore()

        self.statusStore = builder.get_object("status_store")
        self.refreshStatusStore()

        self.outlineStore = builder.get_object("outline_store")
        self.refreshOutlineStore()

        self.viewStack = builder.get_object("view_stack")

        self.editorTextBuffer = builder.get_object("editor_text")
        self.editorFlowbox = builder.get_object("editor_flowbox")

        self.editorFlowbox.connect("child-activated", self._editorFlowboxChildActivated)

        self.upButtons = [
            builder.get_object("up"),
            builder.get_object("up_")
        ]

        for button in self.upButtons:
            button.connect("clicked", self._upButtonClicked)

        self.counterLabel = builder.get_object("counter")
        self.counterProgressBar = builder.get_object("counter_progress")

        self.unloadOutlineData()

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

        icon = iconByOutlineItemType(outlineItem)

        if type(outlineItem) is OutlineFolder:
            for item in outlineItem:
                self.__appendOutlineItem(item, tree_iter)

        wordCount = validInt(outlineItem.textCount())
        goal = validInt(outlineItem.goalCount())
        progress = 100 * safeFraction(wordCount, 0, goal)

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

    def loadOutlineData(self, outlineItem: OutlineItem):
        if outlineItem is None:
            self.unloadOutlineData()
            return

        self.outlineItem = None
        self.loadEditorData(outlineItem)

        if type(outlineItem) is OutlineText:
            self.viewStack.set_visible_child_name("page_text")
        else:
            self.viewStack.set_visible_child_name("page_stack")

        goalKind = outlineItem.goalKind()
        textCount = outlineItem.textCount(goalKind)
        goalCount = outlineItem.goalCount()

        self.counterLabel.set_text("{0} {1}".format(textCount, goalKind.name.lower()))
        self.counterProgressBar.set_text("{0} / {1} {2}".format(textCount, goalCount, goalKind.name.lower()))
        self.counterProgressBar.set_fraction(safeFraction(textCount, 0, goalCount))

        self.outlineItem = outlineItem

    def unloadOutlineData(self):
        self.outlineItem = None

        self.loadEditorData(None)

        goalKind = self.project.outline.goalKind()
        textCount = self.project.outline.textCount(goalKind)
        goalCount = self.project.outline.goalCount()

        self.counterLabel.set_text("{0} {1}".format(textCount, goalKind.name.lower()))
        self.counterProgressBar.set_text("{0} / {1} {2}".format(textCount, goalCount, goalKind.name.lower()))
        self.counterProgressBar.set_fraction(safeFraction(textCount, 0, goalCount))

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
        self.editorItems = list()
        self.outlineItem = None

        start_iter, end_iter = self.editorTextBuffer.get_bounds()
        self.editorTextBuffer.delete(start_iter, end_iter)

        if outlineItem is None:
            self.editorItems = self.project.outline.items
        elif type(outlineItem) is OutlineFolder:
            self.editorItems = outlineItem.items
        elif type(outlineItem) is OutlineText:
            self.__appendOutlineItemText(outlineItem)

        self.editorFlowbox.foreach(self.editorFlowbox.remove)
        if len(self.editorItems) <= 0:
            self.outlineItem = outlineItem
            return

        for item in self.editorItems:
            self.__appendOutlineItemText(item)

        for item in self.editorItems:
            self.editorFlowbox.insert(GridItem(item).widget, -1)

        self.outlineItem = outlineItem

    def _editorFlowboxChildActivated(self, box: Gtk.FlowBox, child: Gtk.FlowBoxChild):
        if child is None:
            return

        index = child.get_index()
        if (index < 0) or (index >= len(self.editorItems)):
            return

        self.loadOutlineData(self.editorItems[index])

    def _upButtonClicked(self, button: Gtk.Button):
        if self.outlineItem is None:
            return

        self.loadOutlineData(self.outlineItem.parentItem())

    def show(self):
        self.widget.show_all()
