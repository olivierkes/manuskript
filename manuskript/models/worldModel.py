#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import QModelIndex, QSize
from PyQt5.QtCore import Qt, QMimeData, QByteArray
from PyQt5.QtGui import QStandardItem, QBrush, QFontMetrics
from PyQt5.QtGui import QStandardItemModel, QColor
from PyQt5.QtWidgets import QMenu, QAction, qApp

from manuskript.enums import World, Model
from manuskript.functions import mainWindow
from manuskript.ui import style as S
from manuskript.models.searchableModel import searchableModel
from manuskript.models.searchableItem import searchableItem
from manuskript.searchLabels import WorldSearchLabels


class worldModel(QStandardItemModel, searchableModel):
    def __init__(self, parent):
        QStandardItemModel.__init__(self, 0, len(World), parent)
        self.mw = mainWindow()

    ###############################################################################
    # SELECTION
    ###############################################################################

    def selectedItem(self):
        """Returns the item selected in mw.treeWorld. invisibleRootItem if None."""
        index = self.selectedIndex()
        item = self.itemFromIndex(index)
        if item:
            return item
        else:
            return self.invisibleRootItem()

    def selectedIndex(self):
        """Returns the selected index in the treeView."""
        if self.mw.treeWorld.selectedIndexes():
            return self.mw.treeWorld.currentIndex()
        else:
            return QModelIndex()

    def selectedIndexes(self):
        return self.mw.treeWorld.selectedIndexes()

    ###############################################################################
    # GETTERS
    ###############################################################################

    def ID(self, index):
        """Returns the ID of the given index."""
        index = index.sibling(index.row(), World.ID)
        return self.data(index)

    def name(self, index):
        """Returns the name of the given index."""
        index = index.sibling(index.row(), World.name)
        return self.data(index)

    def description(self, index):
        index = index.sibling(index.row(), World.description)
        return self.data(index)

    def conflict(self, index):
        index = index.sibling(index.row(), World.conflict)
        return self.data(index)

    def passion(self, index):
        index = index.sibling(index.row(), World.passion)
        return self.data(index)

    def itemID(self, item):
        """Returns the ID of the given item."""
        index = self.indexFromItem(item)
        return self.ID(index)

    def children(self, item):
        """Returns a list of all item's children."""
        c = []
        for i in range(item.rowCount()):
            c.append(item.child(i))
        return c

    def listAll(self):
        """Returns a list of tuple ``(name, ID, path)`` for all items."""
        lst = []

        def readAll(item):
            name = item.text()
            ID = self.itemID(item)
            path = self.path(item)
            if name and ID:
                lst.append((name, ID, path))
            for c in self.children(item):
                readAll(c)

        readAll(self.invisibleRootItem())

        return lst

    def indexByID(self, ID):
        """Returns the index of item whose ID is ID."""
        return self.indexFromItem(self.itemByID(ID))

    def itemByID(self, ID):
        """Returns the item whose ID is ID."""

        def browse(item):
            if self.itemID(item) == ID:
                return item
            for c in self.children(item):
                r = browse(c)
                if r:
                    return r

        r = browse(self.invisibleRootItem())
        return r if r else None

    def path(self, item):
        """Returns the path to the item in the form of 'ancestor > ... > grand-parent > parent'."""
        path = []
        while item.parent():
            item = item.parent()
            path.append(item.text())
        path = " > ".join(path)
        return path

    ###############################################################################
    # ADDING AND REMOVE
    ###############################################################################

    def addItem(self, title=None, parent=None):
        """Adds an item, and returns it."""
        if not parent:
            parent = self.selectedItem()
        if not title:
            title = self.tr("New item")
        name = QStandardItem(title)
        _id = QStandardItem(self.getUniqueID())
        row = [name, _id] + [QStandardItem() for i in range(2, len(World))]
        parent.appendRow(row)

        self.mw.treeWorld.setExpanded(self.selectedIndex(), True)
        self.mw.treeWorld.setCurrentIndex(self.indexFromItem(name))
        return name

    def getUniqueID(self):
        """Returns an unused ID"""

        parentItem = self.invisibleRootItem()
        vals = []

        def collectIDs(item):
            vals.append(int(self.itemID(item)))
            for c in self.children(item):
                collectIDs(c)

        for c in self.children(parentItem):
            collectIDs(c)

        k = 0
        while k in vals:
            k += 1
        return str(k)

    def removeItem(self):
        while self.selectedIndexes():
            index = self.selectedIndexes()[0]
            self.removeRows(index.row(), 1, index.parent())

    ###############################################################################
    # DRAG & DROP
    ###############################################################################

    """Mime type for worldModel"""
    MIME_TYPE = "application/x.manuskript.worldmodel"

    def mimeTypes(self):
        """Returns available MIME types

        Returns only worldModel MIME type to allow only internal drag & drop"""
        return [self.MIME_TYPE]

    def mimeData(self, indexes):
        """Returns dragged data as MIME data"""
        mime_data = QMimeData()
        """set MIME type"""
        mime_data.setData(self.MIME_TYPE, QByteArray())

        """row index is just a pair of item parent and row number"""
        row_indexes = []
        for index in indexes:
            item = self.itemFromIndex(index)
            parent = item.parent()
            if parent == None:
                parent = self.invisibleRootItem()
            row_indexes.append((parent, item.row()))

        def copyRowWithChildren(row_index):
            """copy row and its children except for those that are in
            row_indexes to avoid duplicates"""
            parent, row_i = row_index

            row = []
            for column_i in range(parent.columnCount()):
                original = parent.child(row_i, column_i)
                copy = original.clone()
                for child_row_i in range(original.rowCount()):
                    child_row_index = (original, child_row_i)
                    if child_row_index not in row_indexes:
                        child_row = copyRowWithChildren(child_row_index)
                        copy.appendRow(child_row)
                row.append(copy)

            return row

        rows = []
        for i in row_indexes:
            """copy not move, because these rows will be deleted automatically
            after dropMimeData"""
            rows.append(copyRowWithChildren(i))
        """mime_data.rows available only in the application"""
        mime_data.rows = rows
        return mime_data

    def dropMimeData(self, mime_data, action, row_i, column_i, parent):
        """insert MIME data"""
        parent_item = self.itemFromIndex(parent)
        if not parent_item:
            parent_item = self.invisibleRootItem()

        """if place for drop is not specified row_i equals -1"""
        if row_i == -1:
            for row in mime_data.rows:
                parent_item.appendRow(row)
        else:
            """reverse list of rows, because QStandardItem::insertRow inserts
            before the index"""
            for row in reversed(mime_data.rows):
                parent_item.insertRow(row_i, row)

        return True

        ###############################################################################
        # TEMPLATES
        ###############################################################################

    def dataSets(self):
        """Returns sets of empty data that can guide the writer for world building."""
        dataset = {
            self.tr("Fantasy world building"): [
                (self.tr("Physical"), [
                    self.tr("Climate"),
                    self.tr("Topography"),
                    self.tr("Astronomy"),
                    self.tr("Natural resources"),
                    self.tr("Wild life"),
                    self.tr("Flora"),
                    self.tr("History"),
                    self.tr("Races"),
                    self.tr("Diseases"),
                ]),
                (self.tr("Cultural"), [
                    self.tr("Customs"),
                    self.tr("Food"),
                    self.tr("Languages"),
                    self.tr("Education"),
                    self.tr("Dresses"),
                    self.tr("Science"),
                    self.tr("Calendar"),
                    self.tr("Bodily language"),
                    self.tr("Ethics"),
                    self.tr("Religion"),
                    self.tr("Government"),
                    self.tr("Politics"),
                    self.tr("Gender roles"),
                    self.tr("Music and arts"),
                    self.tr("Architecture"),
                    self.tr("Military"),
                    self.tr("Technology"),
                    self.tr("Courtship"),
                    self.tr("Demography"),
                    self.tr("Transportation"),
                    self.tr("Medicine"),
                ]),
                (self.tr("Magic system"), [
                    self.tr("Rules"),
                    self.tr("Organization"),
                    self.tr("Magical objects"),
                    self.tr("Magical places"),
                    self.tr("Magical races"),
                ]),
                self.tr("Important places"),
                self.tr("Important objects"),
            ]
        }
        return dataset

    def emptyDataMenu(self):
        """Returns a menu with the empty data sets."""
        self.menu = QMenu("menu")
        for name in self.dataSets():
            a = QAction(name, self.menu)
            a.triggered.connect(self.setEmptyData)
            self.menu.addAction(a)
        return self.menu

    def setEmptyData(self):
        """Called from the menu generated with ``emptyDataMenu``."""
        act = self.sender()
        data = self.dataSets()[act.text()]

        def addItems(data, parent):
            for d in data:
                if len(d) == 1 or type(d) == str:
                    self.addItem(d, parent)
                else:
                    i = self.addItem(d[0], parent)
                    addItems(d[1], i)

        addItems(data, self.invisibleRootItem())
        self.mw.treeWorld.expandAll()

    ###############################################################################
    # APPEARANCE
    ###############################################################################

    def data(self, index, role=Qt.EditRole):
        level = 0
        i = index
        while i.parent() != QModelIndex():
            i = i.parent()
            level += 1

        if role == Qt.BackgroundRole:
            if level == 0:
                return QBrush(QColor(S.highlightLight))

        if role == Qt.TextAlignmentRole:
            if level == 0:
                return Qt.AlignCenter

        if role == Qt.FontRole:
            if level in [0, 1]:
                f = qApp.font()
                f.setBold(True)
                return f

        if role == Qt.ForegroundRole:
            if level == 0:
                return QBrush(QColor(S.highlightedTextDark))

        if role == Qt.SizeHintRole:
            fm = QFontMetrics(qApp.font())
            h = fm.height()
            if level == 0:
                return QSize(0, h + 12)
            elif level == 1:
                return QSize(0, h + 6)

        return QStandardItemModel.data(self, index, role)

    #######################################################################
    # Search
    #######################################################################
    def searchableItems(self):
        def readAll(item):
            items = [WorldItemSearchWrapper(item, self.itemID(item), self.indexFromItem(item), self.data)]

            for c in self.children(item):
                items += readAll(c)

            return items

        return readAll(self.invisibleRootItem())

class WorldItemSearchWrapper(searchableItem):
    def __init__(self, item, itemID, itemIndex, getColumnData):
        super().__init__(WorldSearchLabels)
        self.item = item
        self.itemID = itemID
        self.itemIndex = itemIndex
        self.getColumnData = getColumnData

    def searchModel(self):
        return Model.World

    def searchID(self):
        return self.itemID

    def searchTitle(self, column):
        return self.item.text()

    def searchPath(self, column):

        def _path(item):
            path = []

            if item.parent():
                path += _path(item.parent())
            path.append(item.text())

            return path

        return [self.translate("World")] + _path(self.item) + [self.translate(self.searchColumnLabel(column))]

    def searchData(self, column):
        return self.getColumnData(self.itemIndex.sibling(self.itemIndex.row(), column))

