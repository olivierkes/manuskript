#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import GObject, Gtk, Pango, Gdk

from manuskript.data import Project, OutlineFolder, OutlineText, OutlineItem, OutlineState, Goal
from manuskript.ui.editor import GridItem
from manuskript.ui.util import pixbufFromColor, iconByOutlineItemType
from manuskript.util import validString, validInt, safeFraction


class EditorView:

    def __init__(self, project: Project):
        self.project = project
        self.outlineItem = None
        self.outlineCompletion = []
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

        self.editorOutlineStore = builder.get_object("editor_outline_store")

        self.outlineView = builder.get_object("outline_view")
        self.editorOutlineView = builder.get_object("editor_outline_view")

        self.outlineSelection = builder.get_object("outline_selection")
        self.editorOutlineSelection = builder.get_object("editor_outline_selection")

        self.h1Tag = builder.get_object("h1_tag")
        self.h2Tag = builder.get_object("h2_tag")
        self.h3Tag = builder.get_object("h3_tag")
        self.h4Tag = builder.get_object("h4_tag")
        self.h5Tag = builder.get_object("h5_tag")
        self.h6Tag = builder.get_object("h6_tag")
        self.bTag = builder.get_object("b_tag")
        self.iTag = builder.get_object("i_tag")
        self.sTag = builder.get_object("s_tag")
        self.uTag = builder.get_object("u_tag")
        self.noneTag = builder.get_object("none_tag")
        self.pTag = builder.get_object("p_tag")
        self.lineTag = builder.get_object("line_tag")

        self.noneTag.set_priority(0)
        self.pTag.set_priority(1)
        self.h1Tag.set_priority(2)
        self.h2Tag.set_priority(3)
        self.h3Tag.set_priority(4)
        self.h4Tag.set_priority(5)
        self.h5Tag.set_priority(6)
        self.h6Tag.set_priority(7)
        self.lineTag.set_priority(8)
        self.bTag.set_priority(9)
        self.iTag.set_priority(10)
        self.sTag.set_priority(11)
        self.uTag.set_priority(12)

        self.outlineSelection.connect("changed", self._outlineSelectionChanged)
        self.editorOutlineSelection.connect("changed", self._editorOutlineSelectionChanged)

        self.viewStack = builder.get_object("view_stack")

        self.editorTextBuffer = builder.get_object("editor_text")
        self.editorFlowbox = builder.get_object("editor_flowbox")

        self.editorFlowbox.connect("selected-children-changed", self._editorFlowboxSelectionChanged)
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

    def __updateOutlineItem(self, tree_iter, outlineItem: OutlineItem):
        icon = iconByOutlineItemType(outlineItem)

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

    def __completeOutlineItem(self):
        (tree_iter, outlineItem) = self.outlineCompletion.pop(0)

        if outlineItem.state != OutlineState.COMPLETE:
            outlineItem.load(False)

        self.__updateOutlineItem(tree_iter, outlineItem)

        completedItem = outlineItem
        while completedItem is not None:
            if completedItem in self.editorItems:
                if self.outlineItem:
                    self.loadOutlineData(self.outlineItem)
                break

            completedItem = completedItem.parentItem()

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

        for item in self.project.outline.items:
            self.__appendOutlineItem(item)

    def __updateEditorOutlineItem(self, list_iter, outlineItem: OutlineItem):
        icon = iconByOutlineItemType(outlineItem)

        wordCount = validInt(outlineItem.textCount())
        goal = validInt(outlineItem.goalCount())
        progress = 100 * safeFraction(wordCount, 0, goal)

        self.editorOutlineStore.set_value(list_iter, 0, outlineItem.UID.value)
        self.editorOutlineStore.set_value(list_iter, 1, validString(outlineItem.title))
        self.editorOutlineStore.set_value(list_iter, 2, validString(outlineItem.label))
        self.editorOutlineStore.set_value(list_iter, 3, validString(outlineItem.status))
        self.editorOutlineStore.set_value(list_iter, 4, outlineItem.compile)
        self.editorOutlineStore.set_value(list_iter, 5, wordCount)
        self.editorOutlineStore.set_value(list_iter, 6, goal)
        self.editorOutlineStore.set_value(list_iter, 7, progress)
        self.editorOutlineStore.set_value(list_iter, 8, icon)

    def refreshEditorOutlineStore(self):
        self.editorOutlineSelection.unselect_all()
        self.editorOutlineStore.clear()

        for outlineItem in self.editorItems:
            list_iter = self.editorOutlineStore.append()

            if list_iter is None:
                continue

            self.__updateEditorOutlineItem(list_iter, outlineItem)

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

    def __appendOutlineItemText(self, outlineItem: OutlineItem, level: int = 1):
        end_iter = self.editorTextBuffer.get_end_iter()

        if type(outlineItem) is OutlineFolder:
            if self.editorTextBuffer.get_line_count() > 1:
                self.editorTextBuffer.insert_with_tags_by_name(end_iter, "\n", "none")

            headerTag = "h{0}".format(min(level, 6))
            end_iter = self.editorTextBuffer.get_end_iter()

            self.editorTextBuffer.insert_with_tags_by_name(end_iter, outlineItem.title + "\n", headerTag)

            firstItem = True

            for item in outlineItem:
                if firstItem:
                    firstItem = False
                else:
                    end_iter = self.editorTextBuffer.get_end_iter()
                    self.editorTextBuffer.insert_with_tags_by_name(end_iter, "\n", "none")

                self.__appendOutlineItemText(item, level + 1)

            return True
        elif type(outlineItem) is OutlineText:
            outlineText: OutlineText = outlineItem

            if (outlineText.text is None) or (len(outlineText.text) <= 0):
                return False

            paragraphs = outlineText.text.split("\n")
            firstParagraph = True

            for paragraph in paragraphs:
                if firstParagraph:
                    firstParagraph = False
                else:
                    self.editorTextBuffer.insert_with_tags_by_name(end_iter, "\n", "none")
                    end_iter = self.editorTextBuffer.get_end_iter()

                self.editorTextBuffer.insert_with_tags_by_name(end_iter, paragraph, "p")
                end_iter = self.editorTextBuffer.get_end_iter()

            return True
        else:
            return False

    def loadEditorData(self, outlineItem: OutlineItem | None = None):
        self.editorItems = list()
        self.outlineItem = None

        start_iter, end_iter = self.editorTextBuffer.get_bounds()
        self.editorTextBuffer.delete(start_iter, end_iter)

        if outlineItem is None:
            self.editorItems = self.project.outline.items
        elif type(outlineItem) is OutlineFolder:
            self.editorItems = outlineItem.items

        if outlineItem is None:
            for item in self.editorItems:
                self.__appendOutlineItemText(item)
        else:
            self.__appendOutlineItemText(outlineItem)

        self.editorFlowbox.foreach(self.editorFlowbox.remove)
        if len(self.editorItems) <= 0:
            self.outlineItem = outlineItem
            return

        for item in self.editorItems:
            self.editorFlowbox.insert(GridItem(item).widget, -1)

        self.refreshEditorOutlineStore()
        self.outlineItem = outlineItem

    def _outlineSelectionChanged(self, selection: Gtk.TreeSelection):
        model, tree_iter = selection.get_selected()

        if tree_iter is None:
            self.unloadOutlineData()
            return

        outlineItem = self.project.outline.getItemByID(model[tree_iter][0])

        self.loadOutlineData(outlineItem)

    def _editorOutlineSelectionChanged(self, selection: Gtk.TreeSelection):
        if len(self.editorItems) == 0:
            return

        model, tree_iter = selection.get_selected()

        if tree_iter is None:
            return

        outlineItem = self.project.outline.getItemByID(model[tree_iter][0])

        try:
            index = self.editorItems.index(outlineItem)
        except ValueError:
            self.editorFlowbox.unselect_all()
            return

        for child in self.editorFlowbox.get_children():
            if index == child.get_index():
                self.editorFlowbox.select_child(child)
                break

    def _editorFlowboxSelectionChanged(self, box: Gtk.FlowBox):
        if len(self.editorItems) == 0:
            return

        children = box.get_selected_children()
        child = children[0] if len(children) > 0 else None

        if child is None:
            self.editorOutlineSelection.unselect_all()
            return

        index = child.get_index()
        if (index < 0) or (index >= len(self.editorItems)):
            return

        outlineItem = self.editorItems[index]

        def selectEditorOutlineItem(model: Gtk.TreeModel, path: Gtk.TreePath, _iter: Gtk.TreeIter, outline_id: int):
            if model[_iter][0] != outline_id:
                return False

            if not self.editorOutlineSelection.path_is_selected(path):
                self.editorOutlineSelection.select_path(path)

            return True

        self.editorOutlineStore.foreach(selectEditorOutlineItem, outlineItem.UID.value)

    def __openOutlineItem(self, outlineItem: OutlineItem | None):
        if outlineItem is None:
            self.outlineSelection.unselect_all()
            return

        def selectOutlineItem(model: Gtk.TreeModel, path: Gtk.TreePath, _iter: Gtk.TreeIter, outline_id: int):
            if model[_iter][0] != outline_id:
                return False

            if not self.outlineView.row_expanded(path):
                self.outlineView.expand_to_path(path)

            if not self.outlineSelection.path_is_selected(path):
                self.outlineSelection.select_path(path)

            return True

        self.outlineStore.foreach(selectOutlineItem, outlineItem.UID.value)

    def _editorFlowboxChildActivated(self, box: Gtk.FlowBox, child: Gtk.FlowBoxChild):
        if len(self.editorItems) == 0:
            return

        if child is None:
            self.__openOutlineItem(None)
            return

        index = child.get_index()
        if (index < 0) or (index >= len(self.editorItems)):
            return

        outlineItem = self.editorItems[index]

        self.__openOutlineItem(outlineItem)

    def _upButtonClicked(self, button: Gtk.Button):
        if self.outlineItem is None:
            return

        self.__openOutlineItem(self.outlineItem.parentItem())

    def show(self):
        self.widget.show_all()

    def cutSelection(self):
        if not self.editorTextBuffer.get_has_selection():
            return
        
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        if clipboard is None:
            return
        
        self.editorTextBuffer.cut_clipboard(clipboard, True)

    def copySelection(self):
        if not self.editorTextBuffer.get_has_selection():
            return
        
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        if clipboard is None:
            return
        
        self.editorTextBuffer.copy_clipboard(clipboard)

    def pasteClipboard(self):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        if clipboard is None:
            return
        
        self.editorTextBuffer.paste_clipboard(clipboard, None, True)

    def deleteSelection(self):
        if not self.editorTextBuffer.get_has_selection():
            return
        
        self.editorTextBuffer.delete_selection(True, True)

    def renameItem(self, name: str|None = None):
        model, tree_iter = self.outlineSelection.get_selected()

        if tree_iter is None:
            return

        outlineItem = self.project.outline.getItemByID(model[tree_iter][0])

        if outlineItem is None:
            return

        outlineItem.title = validString(name)

        if tree_iter:
            self.__updateOutlineItem(tree_iter, outlineItem)

        self.loadOutlineData(outlineItem)

    def toggleTagFromSelection(self, tag_name: str):
        if not self.editorTextBuffer.get_has_selection():
            return
        
        tag = self.editorTextBuffer.get_tag_table().lookup(tag_name)

        if tag is None:
            return
        
        start_iter, end_iter = self.editorTextBuffer.get_selection_bounds()

        if start_iter.has_tag(tag):
            self.editorTextBuffer.remove_tag(tag, start_iter, end_iter)
        else:
            self.editorTextBuffer.apply_tag(tag, start_iter, end_iter)
