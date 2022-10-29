#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from manuskript.data import Plots, PlotLine, PlotStep, Importance
from manuskript.ui.util import rgbaFromColor, pixbufFromColor
from manuskript.util import validString, invalidString, validInt, invalidInt


class PlotView:

    def __init__(self, plots: Plots):
        self.plots = plots
        self.plotLine = None
        self.plotStep = None

        builder = Gtk.Builder()
        builder.add_from_file("ui/plot.glade")

        self.widget = builder.get_object("plot_view")

        self.plotsStore = builder.get_object("plots_store")
        self.refreshPlotsStore()

        self.charactersStore = builder.get_object("characters_store")
        self.refreshCharacterStore()

        self.filteredPlotsStore = builder.get_object("filtered_plots_store")
        self.mainPlotsStore = builder.get_object("main_plots_store")
        self.secondaryPlotsStore = builder.get_object("secondary_plots_store")
        self.minorPlotsStore = builder.get_object("minor_plots_store")

        self.filterPlotsBuffer = builder.get_object("filter_plots")

        self.filterPlotsBuffer.connect("deleted-text", self.filterPlotsDeletedText)
        self.filterPlotsBuffer.connect("inserted-text", self.filterPlotsInsertedText)

        self.filteredPlotsStore.set_visible_func(self.filterPlots)
        self.filteredPlotsStore.refilter()

        self.mainPlotsStore.set_visible_func(
            lambda model, iter, userdata: model[iter][2] == Importance.MAIN.value)
        self.secondaryPlotsStore.set_visible_func(
            lambda model, iter, userdata: model[iter][2] == Importance.SECONDARY.value)
        self.minorPlotsStore.set_visible_func(
            lambda model, iter, userdata: model[iter][2] == Importance.MINOR.value)

        self.mainPlotsStore.refilter()
        self.secondaryPlotsStore.refilter()
        self.minorPlotsStore.refilter()

        self.plotSelections = [
            builder.get_object("minor_plot_selection"),
            builder.get_object("secondary_plot_selection"),
            builder.get_object("main_plot_selection")
        ]

        for selection in self.plotSelections:
            selection.connect("changed", self.plotSelectionChanged)

        self.addPlotButton = builder.get_object("add_plot")
        self.removePlotButton = builder.get_object("remove_plot")

        self.addPlotButton.connect("clicked", self.addPlotClicked)
        self.removePlotButton.connect("clicked", self.removePlotClicked)

        self.importanceCombo = builder.get_object("importance")

        self.nameBuffer = builder.get_object("name")
        self.descriptionBuffer = builder.get_object("description")
        self.resultBuffer = builder.get_object("result")
        self.stepSummaryBuffer = builder.get_object("step_summary")

        self.nameBuffer.connect("deleted-text", self.nameDeletedText)
        self.nameBuffer.connect("inserted-text", self.nameInsertedText)

        self.plotCharactersStore = builder.get_object("plot_characters_store")

        self.plotCharactersStore.set_visible_func(self.filterPlotCharacters)
        self.plotCharactersStore.refilter()

        self.descriptionBuffer.connect("changed", self.descriptionChanged)
        self.resultBuffer.connect("changed", self.resultChanged)
        self.stepSummaryBuffer.connect("changed", self.stepSummaryChanged)

    def refreshPlotsStore(self):
        self.plotsStore.clear()

        for plotLine in self.plots:
            tree_iter = self.plotsStore.append()

            if tree_iter is None:
                continue

            self.plotsStore.set_value(tree_iter, 0, plotLine.UID.value)
            self.plotsStore.set_value(tree_iter, 1, validString(plotLine.name))
            self.plotsStore.set_value(tree_iter, 2, Importance.asValue(plotLine.importance))

    def refreshCharacterStore(self):
        self.charactersStore.clear()

        for character in self.plots.characters:
            tree_iter = self.charactersStore.append()

            if tree_iter is None:
                continue

            self.charactersStore.set_value(tree_iter, 0, character.UID.value)
            self.charactersStore.set_value(tree_iter, 1, validString(character.name))
            self.charactersStore.set_value(tree_iter, 2, pixbufFromColor(character.color))

    def loadPlotData(self, plotLine: PlotLine):
        self.plotLine = None

        self.importanceCombo.set_active(Importance.asValue(plotLine.importance))

        self.nameBuffer.set_text(validString(plotLine.name), -1)
        self.descriptionBuffer.set_text(validString(plotLine.description), -1)
        self.resultBuffer.set_text(validString(plotLine.result), -1)

        self.plotLine = plotLine

        self.plotCharactersStore.refilter()

    def unloadPlotData(self):
        self.plotLine = None

        self.nameBuffer.set_text("", -1)
        self.descriptionBuffer.set_text("", -1)
        self.resultBuffer.set_text("", -1)
        self.stepSummaryBuffer.set_text("", -1)

    def plotSelectionChanged(self, selection: Gtk.TreeSelection):
        model, tree_iter = selection.get_selected()

        if tree_iter is None:
            self.unloadPlotData()
            return

        for other in self.plotSelections:
            if other != selection:
                other.unselect_all()

        plotLine = self.plots.getLineByID(model[tree_iter][0])

        if plotLine is None:
            self.unloadPlotData()
        else:
            self.loadPlotData(plotLine)

    def addPlotClicked(self, button: Gtk.Button):
        name = invalidString(self.filterPlotsBuffer.get_text())
        plotLine = self.plots.addLine(name)

        if plotLine is None:
            return

        if self.plotLine is not None:
            plotLine.importance = self.plotLine.importance

        self.refreshPlotsStore()

    def removePlotClicked(self, button: Gtk.Button):
        if self.plotLine is None:
            return

        self.plots.removeLine(self.plotLine)
        self.refreshPlotsStore()

    def filterPlots(self, model, iter, userdata):
        name = validString(model[iter][1])
        text = validString(self.filterPlotsBuffer.get_text())

        return text.lower() in name.lower()

    def filterPlotsChanged(self, buffer: Gtk.EntryBuffer):
        self.filteredPlotsStore.refilter()

    def filterPlotsDeletedText(self, buffer: Gtk.EntryBuffer, position: int, n_chars: int):
        self.filterPlotsChanged(buffer)

    def filterPlotsInsertedText(self, buffer: Gtk.EntryBuffer, position: int, chars: str, n_chars: int):
        self.filterPlotsChanged(buffer)

    def nameChanged(self, buffer: Gtk.EntryBuffer):
        if self.plotLine is None:
            return

        text = buffer.get_text()
        name = invalidString(text)

        self.plotLine.name = name

        plot_id = self.plotLine.UID.value

        for row in self.plotsStore:
            if row[0] == plot_id:
                row[1] = validString(name)
                break

    def nameDeletedText(self, buffer: Gtk.EntryBuffer, position: int, n_chars: int):
        self.nameChanged(buffer)

    def nameInsertedText(self, buffer: Gtk.EntryBuffer, position: int, chars: str, n_chars: int):
        self.nameChanged(buffer)

    def filterPlotCharacters(self, model, iter, userdata):
        ID = validInt(model[iter][0])

        if self.plotLine is None:
            return False

        return ID in self.plotLine.characters

    def descriptionChanged(self, buffer: Gtk.TextBuffer):
        if self.plotLine is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.plotLine.description = invalidString(text)

    def resultChanged(self, buffer: Gtk.TextBuffer):
        if self.plotLine is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.plotLine.result = invalidString(text)

    def stepSummaryChanged(self, buffer: Gtk.TextBuffer):
        if self.plotStep is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.plotStep.summary = invalidString(text)

    def show(self):
        self.widget.show_all()
