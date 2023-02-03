#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk

from manuskript.data import Outline, OutlineFolder, OutlineText, OutlineItem, OutlineState, Plots, PlotLine, Characters, Character, Importance, Goal
from manuskript.ui.util import rgbaFromColor, pixbufFromColor
from manuskript.util import validString, invalidString, validInt, invalidInt, CounterKind, countText


class OutlineView:

    def __init__(self, outline: Outline):
        self.outline = outline
        self.outlineItem = None
        self.outlineCompletion = []

        builder = Gtk.Builder()
        builder.add_from_file("ui/outline.glade")

        self.widget = builder.get_object("outline_view")

        self.labelStore = builder.get_object("label_store")
        self.refreshLabelStore()

        self.statusStore = builder.get_object("status_store")
        self.refreshStatusStore()

        self.plotsStore = builder.get_object("plots_store")
        self.refreshPlotsStore()

        self.charactersStore = builder.get_object("characters_store")
        self.refreshCharactersStore()

        self.outlineStore = builder.get_object("outline_store")
        self.refreshOutlineStore()

        self.mainPlotsStore = builder.get_object("main_plots_store")
        self.secondaryPlotsStore = builder.get_object("secondary_plots_store")
        self.minorPlotsStore = builder.get_object("minor_plots_store")

        self.mainPlotsStore.set_visible_func(
            lambda model, iterator, userdata: model[iterator][2] == Importance.MAIN.value)
        self.secondaryPlotsStore.set_visible_func(
            lambda model, iterator, userdata: model[iterator][2] == Importance.SECONDARY.value)
        self.minorPlotsStore.set_visible_func(
            lambda model, iterator, userdata: model[iterator][2] == Importance.MINOR.value)

        self.mainPlotsStore.refilter()
        self.secondaryPlotsStore.refilter()
        self.minorPlotsStore.refilter()

        self.plotSelections = [
            builder.get_object("minor_plot_selection"),
            builder.get_object("secondary_plot_selection"),
            builder.get_object("main_plot_selection")
        ]

        for selection in self.plotSelections:
            selection.connect("changed", self._plotSelectionChanged)

        self.filterOutlineBuffer = builder.get_object("filter_outline")

        self.filterOutlineBuffer.connect("deleted-text", self._filterOutlineDeletedText)
        self.filterOutlineBuffer.connect("inserted-text", self._filterOutlineInsertedText)

        self.filteredOutlineStore = builder.get_object("filtered_outline_store")

        self.filteredOutlineStore.set_visible_func(self._filterOutline)
        self.filteredOutlineStore.refilter()

        self.outlineSelection = builder.get_object("outline_selection")

        self.outlineSelection.connect("changed", self._outlineSelectionChanged)

        self.goalBuffer = builder.get_object("goal")
        self.oneLineSummaryBuffer = builder.get_object("one_line_summary")
        self.fewSentencesSummaryBuffer = builder.get_object("few_sentences_summary")

        self.goalBuffer.connect("deleted-text", self._goalDeletedText)
        self.goalBuffer.connect("inserted-text", self._goalInsertedText)

        self.oneLineSummaryBuffer.connect("deleted-text", self._oneLineSummaryDeletedText)
        self.oneLineSummaryBuffer.connect("inserted-text", self._oneLineSummaryInsertedText)

        self.fewSentencesSummaryBuffer.connect("changed", self._fewSentencesSummaryChanged)

        self.unloadOutlineData()

    def refreshLabelStore(self):
        self.labelStore.clear()

        for label in self.outline.labels:
            tree_iter = self.labelStore.append()

            if tree_iter is None:
                continue

            self.labelStore.set_value(tree_iter, 0, validString(label.name))
            self.labelStore.set_value(tree_iter, 1, pixbufFromColor(label.color))

    def refreshStatusStore(self):
        self.statusStore.clear()

        for status in self.outline.statuses:
            tree_iter = self.statusStore.append()

            if tree_iter is None:
                continue

            self.statusStore.set_value(tree_iter, 0, validString(status.name))

    def refreshPlotsStore(self):
        self.plotsStore.clear()

        for plotLine in self.outline.plots:
            tree_iter = self.plotsStore.append()

            if tree_iter is None:
                continue

            self.plotsStore.set_value(tree_iter, 0, plotLine.UID.value)
            self.plotsStore.set_value(tree_iter, 1, validString(plotLine.name))
            self.plotsStore.set_value(tree_iter, 2, Importance.asValue(plotLine.importance))

    def refreshCharactersStore(self):
        self.charactersStore.clear()

        for character in self.outline.plots.characters:
            tree_iter = self.charactersStore.append()

            if tree_iter is None:
                continue

            self.charactersStore.set_value(tree_iter, 0, character.UID.value)
            self.charactersStore.set_value(tree_iter, 1, validString(character.name))
            self.charactersStore.set_value(tree_iter, 2, pixbufFromColor(character.color))

    def __updateOutlineItem(self, tree_iter, outlineItem: OutlineItem):
        if type(outlineItem) is OutlineFolder:
            icon = "folder-symbolic"
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

    def __completeOutlineItem(self):
        (tree_iter, outlineItem) = self.outlineCompletion.pop(0)

        if outlineItem.state != OutlineState.COMPLETE:
            outlineItem.load(False)

        self.__updateOutlineItem(tree_iter, outlineItem)

        return len(self.outlineCompletion) > 0

    def __appendOutlineItem(self, outlineItem: OutlineItem, parent_iter=None):
        tree_iter = self.outlineStore.append(parent_iter)

        if tree_iter is None:
            return

        if type(outlineItem) is OutlineFolder:
            for item in outlineItem:
                self.__appendOutlineItem(item, tree_iter)

        if outlineItem.state != OutlineState.COMPLETE:
            if len(self.outlineCompletion) == 0:
                GObject.idle_add(self.__completeOutlineItem)

            self.outlineCompletion.append((tree_iter, outlineItem))

        self.__updateOutlineItem(tree_iter, outlineItem)

    def refreshOutlineStore(self):
        self.outlineStore.clear()

        for item in self.outline.items:
            self.__appendOutlineItem(item)

    def _plotSelectionChanged(self, selection: Gtk.TreeSelection):
        model, tree_iter = selection.get_selected()

        if tree_iter is None:
            return

        for other in self.plotSelections:
            if other != selection:
                other.unselect_all()

    def loadOutlineData(self, outlineItem: OutlineItem):
        self.outlineItem = None

        self.goalBuffer.set_text(validString(outlineItem.goal), -1)
        self.oneLineSummaryBuffer.set_text(validString(outlineItem.summarySentence), -1)
        self.fewSentencesSummaryBuffer.set_text(validString(outlineItem.summaryFull), -1)

        self.outlineItem = outlineItem

    def unloadOutlineData(self):
        self.outlineItem = None

        self.goalBuffer.set_text("", -1)
        self.oneLineSummaryBuffer.set_text("", -1)
        self.fewSentencesSummaryBuffer.set_text("", -1)

    def _outlineSelectionChanged(self, selection: Gtk.TreeSelection):
        model, tree_iter = selection.get_selected()

        if tree_iter is None:
            self.unloadOutlineData()
            return

        outlineItem = self.outline.getItemByID(model[tree_iter][0])

        if outlineItem is None:
            self.unloadOutlineData()
        else:
            self.loadOutlineData(outlineItem)

    def __matchOutlineItemByText(self, outlineItem: OutlineItem, text: str):
        if type(outlineItem) is OutlineFolder:
            for item in outlineItem:
                if self.__matchOutlineItemByText(item, text):
                    return True

        title = validString(outlineItem.title)
        return text in title.lower()

    def _filterOutline(self, model, iterator, userdata):
        outlineItem = self.outline.getItemByID(model[iterator][0])

        if outlineItem is None:
            return False

        text = validString(self.filterOutlineBuffer.get_text())
        return self.__matchOutlineItemByText(outlineItem, text.lower())

    def __filterOutlineChanged(self, buffer: Gtk.EntryBuffer):
        self.filteredOutlineStore.refilter()

    def _filterOutlineDeletedText(self, buffer: Gtk.EntryBuffer, position: int, n_chars: int):
        self.__filterOutlineChanged(buffer)

    def _filterOutlineInsertedText(self, buffer: Gtk.EntryBuffer, position: int, chars: str, n_chars: int):
        self.__filterOutlineChanged(buffer)

    def __goalChanged(self, buffer: Gtk.EntryBuffer):
        if self.outlineItem is None:
            return

        text = buffer.get_text()

        self.outlineItem.goal = Goal.parse(text)

        outline_id = self.outlineItem.UID.value

        wordCount = validInt(self.outlineItem.textCount())
        goal = validInt(self.outlineItem.goalCount())
        progress = 0

        if goal > wordCount:
            progress = 100 * wordCount / goal
        elif goal > 0:
            progress = 100

        for row in self.outlineStore:
            if row[0] == outline_id:
                row[6] = goal
                row[7] = progress
                break

    def _goalDeletedText(self, buffer: Gtk.EntryBuffer, position: int, n_chars: int):
        self.__goalChanged(buffer)

    def _goalInsertedText(self, buffer: Gtk.EntryBuffer, position: int, chars: str, n_chars: int):
        self.__goalChanged(buffer)

    def __oneLineSummaryChanged(self, buffer: Gtk.EntryBuffer):
        if self.outlineItem is None:
            return

        text = buffer.get_text()
        summary = invalidString(text)

        self.outlineItem.summarySentence = summary

    def _oneLineSummaryDeletedText(self, buffer: Gtk.EntryBuffer, position: int, n_chars: int):
        self.__oneLineSummaryChanged(buffer)

    def _oneLineSummaryInsertedText(self, buffer: Gtk.EntryBuffer, position: int, chars: str, n_chars: int):
        self.__oneLineSummaryChanged(buffer)

    def _fewSentencesSummaryChanged(self, buffer: Gtk.TextBuffer):
        if self.outlineItem is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.outlineItem.summaryFull = invalidString(text)

    def show(self):
        self.widget.show_all()
