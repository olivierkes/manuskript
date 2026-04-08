#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import GLib, Gtk, Gdk

from manuskript.ui.views.abstractView import AbstractView

from manuskript.data import Project, OutlineFolder, OutlineText, OutlineItem, OutlineState, Goal
from manuskript.ui.editor import GridItem
from manuskript.ui.util import pixbufFromColor, iconByOutlineItemType
from manuskript.util import validString, validInt, safeFraction
from manuskript.overlay.overlayManager import OverlayManager
from manuskript.overlay.waitingOverlay import WaitingOverlay


class EditorView(AbstractView):
    SCROLL_MARGIN: int = 20
    SCROLL_RATIO: float = 0.9

    def __init__(self, project: Project):
        AbstractView.__init__(self)

        self.project = project
        self.outlineItem = None
        self.outlineCompletion = []
        self.idleCompletion = 0
        self.editorItems = list()
        self.forceReload = False
        self.allEditors: list[Gtk.TextView] = []

        builder = Gtk.Builder()
        builder.add_from_file("ui/editor.glade")

        self.widget = builder.get_object("editor_view")

        self.labelStore: Gtk.ListStore = builder.get_object("label_store")
        self.refreshLabelStore()

        self.statusStore: Gtk.ListStore = builder.get_object("status_store")
        self.refreshStatusStore()

        self.outlineStore: Gtk.TreeStore = builder.get_object("outline_store")
        self.refreshOutlineStore()

        self.editorOutlineStore: Gtk.ListStore = builder.get_object("editor_outline_store")

        self.outlineView: Gtk.TreeView = builder.get_object("outline_view")
        self.editorOutlineView: Gtk.TreeView = builder.get_object("editor_outline_view")

        self.outlineSelection: Gtk.TreeSelection = builder.get_object("outline_selection")
        self.editorOutlineSelection: Gtk.TreeSelection = builder.get_object("editor_outline_selection")

        self.overlay: Gtk.Overlay = builder.get_object("editor_overlay")
        self.overlayManager = OverlayManager(self.overlay)
        self.waitOverlay = WaitingOverlay()
        self.overlayManager.addLayer(self.waitOverlay.getWidget())

        self.h1Tag: Gtk.TextTag = builder.get_object("h1_tag")
        self.h2Tag: Gtk.TextTag = builder.get_object("h2_tag")
        self.h3Tag: Gtk.TextTag = builder.get_object("h3_tag")
        self.h4Tag: Gtk.TextTag = builder.get_object("h4_tag")
        self.h5Tag: Gtk.TextTag = builder.get_object("h5_tag")
        self.h6Tag: Gtk.TextTag = builder.get_object("h6_tag")
        self.bTag: Gtk.TextTag = builder.get_object("b_tag")
        self.iTag: Gtk.TextTag = builder.get_object("i_tag")
        self.sTag: Gtk.TextTag = builder.get_object("s_tag")
        self.uTag: Gtk.TextTag = builder.get_object("u_tag")
        self.noneTag: Gtk.TextTag = builder.get_object("none_tag")
        self.pTag: Gtk.TextTag = builder.get_object("p_tag")
        self.lineTag: Gtk.TextTag = builder.get_object("line_tag")

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

        self.viewStack: Gtk.Stack = builder.get_object("view_stack")

        self.upButtons: list[Gtk.Button] = [
            builder.get_object("up"),
            builder.get_object("up_")
        ]

        self.counterLabel: Gtk.Label = builder.get_object("counter")
        self.counterProgressBar: Gtk.ProgressBar = builder.get_object("counter_progress")

        self.editorTextView: Gtk.TextView = builder.get_object("editor_text_view")

        self.editorTagTable: Gtk.TextTagTable = builder.get_object("editor_tag_table")
        self.editTextBox: Gtk.Box = builder.get_object("editor_text_box")
        self.editorScrollWindow: Gtk.ScrolledWindow = builder.get_object("editor_text_scroll_window")
        self.editorFlowbox: Gtk.FlowBox = builder.get_object("editor_flowbox")

        self.editorOutlineSelection.connect("changed", self._editorOutlineSelectionChanged)
        self.outlineSelection.connect("changed", self._outlineSelectionChanged)
        self.outlineView.connect("button-press-event", self._outlineViewButtonPressed)

        self.editorFlowbox.connect("selected-children-changed", self._editorFlowboxSelectionChanged)
        self.editorFlowbox.connect("child-activated", self._editorFlowboxChildActivated)

        for button in self.upButtons:
            button.connect("clicked", self._upButtonClicked)

        self.unloadOutlineData()

    def activate(self):
        AbstractView.activate(self)

        if self.forceReload:
            self.reloadOutlineData()

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
        if len(self.outlineCompletion) == 0:
            self.loadOutlineData(self.outlineItem)
            self.overlayManager.hideLayers()

            return False

        (tree_iter, outlineItem) = self.outlineCompletion.pop(0)

        if outlineItem.state != OutlineState.COMPLETE:
            outlineItem.load(False)

        self.__updateOutlineItem(tree_iter, outlineItem)

        completedItem = outlineItem
        while completedItem is not None:
            if completedItem in self.editorItems:
                if self.outlineItem:
                    self.reloadOutlineData()
                break

            completedItem = completedItem.parentItem()

        return True

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

    def reloadOutlineData(self):
        if self.active:
            self.loadOutlineData(self.outlineItem)
        else:
            self.forceReload = True

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
        self.forceReload = False

    def unloadOutlineData(self):
        self.outlineItem = None
        self.loadEditorData(None)

        goalKind = self.project.outline.goalKind()
        textCount = self.project.outline.textCount(goalKind)
        goalCount = self.project.outline.goalCount()

        self.counterLabel.set_text("{0} {1}".format(textCount, goalKind.name.lower()))
        self.counterProgressBar.set_text("{0} / {1} {2}".format(textCount, goalCount, goalKind.name.lower()))
        self.counterProgressBar.set_fraction(safeFraction(textCount, 0, goalCount))

        self.forceReload = False

    def __appendOutlineItemText(self, outlineItem: OutlineItem, level: int = 1) -> bool:
        buffer = Gtk.TextBuffer.new(self.editorTagTable)
        textView = Gtk.TextView.new_with_buffer(buffer)
        textView.set_wrap_mode(Gtk.WrapMode.WORD)
        textView.set_left_margin(5)
        textView.set_right_margin(5)
        textView.set_hexpand(False)
        textView.set_vexpand(False)
        textView.set_vscroll_policy(policy=Gtk.ScrollablePolicy.MINIMUM)
        self.allEditors.append(textView)

        self.editTextBox.pack_start(textView, False, False, 0)

        textView.show()

        if type(outlineItem) is OutlineFolder:
            headerTag = "h{0}".format(min(level, 6))

            buffer.insert_with_tags_by_name(buffer.get_start_iter(), outlineItem.title, headerTag)

            textView.set_editable(False)
            for item in outlineItem:
                self.__appendOutlineItemText(item, level + 1)
        else:
            buffer.set_text(outlineItem.text)
            if level==1:
                self.editorTextView.set_buffer(buffer)

        textView.set_size_request(-1, -1)
        textView.connect("key-press-event", self._editorTextViewKeyPressed)
        buffer.connect("mark-set", self._bufferMarkSet, textView)

        return True

    def _bufferMarkSet(self, buffer: Gtk.TextBuffer, iter: Gtk.TextIter, mark: Gtk.TextMark, textView: Gtk.TextView):
        if mark.get_name() != "insert":
            return

        vAdjustment = self.editorScrollWindow.get_vadjustment()
        rect: Gdk.Rectangle = textView.get_iter_location(iter)
        rect = textView.buffer_to_window_coords(Gtk.TextWindowType.WIDGET, rect.x, rect.y)

        cursorY = rect[1]
        translate = textView.translate_coordinates(self.editorScrollWindow.get_child().get_child(), 0, cursorY)
        if not translate:
            return

        _, yInContainer = translate
        visibleTop = vAdjustment.get_value()
        visibleBottom = visibleTop + vAdjustment.get_page_size()

        if yInContainer < visibleTop + self.SCROLL_MARGIN:
            vAdjustment.set_value(max(0, yInContainer - self.SCROLL_MARGIN))
        elif yInContainer > visibleBottom - self.SCROLL_MARGIN:
            vAdjustment.set_value(yInContainer - vAdjustment.get_page_size() + self.SCROLL_MARGIN)

    def _editorTextViewKeyPressed(self, view: Gtk.TextView, event: Gdk.Event):
        keyval = event.keyval
        buffer = view.get_buffer()
        insertMark = buffer.get_insert()
        currentIter = buffer.get_iter_at_mark(insertMark)
        currentLocation = view.get_iter_location(currentIter)
        originalXPosition = currentLocation.x

        def focus_previous_editor_at_x(current_view, goToEnd: bool):
            index = self.allEditors.index(current_view)
            if index > 0:
                previous_view = self.allEditors[index - 1]
                previous_view.grab_focus()
                prev_buffer = previous_view.get_buffer()
                bottom_iter = prev_buffer.get_end_iter()
                if not goToEnd:
                    _, bottom_iter = previous_view.get_iter_at_location(originalXPosition, previous_view.get_iter_location(bottom_iter).y)
                prev_buffer.place_cursor(bottom_iter)
                return True

            return False

        def focus_next_editor_at_x(current_view, goToStart: bool):
            index = self.allEditors.index(current_view)
            if index < len(self.allEditors) - 1:
                next_view = self.allEditors[index + 1]
                next_view.grab_focus()
                next_buffer = next_view.get_buffer()
                start_iter = next_buffer.get_start_iter()
                if not goToStart:
                    _, start_iter = next_view.get_iter_at_location(originalXPosition, next_view.get_iter_location(start_iter).y)
                next_buffer.place_cursor(start_iter)
                return True
            return False

        def pageScroll():
            vadj = self.editorScrollWindow.get_vadjustment()
            remainingDistance = vadj.get_page_size() * self.SCROLL_RATIO

            currentView = view
            currentIterLocal = currentIter
            index = self.allEditors.index(currentView)

            while True:
                rect = currentView.get_iter_location(currentIterLocal)
                visibleRect = currentView.get_visible_rect()
                viewHeight = visibleRect.height

                if keyval == Gdk.KEY_Page_Down:
                    remainingInView = viewHeight - rect.y
                    if remainingDistance <= remainingInView:
                        _, targetIter = currentView.get_iter_at_location(originalXPosition, rect.y + remainingDistance)
                        currentView.grab_focus()
                        currentView.get_buffer().place_cursor(targetIter)
                        return True

                    remainingDistance -= remainingInView
                    index += 1

                    if index >= len(self.allEditors):
                        lastView = self.allEditors[-1]
                        lastBuffer = lastView.get_buffer()
                        lastView.grab_focus()
                        lastBuffer.place_cursor(lastBuffer.get_end_iter())
                        return True

                    currentView = self.allEditors[index]
                    currentIterLocal = currentView.get_buffer().get_start_iter()
                else:
                    distanceFromTop = rect.y

                    if remainingDistance <= distanceFromTop:
                        _, targetIter = currentView.get_iter_at_location(originalXPosition, rect.y - remainingDistance)
                        currentView.grab_focus()
                        currentView.get_buffer().place_cursor(targetIter)
                        return True

                    remainingDistance -= distanceFromTop
                    index -= 1

                    if index < 0:
                        firstView = self.allEditors[0]
                        firstBuffer = firstView.get_buffer()
                        firstView.grab_focus()
                        firstBuffer.place_cursor(firstBuffer.get_start_iter())
                        return True

                    currentView = self.allEditors[index]
                    currentIterLocal = currentView.get_buffer().get_end_iter()

        if keyval == Gdk.KEY_Left:
            if currentIter.is_start():
                return focus_previous_editor_at_x(view, True)

        elif keyval == Gdk.KEY_Right:
            if currentIter.is_end():
                return focus_next_editor_at_x(view, True)

        elif keyval == Gdk.KEY_Up:
            iter_location = view.get_iter_location(currentIter)
            _, top_iter = view.get_iter_at_location(iter_location.x, 0)
            top_location = view.get_iter_location(top_iter)

            if top_location.y == iter_location.y:
                return focus_previous_editor_at_x(view, False)

        elif keyval == Gdk.KEY_Down:
            visible_rect = view.get_visible_rect()
            iter_location = view.get_iter_location(currentIter)
            _, bottom_iter = view.get_iter_at_location(iter_location.x, visible_rect.height)
            bottom_location = view.get_iter_location(bottom_iter)

            if bottom_location.y == iter_location.y:
                return focus_next_editor_at_x(view, False)

        elif keyval == Gdk.KEY_Page_Down or keyval == Gdk.KEY_Page_Up:
            return pageScroll()

        return False

    def loadEditorData(self, outlineItem: OutlineItem | None = None):
        self.editorItems = list()
        self.outlineItem = None

        children = self.editTextBox.get_children()
        for i in reversed(range(len(children))):
            self.editTextBox.remove(children[i])

        self.allEditors = []

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

    def _outlineViewButtonPressed(self, treeview: Gtk.TreeView, event: Gdk.Event):
        if event.button == 1:
            x = int(event.x)
            y = int(event.y)

            path_info = treeview.get_path_at_pos(x, y)
            selection = treeview.get_selection()

            if path_info is None:
                selection.unselect_all()
                self.viewStack.set_visible_child_name("page_stack")
            else:
                selection.select_path(path_info[0])
