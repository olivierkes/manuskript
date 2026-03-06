#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import GLib, Gtk, Gdk

from manuskript.ui.views.abstractView import AbstractView

from manuskript.data import Outline, OutlineFolder, OutlineText, OutlineItem, OutlineState, Plots, PlotLine, Characters, Character, Importance, Goal, Color
from manuskript.ui.util import rgbaFromColor, pixbufFromColor
from manuskript.util import validString, invalidString, validInt, invalidInt, CounterKind, countText
from manuskript.ui.picker import LabelPicker, CharacterPicker, AbstractGridPicker

class OutlineView(AbstractView):

    def __init__(self, outline: Outline):
        AbstractView.__init__(self)
        
        self.outline: Outline = outline
        self.outlineItem: OutlineItem = None
        self.outlineCompletion: list = []
        self.idleCompletion = 0

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

        self.outlineTreeview = builder.get_object("outline_treeview")
        self.outlineTreeview.connect("button-press-event", self._outlineTreeviewClicked)

        self.outlineTitle = builder.get_object("outline_title")
        self.outlineTitle.connect("edited", self._outlineTitleEdited)

        self.labelPopover:LabelPicker = LabelPicker(self.outline.labels)
        self.labelPopover.connect("label-selected", self._labelPopoverItemSelected)

        self.povPopover:CharacterPicker = CharacterPicker(self.outline.plots.characters, pickPovOnly=True)
        self.povPopover.connect("character-selected", self._povPopoverItemSelected)

        self.goalBuffer = builder.get_object("goal")
        self.oneLineSummaryBuffer = builder.get_object("one_line_summary")
        self.fewSentencesSummaryBuffer = builder.get_object("few_sentences_summary")

        self.goalBuffer.connect("deleted-text", self._goalDeletedText)
        self.goalBuffer.connect("inserted-text", self._goalInsertedText)

        self.povCombo = builder.get_object("pov_combo")
        self.povCombo.connect("changed", self._povChanged)

        self.statusCombo = builder.get_object("outline_status")
        self.statusCombo.connect("changed", self._statusChanged)

        self.oneLineSummaryBuffer.connect("deleted-text", self._oneLineSummaryDeletedText)
        self.oneLineSummaryBuffer.connect("inserted-text", self._oneLineSummaryInsertedText)

        self.fewSentencesSummaryBuffer.connect("changed", self._fewSentencesSummaryChanged)

        self.unloadOutlineData()

    def populateLabelList(self):
        for pixbuf, text in self.labelStore:
            row = Gtk.ListBoxRow()
            box = Gtk.Box(spacing=6)

            image = Gtk.Image.new_from_pixbuf(pixbuf)
            label = Gtk.Label(label=text, xalign=0)

            box.pack_start(image, False, False, 0)
            box.pack_start(label, True, True, 0)

            row.add(box)
            row.pixbuf = pixbuf
            row.text = text

            self.labelListbox.add(row)

        self.labelListbox.show_all()

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

        tree_iter = self.charactersStore.append()
        self.charactersStore.set_value(tree_iter, 0, -1)
        self.charactersStore.set_value(tree_iter, 1, validString("None"))

        theme = Gtk.IconTheme.get_default()
        pixbuf = theme.load_icon("dialog-error", 20, 0)
        self.charactersStore.set_value(tree_iter, 2, pixbuf)

        for character in self.outline.plots.characters:
            if not character.POV:
                continue

            tree_iter = self.charactersStore.append()

            if tree_iter is None:
                continue

            self.charactersStore.set_value(tree_iter, 0, character.UID.value)
            self.charactersStore.set_value(tree_iter, 1, validString(character.name))
            self.charactersStore.set_value(tree_iter, 2, pixbufFromColor(character.color))

    def _findOutlineIterById(self, store, uid, parent=None):
        it = store.iter_children(parent)
        while it:
            if store[it][0] == uid.value:
                return it
            child = self._findOutlineIterById(store, uid, it)
            if child:
                return child
            it = store.iter_next(it)
        return None

    def __updateOutlineItemInStore(self, outlineItem: OutlineItem):
        iter = self._findOutlineIterById(self.outlineStore, outlineItem.UID)
        if iter:
            self.__updateOutlineItem(iter, outlineItem)

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
        self.outlineStore.set_value(tree_iter, 9, self._getLabelPixbuf(validString(outlineItem.label)))

        self.outlineStore.set_value(tree_iter, 10, "")
        self.outlineStore.set_value(tree_iter, 11, None)

        if outlineItem.POV:
            povName = outlineItem.POV.name
            povPixbuf = pixbufFromColor(outlineItem.POV.color)
            if povName!=None:
                self.outlineStore.set_value(tree_iter, 10, povName)
                self.outlineStore.set_value(tree_iter, 11, povPixbuf)

    def _getLabelPixbuf(self, labelName: str):
        if labelName=="":
            return None

        for row in self.labelStore:
            if row[0] == labelName:
                return row[1]
            
        return None

    def __completeOutlineItem(self):
        outlineItem: OutlineItem
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
                self.idleCompletion = GLib.idle_add(self.__completeOutlineItem)

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

    def setPovComboById(self, character_id: int):
        store = self.charactersStore

        it = store.get_iter_first()
        while it:
            if store[it][0] == character_id:
                self.povCombo.set_active_iter(it)
                return
            it = store.iter_next(it)

        self.povCombo.set_active(-1)

    def _povChanged(self, combo):
        if not self.outlineItem:
            return
        
        model = combo.get_model()
        tree_iter = combo.get_active_iter()
        
        if tree_iter is None:
            self.current_character = None
            return
        
        povId = model[tree_iter][0] 
        if povId!=-1:
            self.outlineItem.POV = self.outline.characters.getPOVByID(validInt(povId))
        else:
            self.outlineItem.POV = None

        self.__updateOutlineItemInStore(self.outlineItem)


    def loadOutlineData(self, outlineItem: OutlineItem):
        self.outlineItem = None

        self.goalBuffer.set_text(validString(outlineItem.goal), -1)
        self.oneLineSummaryBuffer.set_text(validString(outlineItem.summarySentence), -1)
        self.fewSentencesSummaryBuffer.set_text(validString(outlineItem.summaryFull), -1)
        if outlineItem.POV:
            self.setPovComboById(validInt(outlineItem.POV.UID.value))

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

    def __updateGoalValue(self, model, path, treeiter, userdata):
        id = model[treeiter][0]

        if userdata["outline_id"] == id:
            model[treeiter][6] = userdata["goal"]
            model[treeiter][7] = userdata["progress"]
            return True
        
        return False

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

        userdata = {
            "outline_id": outline_id,
            "goal": goal,
            "progress": progress
        }

        self.outlineStore.foreach(self.__updateGoalValue, userdata)

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

    def _outlineTreeviewClicked(self, treeview: Gtk.TreeView, event):
        if event.button != 1 or event.type != Gdk.EventType._2BUTTON_PRESS:
            return False
                
        result = treeview.get_path_at_pos(int(event.x), int(event.y))
        if not result:
            return False
        
        path, column, cell_x, cell_y = result

        if column.get_title() == "Label":
            self.showPopoverOverTreeview(treeview, path, event, column, self.labelPopover)
            return True
        
        if column.get_title() == "POV":
            self.showPopoverOverTreeview(treeview, path, event, column, self.povPopover)

        return False
    
    def showPopoverOverTreeview(self, treeview: Gtk.TreeView, path: Gtk.TreePath, event: Gdk.Event, column: Gtk.TreeViewColumn, popover: AbstractGridPicker):
        self.current_path = path

        popover.set_relative_to(treeview)

        cellRect = treeview.get_cell_area(path, column)

        x, y = treeview.convert_bin_window_to_widget_coords(
            cellRect.x,
            cellRect.y
        )

        cellRect.x = x
        cellRect.y = y

        popover.set_pointing_to(cellRect)
        popover.set_position(Gtk.PositionType.BOTTOM)

        popover.show()

    def _labelPopoverItemSelected(self, labelPicker: LabelPicker, label: str):
        labelText=validString(label)

        model = self.outlineTreeview.get_model()
        iter_ = model.get_iter(self.current_path)
        model.set_value(iter_, 2, labelText)
        model.set_value(iter_, 9, self._getLabelPixbuf(labelText))
        
        item = self.outline.getItemByID(model.get_value(iter_, 0))

        labelObject = self.outline.labels.getLabel(labelText)
        item.label = labelObject

    def _povPopoverItemSelected(self, povPicker: CharacterPicker, character: Character):
        model = self.outlineTreeview.get_model()
        iter_ = model.get_iter(self.current_path)
        model.set_value(iter_, 10, character.name)
        model.set_value(iter_, 11, pixbufFromColor(character.color))
        
        item = self.outline.getItemByID(model.get_value(iter_, 0))
        item.POV = character
        self.loadOutlineData(item)

    def _outlineTitleEdited(self, renderer: Gtk.CellRenderer, path: Gtk.TreePath, newText: str):
        self.outlineStore[path][1] = newText
        self.outlineItem.title = newText

    def _statusChanged(self, cell, path, new_iter):
        comboModel = cell.get_property("model")
        newStatus = comboModel[new_iter][0]

        for status in self.outline.statuses:
            if status.name == newStatus:
                self.outlineItem.status = status
                
        self.__updateOutlineItemInStore(self.outlineItem)
        
        return True

    def renameItem(self, name: str|None = None):
        model, tree_iter = self.outlineSelection.get_selected()

        if tree_iter is None:
            return

        outlineItem = self.outline.getItemByID(model[tree_iter][0])

        if outlineItem is None:
            return

        outlineItem.title = validString(name)
        tree_iter = model.convert_iter_to_child_iter(tree_iter)

        if tree_iter:
            self.__updateOutlineItem(tree_iter, outlineItem)

        self.loadOutlineData(outlineItem)
