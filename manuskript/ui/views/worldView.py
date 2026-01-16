#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk

from manuskript.data import World, WorldItem, DropPosition
from manuskript.util import validString, invalidString, validInt, invalidInt

class WorldView:

    def __init__(self, world: World):
        self.world: World = world
        self.worldItem: WorldItem = None

        builder = Gtk.Builder()
        builder.add_from_file("ui/world.glade")

        self.widget = builder.get_object("world_view")
        self.notebook = builder.get_object("world_notebook")

        self.worldTreeView = builder.get_object("world_tree_view")

        targets = Gtk.TargetEntry.new("STRING", Gtk.TargetFlags.SAME_APP, 0)
        self.worldTreeView.enable_model_drag_source(
            Gdk.ModifierType.BUTTON1_MASK,
            [targets],
            Gdk.DragAction.MOVE
        )

        self.worldTreeView.enable_model_drag_dest(
            [targets],
            Gdk.DragAction.MOVE
        )

        self.worldTreeView.connect("drag-data-get", self._worldTreeViewDragDataGet)
        self.worldTreeView.connect("drag-data-received", self._worldTreeViewDragDataReceived)
        self.worldTreeView.connect("drag-drop", self._worldTreeViewDragDrop)

        self.worldStore = builder.get_object("world_store")
        self.refreshWorldStore()

        self.filteredWorldStore = builder.get_object("filtered_world_store")
        self.filterWorldBuffer = builder.get_object("filter_world")

        self.filterWorldBuffer.connect("deleted-text", self._filterWorldDeletedText)
        self.filterWorldBuffer.connect("inserted-text", self._filterWorldInsertedText)

        self.filteredWorldStore.set_visible_func(self._filterWorld)
        self.filteredWorldStore.refilter()

        self.worldSelection = builder.get_object("world_selection")

        self.worldSelection.connect("changed", self._worldSelectionChanged)

        self.addToWorldButton = builder.get_object("add_to_world")
        self.removeFromWorldButton = builder.get_object("remove_from_world")
        self.populateButton = builder.get_object("populate")

        self.addToWorldButton.connect("clicked", self._addToWorldClicked)
        self.removeFromWorldButton.connect("clicked", self._removeFromWorldClicked)
        self.populateButton.connect("clicked", self._populateClicked)

        self.popover: Gtk.Popover = self.createPopulatePopover(self.populateButton)

        self.nameBuffer = builder.get_object("name")
        self.descriptionBuffer = builder.get_object("description")
        self.sourceOfPassionBuffer = builder.get_object("source_of_passion")
        self.sourceOfConflictBuffer = builder.get_object("source_of_conflict")

        self.nameBuffer.connect("deleted-text", self._nameDeletedText)
        self.nameBuffer.connect("inserted-text", self._nameInsertedText)

        self.descriptionBuffer.connect("changed", self._descriptionChanged)
        self.sourceOfPassionBuffer.connect("changed", self._sourceOfPassionChanged)
        self.sourceOfConflictBuffer.connect("changed", self._sourceOfConflictChanged)

        self.unloadWorldData()

    def createPopulatePopover(self, button: Gtk.Button):
        popover = Gtk.Popover.new(button)
        popover.set_position(Gtk.PositionType.BOTTOM)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        popover.add(box)

        for templateName in self.world.fetchTemplateList():
            insertTemplateButton = Gtk.ModelButton(label=templateName)
            insertTemplateButton.connect("clicked", self._insertTemplateClicked, templateName)
            box.pack_start(insertTemplateButton, True, True, 0)

        return popover
        
    def _worldTreeViewDragDataGet(self, treeview: Gtk.TreeView, drag_context: Gdk.DragContext, selection: Gtk.SelectionData, target_id: int, etime: int):
        model, iter_ = treeview.get_selection().get_selected()
        if iter_ is not None:
            path = model.get_path(iter_)
            selection.set_text(str(path.to_string()), -1)

        return True

    def _worldTreeViewDragDataReceived(self, treeview: Gtk.TreeView, drag_context: Gdk.DragContext, x: int, y: int, selection: Gtk.SelectionData, info: int, etime: int):
        treeview.stop_emission("drag-data-received")

        model = treeview.get_model()
        
        store = model.get_model()

        data = selection.get_text()
        dragged_path = Gtk.TreePath.new_from_string(data)
        
        filtered_iter = model.get_iter(dragged_path)
        original_iter = model.convert_iter_to_child_iter(filtered_iter)

        dragged_item_uid = store.get_value(original_iter, 0) 

        drop_info = treeview.get_dest_row_at_pos(x, y)
        
        if drop_info is None:
            parent_iter = None
            position = -1
            target_item_uid = None
        else:
            path, pos = drop_info
            parent_iter = store.get_iter(path)
            position = pos 
            target_item_uid = store.get_value(parent_iter, 0)

        self.world.moveItem(dragged_item_uid, target_item_uid, DropPosition.fromGtkEnum(position))

        self.refreshWorldStore()

        return True
    
    def _worldTreeViewDragDrop(self, treeview: Gtk.TreeView, drag_context: Gdk.DragContext, x: int, y: int, etime: int):
        treeview.stop_emission("drag-drop")
        treeview.drag_get_data(drag_context, drag_context.list_targets()[-1], etime)
        return True

    def _insertTemplateClicked(self, button: Gtk.Button, userdata: str):
        self.world.insertTemplate(userdata)
        self.refreshWorldStore()

    def __appendWorldItem(self, worldItem: WorldItem, parent_iter=None):
        tree_iter = self.worldStore.append(parent_iter)

        if tree_iter is None:
            return

        self.worldStore.set_value(tree_iter, 0, worldItem.UID.value)
        self.worldStore.set_value(tree_iter, 1, validString(worldItem.name))

        for item in worldItem:
            self.__appendWorldItem(item, tree_iter)

    def refreshWorldStore(self):
        self.worldStore.clear()

        for item in self.world.top:
            self.__appendWorldItem(item)

        self.worldTreeView.expand_all()

    def loadWorldData(self, worldItem: WorldItem):
        self.worldItem = None

        self.nameBuffer.set_text(validString(worldItem.name), -1)
        self.descriptionBuffer.set_text(validString(worldItem.description), -1)
        self.sourceOfPassionBuffer.set_text(validString(worldItem.passion), -1)
        self.sourceOfConflictBuffer.set_text(validString(worldItem.conflict), -1)

        self.worldItem = worldItem
        self.notebook.set_sensitive(True)

    def unloadWorldData(self):
        self.worldItem = None
        self.notebook.set_sensitive(False)

        self.nameBuffer.set_text("", -1)
        self.descriptionBuffer.set_text("", -1)
        self.sourceOfPassionBuffer.set_text("", -1)
        self.sourceOfConflictBuffer.set_text("", -1)

    def _worldSelectionChanged(self, selection: Gtk.TreeSelection):
        model, tree_iter = selection.get_selected()

        if tree_iter is None:
            self.unloadWorldData()
            return

        worldItem = self.world.getItemByID(model[tree_iter][0])

        if worldItem is None:
            self.unloadWorldData()
        else:
            self.loadWorldData(worldItem)

    def _addToWorldClicked(self, button: Gtk.Button):
        name = invalidString(self.filterWorldBuffer.get_text())
        worldItem = self.world.addItem(name, self.worldItem)

        if worldItem is None:
            return

        self.refreshWorldStore()

    def _removeFromWorldClicked(self, button: Gtk.Button):
        if self.worldItem is None:
            return

        self.worldItem.remove()
        self.refreshWorldStore()

    def _populateClicked(self, button: Gtk.Button):
        self.popover.show_all()
        self.popover.popup()

    def __matchWorldItemByText(self, worldItem: WorldItem, text: str):
        for item in worldItem:
            if self.__matchWorldItemByText(item, text):
                return True

        name = validString(worldItem.name)
        return text in name.lower()

    def _filterWorld(self, model, iterator, userdata):
        worldItem = self.world.getItemByID(model[iterator][0])

        if worldItem is None:
            return False

        text = validString(self.filterWorldBuffer.get_text())
        return self.__matchWorldItemByText(worldItem, text.lower())

    def __filterWorldChanged(self, buffer: Gtk.EntryBuffer):
        self.filteredWorldStore.refilter()

    def _filterWorldDeletedText(self, buffer: Gtk.EntryBuffer, position: int, n_chars: int):
        self.__filterWorldChanged(buffer)

    def _filterWorldInsertedText(self, buffer: Gtk.EntryBuffer, position: int, chars: str, n_chars: int):
        self.__filterWorldChanged(buffer)

    def __updateWorldItemName(self, model, path, treeiter, userdata):
        id = model[treeiter][0]

        if userdata["world_item_id"] == id:
            model[treeiter][1] = userdata["name"]
            return True
        
        return False

    def __nameChanged(self, buffer: Gtk.EntryBuffer):
        if self.worldItem is None:
            return

        text = buffer.get_text()
        name = invalidString(text)

        self.worldItem.name = name

        world_item_id = self.worldItem.UID.value

        userdata = {
            "world_item_id": world_item_id,
            "name": validString(name)
        }

        self.worldStore.foreach(self.__updateWorldItemName, userdata)

    def _nameDeletedText(self, buffer: Gtk.EntryBuffer, position: int, n_chars: int):
        self.__nameChanged(buffer)

    def _nameInsertedText(self, buffer: Gtk.EntryBuffer, position: int, chars: str, n_chars: int):
        self.__nameChanged(buffer)

    def _descriptionChanged(self, buffer: Gtk.TextBuffer):
        if self.worldItem is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.worldItem.description = invalidString(text)

    def _sourceOfPassionChanged(self, buffer: Gtk.TextBuffer):
        if self.worldItem is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.worldItem.passion = invalidString(text)

    def _sourceOfConflictChanged(self, buffer: Gtk.TextBuffer):
        if self.worldItem is None:
            return

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.worldItem.conflict = invalidString(text)

    def show(self):
        self.widget.show_all()
