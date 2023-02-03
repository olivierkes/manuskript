#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from manuskript.data import Plots, PlotLine, PlotStep, Importance, LinkAction
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
        self.notebook = builder.get_object("plot_notebook")

        self.plotsStore = builder.get_object("plots_store")
        self.refreshPlotsStore()

        self.charactersStore = builder.get_object("characters_store")
        self.refreshCharactersStore()

        self.filteredPlotsStore = builder.get_object("filtered_plots_store")
        self.mainPlotsStore = builder.get_object("main_plots_store")
        self.secondaryPlotsStore = builder.get_object("secondary_plots_store")
        self.minorPlotsStore = builder.get_object("minor_plots_store")

        self.filterPlotsBuffer = builder.get_object("filter_plots")

        self.filterPlotsBuffer.connect("deleted-text", self._filterPlotsDeletedText)
        self.filterPlotsBuffer.connect("inserted-text", self._filterPlotsInsertedText)

        self.filteredPlotsStore.set_visible_func(self._filterPlots)
        self.filteredPlotsStore.refilter()

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

        self.addPlotButton = builder.get_object("add_plot")
        self.removePlotButton = builder.get_object("remove_plot")

        self.addPlotButton.connect("clicked", self._addPlotClicked)
        self.removePlotButton.connect("clicked", self._removePlotClicked)

        self.importanceCombo = builder.get_object("importance")

        self.importanceCombo.connect("changed", self._importanceChanged)

        self.resolutionStepsStore = builder.get_object("resolution_steps_store")
        self.resolutionStepsSelection = builder.get_object("resolution_steps_selection")
        self.addResolutionStepButton = builder.get_object("add_resolution_step")
        self.removeResolutionStepButton = builder.get_object("remove_resolution_step")
        self.resolutionStepsNameRenderer = builder.get_object("resolution_steps_name")
        self.resolutionStepsMetaRenderer = builder.get_object("resolution_steps_meta")

        self.resolutionStepsSelection.connect("changed", self._resolutionStepsSelectionChanged)
        self.addResolutionStepButton.connect("clicked", self._addResolutionStepClicked)
        self.removeResolutionStepButton.connect("clicked", self._removeResolutionStepClicked)
        self.resolutionStepsNameRenderer.connect("edited", self._resolutionStepsNameEdited)
        self.resolutionStepsMetaRenderer.connect("edited", self._resolutionStepsMetaEdited)

        self.nameBuffer = builder.get_object("name")
        self.descriptionBuffer = builder.get_object("description")
        self.resultBuffer = builder.get_object("result")
        self.stepSummaryBuffer = builder.get_object("step_summary")

        self.nameBuffer.connect("deleted-text", self._nameDeletedText)
        self.nameBuffer.connect("inserted-text", self._nameInsertedText)

        self.plotCharactersStore = builder.get_object("plot_characters_store")

        self.plotCharactersStore.set_visible_func(self._filterPlotCharacters)
        self.plotCharactersStore.refilter()

        self.descriptionBuffer.connect("changed", self._descriptionChanged)
        self.resultBuffer.connect("changed", self._resultChanged)
        self.stepSummaryBuffer.connect("changed", self._stepSummaryChanged)

        self.unloadPlotData()

    def refreshPlotsStore(self):
        self.plotsStore.clear()

        for plotLine in self.plots:
            tree_iter = self.plotsStore.append()

            if tree_iter is None:
                continue

            self.plotsStore.set_value(tree_iter, 0, plotLine.UID.value)
            self.plotsStore.set_value(tree_iter, 1, validString(plotLine.name))
            self.plotsStore.set_value(tree_iter, 2, Importance.asValue(plotLine.importance))

    def refreshCharactersStore(self):
        self.charactersStore.clear()

        for character in self.plots.characters:
            tree_iter = self.charactersStore.append()

            if tree_iter is None:
                continue

            self.charactersStore.set_value(tree_iter, 0, character.UID.value)
            self.charactersStore.set_value(tree_iter, 1, validString(character.name))
            self.charactersStore.set_value(tree_iter, 2, pixbufFromColor(character.color))

    def __linkActionPlotLine(self, action, UID, plotLine):
        if action == LinkAction.DELETE:
            return

        self.plotCharactersStore.refilter()

    def loadPlotData(self, plotLine: PlotLine):
        if self.plotLine is not None:
            self.plotLine.links.remove(self.__linkActionPlotLine)

        self.plotLine = None

        self.importanceCombo.set_active(Importance.asValue(plotLine.importance))

        self.nameBuffer.set_text(validString(plotLine.name), -1)
        self.descriptionBuffer.set_text(validString(plotLine.description), -1)
        self.resultBuffer.set_text(validString(plotLine.result), -1)

        self.resolutionStepsStore.clear()

        for step in plotLine:
            tree_iter = self.resolutionStepsStore.append()

            if tree_iter is None:
                continue

            self.resolutionStepsStore.set_value(tree_iter, 0, validInt(step.UID.value))
            self.resolutionStepsStore.set_value(tree_iter, 1, validString(step.name))
            self.resolutionStepsStore.set_value(tree_iter, 2, validString(step.meta))

        self.plotLine = plotLine
        self.notebook.set_sensitive(True)

        if self.plotLine is not None:
            self.plotLine.links.add(self.__linkActionPlotLine)

        self.refreshCharactersStore()
        self.plotCharactersStore.refilter()

    def unloadPlotData(self):
        if self.plotLine is not None:
            self.plotLine.links.remove(self.__linkActionPlotLine)

        self.plotLine = None
        self.notebook.set_sensitive(False)

        self.nameBuffer.set_text("", -1)
        self.descriptionBuffer.set_text("", -1)
        self.resultBuffer.set_text("", -1)
        self.stepSummaryBuffer.set_text("", -1)

        self.resolutionStepsStore.clear()

        self.plotCharactersStore.refilter()

    def _plotSelectionChanged(self, selection: Gtk.TreeSelection):
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

    def _addPlotClicked(self, button: Gtk.Button):
        name = invalidString(self.filterPlotsBuffer.get_text())
        plotLine = self.plots.addLine(name)

        if plotLine is None:
            return

        if self.plotLine is not None:
            plotLine.importance = self.plotLine.importance

        self.refreshPlotsStore()

    def _removePlotClicked(self, button: Gtk.Button):
        if self.plotLine is None:
            return

        self.plots.removeLine(self.plotLine)
        self.refreshPlotsStore()

    def _filterPlots(self, model, iterator, userdata):
        name = validString(model[iterator][1])
        text = validString(self.filterPlotsBuffer.get_text())

        return text.lower() in name.lower()

    def __filterPlotsChanged(self, buffer: Gtk.EntryBuffer):
        self.filteredPlotsStore.refilter()

    def _filterPlotsDeletedText(self, buffer: Gtk.EntryBuffer, position: int, n_chars: int):
        self.__filterPlotsChanged(buffer)

    def _filterPlotsInsertedText(self, buffer: Gtk.EntryBuffer, position: int, chars: str, n_chars: int):
        self.__filterPlotsChanged(buffer)

    def _importanceChanged(self, combo: Gtk.ComboBox):
        if self.plotLine is None:
            return

        tree_iter = combo.get_active_iter()

        if tree_iter is None:
            return

        model = combo.get_model()
        value = model[tree_iter][1]

        importance = Importance.fromValue(value)

        if (importance is None) or (self.plotLine.importance == importance):
            return

        self.plotLine.importance = importance

        plot_id = self.plotLine.UID.value

        for row in self.plotsStore:
            if row[0] == plot_id:
                row[2] = Importance.asValue(importance)
                break

        self.mainPlotsStore.refilter()
        self.secondaryPlotsStore.refilter()
        self.minorPlotsStore.refilter()

        selection = self.plotSelections[importance.value]
        tree_view = selection.get_tree_view()
        model = tree_view.get_model()

        for row in model:
            if row[0] == plot_id:
                selection.select_iter(row.iter)
                break

    def _resolutionStepsSelectionChanged(self, selection: Gtk.TreeSelection):
        model, tree_iter = selection.get_selected()

        self.plotStep = None

        if (tree_iter is None) or (self.plotLine is None):
            self.stepSummaryBuffer.set_text("", -1)
            return

        plotStep = self.plotLine.getStepByID(model[tree_iter][0])

        if plotStep is None:
            self.stepSummaryBuffer.set_text("", -1)
        else:
            self.stepSummaryBuffer.set_text(validString(plotStep.summary), -1)

            self.plotStep = plotStep

    def _addResolutionStepClicked(self, button: Gtk.Button):
        if self.plotLine is None:
            return

        tree_iter = self.resolutionStepsStore.append()

        if tree_iter is None:
            return

        name = "New step"
        meta = "Problem"

        step = self.plotLine.addStep(name, meta)

        self.resolutionStepsStore.set_value(tree_iter, 0, validInt(step.UID.value))
        self.resolutionStepsStore.set_value(tree_iter, 1, validString(step.name))
        self.resolutionStepsStore.set_value(tree_iter, 2, validString(step.meta))

    def _removeResolutionStepClicked(self, button: Gtk.Button):
        if (self.plotLine is None) or (self.plotStep is None):
            return

        model, tree_iter = self.resolutionStepsSelection.get_selected()

        if (model is None) or (tree_iter is None):
            return

        model.remove(tree_iter)

        self.plotLine.removeStep(self.plotStep)

    def _resolutionStepsNameEdited(self, renderer: Gtk.CellRendererText, path: str, text: str):
        if self.plotStep is None:
            return

        model, tree_iter = self.resolutionStepsSelection.get_selected()

        if (model is None) or (tree_iter is None):
            return

        model.set_value(tree_iter, 1, text)

        self.plotStep.name = invalidString(text)

    def _resolutionStepsMetaEdited(self, renderer: Gtk.CellRendererText, path: str, text: str):
        if self.plotStep is None:
            return

        model, tree_iter = self.resolutionStepsSelection.get_selected()

        if (model is None) or (tree_iter is None):
            return

        model.set_value(tree_iter, 2, text)

        self.plotStep.meta = invalidString(text)

    def __nameChanged(self, buffer: Gtk.EntryBuffer):
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

    def _nameDeletedText(self, buffer: Gtk.EntryBuffer, position: int, n_chars: int):
        self.__nameChanged(buffer)

    def _nameInsertedText(self, buffer: Gtk.EntryBuffer, position: int, chars: str, n_chars: int):
        self.__nameChanged(buffer)

    def _filterPlotCharacters(self, model, iterator, userdata):
        ID = validInt(model[iterator][0])

        if self.plotLine is None:
            return False

        return ID in self.plotLine.characters

    def _descriptionChanged(self, buffer: Gtk.TextBuffer):
        if self.plotLine is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.plotLine.description = invalidString(text)

    def _resultChanged(self, buffer: Gtk.TextBuffer):
        if self.plotLine is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.plotLine.result = invalidString(text)

    def _stepSummaryChanged(self, buffer: Gtk.TextBuffer):
        if self.plotStep is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.plotStep.summary = invalidString(text)

    def show(self):
        self.widget.show_all()
