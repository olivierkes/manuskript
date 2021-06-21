#!/usr/bin/env python
# --!-- coding: utf8 --!--

import locale

from PyQt5.QtCore import QAbstractItemModel, QMimeData
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QVariant
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QTextEdit, qApp

from manuskript import settings
from lxml import etree as ET

from manuskript.enums import Outline
from manuskript.functions import mainWindow, toInt, wordCount
from manuskript.models import outlineItem

try:
    locale.setlocale(locale.LC_ALL, '')
except:
    # Invalid locale, but not really a big deal because it's used only for
    # number formatting
    pass
import time, os

import logging
LOGGER = logging.getLogger(__name__)

class abstractModel(QAbstractItemModel):
    """
    Abstract model is the base class for all others models we use.

    It's main responsibilities are:

    - Interface with QModelIndex and stuff
    - XML Import / Export
    - Drag'n'drop

    Row => item/abstractModel/etc.
    Col => data sub-element. Col 1 (second counting) is ID for all model types.

    """
    def __init__(self, parent):
        QAbstractItemModel.__init__(self, parent)
        self.nextAvailableID = 1

        # Stores removed item, in order to remove them on disk when saving, depending on the file format.
        self.removed = []
        self._removingRows = False

    def requestNewID(self):
        newID = self.nextAvailableID
        self.nextAvailableID += 1
        return str(newID)

    # Call this if loading an ID from file rather than assigning a new one.
    def updateAvailableIDs(self, addedID):
        if int(addedID) >= self.nextAvailableID:
            self.nextAvailableID = int(addedID) + 1

    def index(self, row, column, parent):

        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def indexFromItem(self, item, column=0):
        if item == self.rootItem:
            return QModelIndex()

        parent = item.parent()
        if not parent:
            parent = self.rootItem

        if len(parent.children()) == 0:
            return None

        #LOGGER.debug("%s: %s", item.title(), [i.title() for i in parent.children()])

        row = parent.children().index(item)
        col = column
        return self.createIndex(row, col, item)

    def ID(self, index):
        if index.isValid():
            item = index.internalPointer()
            return item.ID()

    def findItemsContaining(self, text, columns, caseSensitive=False):
        """
        Returns a list of IDs of all items containing `text`
        in columns `columns` (being a list of int).
        """
        return self.rootItem.findItemsContaining(text, columns, mainWindow(), caseSensitive)

    def getItemByID(self, ID, ignore=None):
        """Returns the item whose ID is `ID`, unless this item matches `ignore`."""

        def search(item):
            if item.ID() == ID:
                if item == ignore:
                    # The item we really want won't be found in the children of this
                    # particular item anymore; stop searching this branch entirely.
                    return None
                return item
            for c in item.children():
                r = search(c)
                if r:
                    return r

        item = search(self.rootItem)
        return item

    def getIndexByID(self, ID, column=0, ignore=None):
        """Returns the index of item whose ID is `ID`. If none, returns QModelIndex().

        If `ignore` is set, it will not return that item if found as valid match for the ID"""

        item = self.getItemByID(ID, ignore=ignore)
        if not item:
            return QModelIndex()
        else:
            return self.indexFromItem(item, column)

    def parent(self, index=QModelIndex()):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        # Check whether the parent is the root, or is otherwise invalid.
        # That is to say: no parent or the parent lacks a parent.
        if (parentItem == self.rootItem) or \
           (parentItem == None) or (parentItem.parent() == None):
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        item = index.internalPointer()
        return item.data(index.column(), role)

    def setData(self, index, value, role=Qt.EditRole):
        item = index.internalPointer()
        if item.data(index.column(), role) != value:

            item.setData(index.column(), value, role)

            # self.dataChanged.emit(index.sibling(index.row(), 0),
            # index.sibling(index.row(), max([i.value for i in Outline])))
            # LOGGER.debug("Model dataChanged emit: %s, %s", index.row(), index.column())
            self.dataChanged.emit(index, index)

            if index.column() == Outline.type:
                # If type changed, then the icon of title changed.
                # Some views might be glad to know it.
                self.dataChanged.emit(index.sibling(index.row(), Outline.title),
                                      index.sibling(index.row(), Outline.title))

        return True

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role in [Qt.DisplayRole, Qt.ToolTipRole]:
            if section == Outline.title:
                return self.tr("Title")
            elif section == Outline.POV:
                return self.tr("POV")
            elif section == Outline.label:
                return self.tr("Label")
            elif section == Outline.status:
                return self.tr("Status")
            elif section == Outline.compile:
                return self.tr("Compile")
            elif section == Outline.wordCount:
                return self.tr("Word count")
            elif section == Outline.goal:
                return self.tr("Goal")
            elif section == Outline.goalPercentage:
                return "%"
            else:
                return [i.name for i in Outline][section]

        elif role == Qt.SizeHintRole:
            if section == Outline.compile:
                return QSize(40, 30)
            elif section == Outline.goalPercentage:
                return QSize(100, 30)
            else:
                return QVariant()
        else:
            return QVariant()

        return True

    def maxLevel(self):
        """Returns the max depth of the model."""
        def depth(item, d=-1):
            d += 1
            r = d
            for c in item.children():
                r = max(r, depth(c, d))
            return r

        d = depth(self.rootItem)
        return d

    #################### DRAG AND DROP ########################
    # http://doc.qt.io/qt-5/model-view-programming.html#using-drag-and-drop-with-item-views

    def flags(self, index):
        # FIXME when dragging folders, sometimes flags is not called

        flags = QAbstractItemModel.flags(self, index) | Qt.ItemIsEditable

        if index.isValid() and index.internalPointer().isFolder() and index.column() == 0:
            flags |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

        elif index.isValid() and index.column() == 0:
            flags |= Qt.ItemIsDragEnabled

        elif not index.isValid():
            flags |= Qt.ItemIsDropEnabled

        if index.isValid() and index.column() == Outline.compile:
            flags |= Qt.ItemIsUserCheckable

        if index.column() in [i.value for i in [Outline.wordCount, Outline.goalPercentage]]:
            flags &= ~ Qt.ItemIsEditable

        return flags

    def mimeTypes(self):
        return ["application/xml"]

    def mimeData(self, indexes):
        mimeData = QMimeData()
        encodedData = ""

        root = ET.Element("outlineItems")

        for index in indexes:
            if index.isValid() and index.column() == 0:
                item = ET.XML(index.internalPointer().toXML())
                root.append(item)

        encodedData = ET.tostring(root)

        mimeData.setData("application/xml", encodedData)
        return mimeData

    def supportedDropActions(self):

        return Qt.CopyAction | Qt.MoveAction

    def canDropMimeData(self, data, action, row, column, parent):
        """Ensures that we are not dropping an item into itself."""

        if not data.hasFormat("application/xml"):
            return False

        if column > 0:
            return False

        # # Gets encoded mime data to retrieve the item
        items = self.decodeMimeData(data)
        if items == None:
            return False

        # We check if parent is not a child of one of the items
        if self.isParentAChildOfItems(parent, items):
            return False

        return True

    def isParentAChildOfItems(self, parent, items):
        """
        Takes a parent index, and a list of outlineItems items. Check whether
        parent is in a child of one of the items.
        Return True in that case, False if not.
        """

        # Get the parent item
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        for item in items:
            # Get parentItem's parents IDs in a list
            path = parentItem.pathID()  # path to item in the form [(ID, title), ...]
            path = [ID for ID, title in path]
            # Is item in the path? It would mean that it tries to get dropped
            # as a children of himself.
            if item.ID() in path:
                return True

        return False

    def decodeMimeData(self, data):
        if not data.hasFormat("application/xml"):
            return None
        encodedData = bytes(data.data("application/xml")).decode()
        root = ET.XML(encodedData)
        if root == None:
            return None

        if root.tag != "outlineItems":
            return None

        items = []
        for child in root:
            if child.tag == "outlineItem":
                item = outlineItem(xml=ET.tostring(child))
                items.append(item)

        # We remove every item whose parent is also in items, otherwise it gets
        # duplicated. (https://github.com/olivierkes/manuskript/issues/169)
        # For example if selecting:
        #   - Parent
        #      - Child
        # And dragging them, items encoded in mime data are: [Parent, Child],
        # but Child is already contained in Parent, so if we do nothing we end
        # up with:
        #   - Parent
        #     - Child
        #   - Child

        newItems = items[:]
        IDs = [i.ID() for i in items]

        def checkIfChildIsPresent(item):
            # Recursively check every children of item, to see if any is in
            # the list of items to copy. If so, we remove it from the list.
            for c in item.children():
                # We check if children is in the selection
                # and if it hasn't been removed yet
                if c.ID() in IDs and c.ID() in [i.ID() for i in newItems]:
                    # Remove item by ID
                    newItems.remove([i for i in newItems if i.ID() == c.ID()][0])
                checkIfChildIsPresent(c)

        for i in items:
            checkIfChildIsPresent(i)

        items = newItems

        return items

    def dropMimeData(self, data, action, row, column, parent):

        if action == Qt.IgnoreAction:
            return True  # What is that?

        if action == Qt.MoveAction:
            # Strangely, on some cases, we get a call to dropMimeData though
            # self.canDropMimeData returned False.
            # See https://github.com/olivierkes/manuskript/issues/169 to reproduce.
            # So we double check for safety.
            if not self.canDropMimeData(data, action, row, column, parent):
                return False

        items = self.decodeMimeData(data)

        if items == None:
            return False

        if column > 0:
            column = 0

        if row != -1:
            beginRow = row
        elif parent.isValid():
            beginRow = self.rowCount(parent) + 1
        else:
            beginRow = self.rowCount() + 1

        if action == Qt.CopyAction:
            # Behavior if parent is a text item
            # For example, we select a text and do: CTRL+C CTRL+V
            if parent.isValid() and not parent.internalPointer().isFolder():
                # We insert copy in parent folder, just below
                beginRow = parent.row() + 1
                parent = parent.parent()

            if parent.isValid() and parent.internalPointer().isFolder():
                while self.isParentAChildOfItems(parent, items):
                    # We are copying a folder on itself. Assume duplicates.
                    # Copy not in, but next to
                    beginRow = parent.row() + 1
                    parent = parent.parent()

        if not items:
            return False

        # In case of copy actions, items might be duplicates, so we need new IDs.
        # But they might not be, if we cut, then paste. Paste is a Copy Action.
        # The first paste would not need new IDs. But subsequent ones will.

        # Recursively change the existing IDs to new, unique values. No need to strip out the old
        # even if they are not duplicated in pasting. There is no practical need for ID conservation.

        if action == Qt.CopyAction:
            IDs = self.rootItem.listAllIDs()

            for item in items:
                if item.ID() in IDs:
                    item.getUniqueID(recursive=True)

        r = self.insertItems(items, beginRow, parent)

        return r

    ################# ADDING AND REMOVING #################

    def insertItem(self, item, row, parent=QModelIndex()):
        return self.insertItems([item], row, parent)

    def insertItems(self, items, row, parent=QModelIndex()):
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        if parent.isValid() and parent.column() != 0:
            parent = parentItem.index()

        # Insert only if parent is folder
        if parentItem.isFolder():
            self.beginInsertRows(parent, row, row + len(items) - 1) # Create space.

            for i in items:
                parentItem.insertChild(row + items.index(i), i)

            self.endInsertRows()

            return True

        else:
            return False

    def appendItem(self, item, parent=QModelIndex()):
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        if parent.isValid() and parent.column() != 0:
            parent = parentItem.index()

        # If parent is folder, write into
        if parentItem.isFolder():
            self.insertItem(item, self.rowCount(parent), parent)

        # If parent is not folder, write next to
        else:
            self.insertItem(item, parent.row() + 1, parent.parent())

    def removeIndex(self, index):
        item = index.internalPointer()
        self.removeRow(item.row(), index.parent())

    def removeIndexes(self, indexes):
        levels = {}
        for i in indexes:
            item = i.internalPointer()
            level = item.level()
            if not level in levels:
                levels[level] = []
            levels[level].append([i.row(), i])

        # Sort by level then by row
        for l in reversed(sorted(levels.keys())):
            rows = levels[l]

            rows = list(reversed(sorted(rows, key=lambda x: x[0])))
            for r in rows:
                self.removeIndex(r[1])

    def removeRow(self, row, parent=QModelIndex()):
        return self.removeRows(row, 1, parent)

    def removeRows(self, row, count, parent=QModelIndex()):
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        self._removingRows = True
        # Views that are updating can easily know
        # if this is due to row removal.
        self.beginRemoveRows(parent, row, row + count - 1)
        for i in range(count):
            item = parentItem.removeChild(row)
            self.removed.append(item)

        self._removingRows = False
        self.endRemoveRows()
        return True

        # def insertRow(self, row, item, parent=QModelIndex()):
        # self.beginInsertRows(parent, row, row)

        # if not parent.isValid():
        # parentItem = self.rootItem
        # else:
        # parentItem = parent.internalPointer()

        # parentItem.insertChild(row, item)

        # self.endInsertRows()

    ################# XML / saving / loading #################

    def saveToXML(self, xml=None):
        "If xml (filename) is given, saves the items to xml. Otherwise returns as string."
        root = ET.XML(self.rootItem.toXML())
        if xml:
            ET.ElementTree(root).write(xml, encoding="UTF-8", xml_declaration=True, pretty_print=True)
        else:
            return ET.tostring(root, encoding="UTF-8", xml_declaration=True, pretty_print=True)

    def loadFromXML(self, xml, fromString=False):
        "Load from xml. Assume that xml is a filename. If fromString=True, xml is the content."
        if not fromString:
            root = ET.parse(xml)
        else:
            root = ET.fromstring(xml)

        self.rootItem = outlineItem(model=self, xml=ET.tostring(root), ID="0")
        self.rootItem.checkIDs()

    def indexFromPath(self, path):
        path = path.split(",")
        item = self.rootItem
        for p in path:
            if p != "" and int(p) < item.childCount():
                item = item.child(int(p))
        return self.indexFromItem(item)
