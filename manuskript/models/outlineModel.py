#!/usr/bin/env python
# --!-- coding: utf8 --!--

from qt import *
from enums import *
from enum import Enum
from lxml import etree as ET
from functions import *
import settings
import locale

locale.setlocale(locale.LC_ALL, '')
import time


class outlineModel(QAbstractItemModel):
    def __init__(self, parent):
        QAbstractItemModel.__init__(self, parent)

        self.rootItem = outlineItem(self, title="root", ID="0")

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

        # print(item.title(), [i.title() for i in parent.children()])

        row = parent.children().index(item)
        col = column
        return self.createIndex(row, col, item)

    def ID(self, index):
        if index.isValid():
            item = index.internalPointer()
            return item.ID()

    def findItemsByPOV(self, POV):
        "Returns a list of IDs of all items whose POV is ``POV``."
        return self.rootItem.findItemsByPOV(POV)

    def findItemsContaining(self, text, columns, caseSensitive=False):
        """Returns a list of IDs of all items containing ``text``
        in columns ``columns`` (being a list of int)."""
        return self.rootItem.findItemsContaining(text, columns, mainWindow(), caseSensitive)

    def getIndexByID(self, ID):
        "Returns the index of item whose ID is ``ID``. If none, returns QModelIndex()."

        def search(item):
            if item.ID() == ID:
                return item
            for c in item.children():
                r = search(c)
                if r:
                    return r

        item = search(self.rootItem)
        if not item:
            return QModelIndex()
        else:
            return self.indexFromItem(item)

    def parent(self, index=QModelIndex()):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        # print(childItem.title())
        parentItem = childItem.parent()
        # try:
        #     parentItem = childItem.parent()
        # except AttributeError:
        #     import traceback, sys
        #     print(traceback.print_exc())
        #     print(sys.exc_info()[0])
        #     return QModelIndex()

        if parentItem == self.rootItem:
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
            # print("Model emit", index.row(), index.column())
            self.dataChanged.emit(index, index)

            if index.column() == Outline.type.value:
                # If type changed, then the icon of title changed.
                # Some views might be glad to know it.
                self.dataChanged.emit(index.sibling(index.row(), Outline.title.value),
                                      index.sibling(index.row(), Outline.title.value))

        return True

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role in [Qt.DisplayRole, Qt.ToolTipRole]:
            if section == Outline.title.value:
                return self.tr("Title")
            elif section == Outline.POV.value:
                return self.tr("POV")
            elif section == Outline.label.value:
                return self.tr("Label")
            elif section == Outline.status.value:
                return self.tr("Status")
            elif section == Outline.compile.value:
                return self.tr("Compile")
            elif section == Outline.wordCount.value:
                return self.tr("Word count")
            elif section == Outline.goal.value:
                return self.tr("Goal")
            elif section == Outline.goalPercentage.value:
                return "%"
            else:
                return [i.name for i in Outline][section]

        elif role == Qt.SizeHintRole:
            if section == Outline.compile.value:
                return QSize(40, 30)
            elif section == Outline.goalPercentage.value:
                return QSize(100, 30)
            else:
                return QVariant()
        else:
            return QVariant()

        return True

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

        if index.isValid() and index.column() == Outline.compile.value:
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

        # def canDropMimeData(self, data, action, row, column, parent):
        # if not data.hasFormat("application/xml"):
        # return False

        # if column > 0:
        # return False

        # return True

    def dropMimeData(self, data, action, row, column, parent):

        if action == Qt.IgnoreAction:
            return True  # What is that?

        if not data.hasFormat("application/xml"):
            return False

        if column > 0:
            column = 0

        if row != -1:
            beginRow = row
        elif parent.isValid():
            beginRow = self.rowCount(parent) + 1
        else:
            beginRow = self.rowCount() + 1

        encodedData = bytes(data.data("application/xml")).decode()

        root = ET.XML(encodedData)

        if root.tag != "outlineItems":
            return False

        items = []
        for child in root:
            if child.tag == "outlineItem":
                item = outlineItem(xml=ET.tostring(child))
                items.append(item)

        if not items:
            return False

        r = self.insertItems(items, beginRow, parent)

        if action == Qt.CopyAction:
            for item in items:
                item.getUniqueID()

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
            self.beginInsertRows(parent, row, row + len(items) - 1)

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

        self.beginRemoveRows(parent, row, row + count - 1)
        for i in range(count):
            parentItem.removeChild(row)

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

    def pathToIndex(self, index, path=""):
        # FIXME: Use item's ID instead of rows
        if not index.isValid():
            return ""
        if index.parent().isValid():
            path = self.pathToIndex(index.parent())
        if path:
            path = "{},{}".format(path, str(index.row()))
        else:
            path = str(index.row())

        return path

    def indexFromPath(self, path):
        path = path.split(",")
        item = self.rootItem
        for p in path:
            if p != "" and int(p) < item.childCount():
                item = item.child(int(p))
        return self.indexFromItem(item)


class outlineItem():
    def __init__(self, model=None, title="", _type="folder", xml=None, parent=None, ID=None):

        self._data = {}
        self.childItems = []
        self._parent = None
        self._model = model
        self.defaultTextType = None
        self.IDs = []  # used by root item to store unique IDs

        if title:
            self._data[Outline.title] = title

        self._data[Outline.type] = _type
        self._data[Outline.compile] = Qt.Checked

        if xml is not None:
            self.setFromXML(xml)

        if parent:
            parent.appendChild(self)

        if ID:
            self._data[Outline.ID] = ID

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def children(self):
        return self.childItems

    def columnCount(self):
        return len(Outline)

    def data(self, column, role=Qt.DisplayRole):

        # print("Data: ", column, role)

        if role == Qt.DisplayRole or role == Qt.EditRole:
            # if column == Outline.compile.value:
            # return self.data(column, Qt.CheckStateRole)

            if Outline(column) in self._data:
                return self._data[Outline(column)]

            elif column == Outline.revisions.value:
                return []

            else:
                return ""

        elif role == Qt.DecorationRole and column == Outline.title.value:
            if self.isFolder():
                return QIcon.fromTheme("folder")
            elif self.isText():
                return QIcon.fromTheme("text-x-generic")
            elif self.isT2T():
                return QIcon.fromTheme("text-x-script")
            elif self.isHTML():
                return QIcon.fromTheme("text-html")

                # elif role == Qt.ForegroundRole:
                # if self.isCompile() in [0, "0"]:
                # return QBrush(Qt.gray)

        elif role == Qt.CheckStateRole and column == Outline.compile.value:
            # print(self.title(), self.compile())
            # if self._data[Outline(column)] and not self.compile():
            # return Qt.PartiallyChecked
            # else:
            return self._data[Outline(column)]

        elif role == Qt.FontRole:
            f = QFont()
            if column == Outline.wordCount.value and self.isFolder():
                f.setItalic(True)
            elif column == Outline.goal.value and self.isFolder() and self.data(Outline.setGoal) == None:
                f.setItalic(True)
            if self.isFolder():
                f.setBold(True)
            return f

    def setData(self, column, data, role=Qt.DisplayRole):
        if role not in [Qt.DisplayRole, Qt.EditRole, Qt.CheckStateRole]:
            print(column, column == Outline.text.value, data, role)
            return

        if column == Outline.text.value and self.isFolder():
            # Folder have no text
            return

        if column == Outline.goal.value:
            self._data[Outline.setGoal] = toInt(data) if toInt(data) > 0 else ""

        # Checking if we will have to recount words
        updateWordCount = False
        if column in [Outline.wordCount.value, Outline.goal.value, Outline.setGoal.value]:
            updateWordCount = not Outline(column) in self._data or self._data[Outline(column)] != data

        # Stuff to do before
        if column == Outline.type.value:
            oldType = self._data[Outline.type]
            if oldType == "html" and data in ["txt", "t2t"]:
                # Resource inneficient way to convert HTML to plain text
                e = QTextEdit()
                e.setHtml(self._data[Outline.text])
                self._data[Outline.text] = e.toPlainText()
            elif oldType in ["txt", "t2t"] and data == "html" and Outline.text in self._data:
                self._data[Outline.text] = self._data[Outline.text].replace("\n", "<br>")

        elif column == Outline.text.value:
            self.addRevision()

        # Setting data
        self._data[Outline(column)] = data

        # Stuff to do afterwards
        if column == Outline.text.value:
            wc = wordCount(data)
            self.setData(Outline.wordCount.value, wc)

        if column == Outline.compile.value:
            self.emitDataChanged(cols=[Outline.title.value, Outline.compile.value], recursive=True)

        if updateWordCount:
            self.updateWordCount()

    def updateWordCount(self, emit=True):
        """Update word count for item and parents.
        If emit is False, no signal is emitted (sometimes cause segfault)"""
        if not self.isFolder():
            setGoal = toInt(self.data(Outline.setGoal.value))
            goal = toInt(self.data(Outline.goal.value))

            if goal != setGoal:
                self._data[Outline.goal] = setGoal
            if setGoal:
                wc = toInt(self.data(Outline.wordCount.value))
                self.setData(Outline.goalPercentage.value, wc / float(setGoal))

        else:
            wc = 0
            for c in self.children():
                wc += toInt(c.data(Outline.wordCount.value))
            self._data[Outline.wordCount] = wc

            setGoal = toInt(self.data(Outline.setGoal.value))
            goal = toInt(self.data(Outline.goal.value))

            if setGoal:
                if goal != setGoal:
                    self._data[Outline.goal] = setGoal
                    goal = setGoal
            else:
                goal = 0
                for c in self.children():
                    goal += toInt(c.data(Outline.goal.value))
                self._data[Outline.goal] = goal

            if goal:
                self.setData(Outline.goalPercentage.value, wc / float(goal))
            else:
                self.setData(Outline.goalPercentage.value, "")

        if emit:
            self.emitDataChanged([Outline.goal.value, Outline.setGoal.value,
                                  Outline.wordCount.value, Outline.goalPercentage.value])

        if self.parent():
            self.parent().updateWordCount(emit)

    def row(self):
        if self.parent:
            return self.parent().childItems.index(self)

    def appendChild(self, child):
        self.insertChild(self.childCount(), child)

    def insertChild(self, row, child):
        self.childItems.insert(row, child)
        child._parent = self
        child.setModel(self._model)
        if not child.data(Outline.ID.value):
            child.getUniqueID()
        self.updateWordCount()

    def setModel(self, model):
        self._model = model
        for c in self.children():
            c.setModel(model)

    def index(self, column=0):
        if self._model:
            return self._model.indexFromItem(self, column)
        else:
            return QModelIndex()

    def emitDataChanged(self, cols=None, recursive=False):
        idx = self.index()
        if idx and self._model:
            if not cols:
                # Emit data changed for the whole item (all columns)
                self._model.dataChanged.emit(idx, self.index(len(Outline)))

            else:
                # Emit only for the specified columns
                for c in cols:
                    self._model.dataChanged.emit(self.index(c), self.index(c))

            if recursive:
                for c in self.children():
                    c.emitDataChanged(cols, recursive=True)

    def removeChild(self, row):
        self.childItems.pop(row)
        # Might be causing segfault when updateWordCount emits dataChanged
        self.updateWordCount(emit=False)

    def parent(self):
        return self._parent

    def type(self):
        return self._data[Outline.type]

    def isFolder(self):
        return self._data[Outline.type] == "folder"

    def isT2T(self):
        return self._data[Outline.type] == "t2t"

    def isHTML(self):
        return self._data[Outline.type] == "html"

    def isText(self):
        return self._data[Outline.type] == "txt"

    def text(self):
        return self.data(Outline.text.value)

    def compile(self):
        if self._data[Outline.compile] in ["0", 0]:
            return False
        elif self.parent():
            return self.parent().compile()
        else:
            return True  # rootItem always compile

    def title(self):
        if Outline.title in self._data:
            return self._data[Outline.title]
        else:
            return ""

    def ID(self):
        return self.data(Outline.ID.value)

    def POV(self):
        return self.data(Outline.POV.value)

    def status(self):
        return self.data(Outline.status.value)

    def label(self):
        return self.data(Outline.label.value)

    def path(self):
        "Returns path to item as string."
        if self.parent().parent():
            return "{} > {}".format(self.parent().path(), self.title())
        else:
            return self.title()

    def pathID(self):
        "Returns path to item as list of (ID, title)."
        if self.parent().parent():
            return self.parent().pathID() + [(self.ID(), self.title())]
        else:
            return [(self.ID(), self.title())]

    def level(self):
        if self.parent():
            return self.parent().level() + 1
        else:
            return -1

    def stats(self):
        wc = self.data(Outline.wordCount.value)
        goal = self.data(Outline.goal.value)
        progress = self.data(Outline.goalPercentage.value)
        if not wc:
            wc = 0
        if goal:
            return qApp.translate("outlineModel", "{} words / {} ({})").format(
                    locale.format("%d", wc, grouping=True),
                    locale.format("%d", goal, grouping=True),
                    "{}%".format(str(int(progress * 100))))
        else:
            return qApp.translate("outlineModel", "{} words").format(
                    locale.format("%d", wc, grouping=True))


        ###############################################################################
        # XML
        ###############################################################################

    def toXML(self):
        item = ET.Element("outlineItem")

        # We don't want to write some datas (computed)
        exclude = [Outline.wordCount, Outline.goal, Outline.goalPercentage, Outline.revisions]
        # We want to force some data even if they're empty
        force = [Outline.compile]

        for attrib in Outline:
            if attrib in exclude: continue
            val = self.data(attrib.value)
            if val or attrib in force:
                item.set(attrib.name, str(val))

        # Saving revisions
        rev = self.revisions()
        for r in rev:
            revItem = ET.Element("revision")
            revItem.set("timestamp", str(r[0]))
            revItem.set("text", r[1])
            item.append(revItem)

        for i in self.childItems:
            item.append(ET.XML(i.toXML()))

        return ET.tostring(item)

    def setFromXML(self, xml):
        root = ET.XML(xml)

        for k in root.attrib:
            if k in Outline.__members__:
                # if k == Outline.compile:
                # self.setData(Outline.__members__[k].value, unicode(root.attrib[k]), Qt.CheckStateRole)
                # else:
                self.setData(Outline.__members__[k].value, str(root.attrib[k]))

        for child in root:
            if child.tag == "outlineItem":
                item = outlineItem(self._model, xml=ET.tostring(child), parent=self)
            elif child.tag == "revision":
                self.appendRevision(child.attrib["timestamp"], child.attrib["text"])


            ###############################################################################
            # IDS
            ###############################################################################

    def getUniqueID(self):
        self.setData(Outline.ID.value, self._model.rootItem.findUniqueID())

    def checkIDs(self):
        """This is called when a model is loaded.

        Makes a list of all sub-items IDs, that is used to generate unique IDs afterwards.
        """
        self.IDs = self.listAllIDs()

        if max([self.IDs.count(i) for i in self.IDs if i]) != 1:
            print("There are some doublons:", [i for i in self.IDs if i and self.IDs.count(i) != 1])

        def checkChildren(item):
            for c in item.children():
                _id = c.data(Outline.ID.value)
                if not _id or _id == "0":
                    c.getUniqueID()
                checkChildren(c)

        checkChildren(self)

    def listAllIDs(self):
        IDs = [self.data(Outline.ID.value)]
        for c in self.children():
            IDs.extend(c.listAllIDs())
        return IDs

    def findUniqueID(self):
        k = 0
        while str(k) in self.IDs:
            k += 1
        self.IDs.append(str(k))
        return str(k)

    def pathToItem(self):
        path = self.data(Outline.ID.value)
        if self.parent().parent():
            path = "{}:{}".format(self.parent().pathToItem(), path)
        return path

    def findItemsByPOV(self, POV):
        "Returns a list of IDs of all subitems whose POV is ``POV``."
        lst = []
        if self.POV() == POV:
            lst.append(self.ID())

        for c in self.children():
            lst.extend(c.findItemsByPOV(POV))

        return lst

    def findItemsContaining(self, text, columns, mainWindow, caseSensitive=False):
        """Returns a list if IDs of all subitems
        containing ``text`` in columns ``columns``
        (being a list of int).
        """
        lst = []
        text = text.lower() if not caseSensitive else text
        for c in columns:

            if c == Outline.POV.value:
                searchIn = mainWindow.mdlPersos.getPersoNameByID(self.POV())

            elif c == Outline.status.value:
                searchIn = mainWindow.mdlStatus.item(toInt(self.status()), 0).text()

            elif c == Outline.label.value:
                searchIn = mainWindow.mdlLabels.item(toInt(self.label()), 0).text()

            else:
                searchIn = self.data(c)

            searchIn = searchIn.lower() if not caseSensitive else searchIn

            if text in searchIn:
                if not self.ID() in lst:
                    lst.append(self.ID())

        for c in self.children():
            lst.extend(c.findItemsContaining(text, columns, mainWindow, caseSensitive))

        return lst

    ###############################################################################
    # REVISIONS
    ###############################################################################

    def revisions(self):
        return self.data(Outline.revisions.value)

    def appendRevision(self, ts, text):
        if not Outline.revisions in self._data:
            self._data[Outline.revisions] = []

        self._data[Outline.revisions].append((
            int(ts),
            text))

    def addRevision(self):
        if not settings.revisions["keep"]:
            return

        if not Outline.text in self._data:
            return

        self.appendRevision(
                time.time(),
                self._data[Outline.text])

        if settings.revisions["smartremove"]:
            self.cleanRevisions()

        self.emitDataChanged([Outline.revisions.value])

    def deleteRevision(self, ts):
        self._data[Outline.revisions] = [r for r in self._data[Outline.revisions] if r[0] != ts]
        self.emitDataChanged([Outline.revisions.value])

    def clearAllRevisions(self):
        self._data[Outline.revisions] = []
        self.emitDataChanged([Outline.revisions.value])

    def cleanRevisions(self):
        "Keep only one some the revisions."
        rev = self.revisions()
        rev2 = []
        now = time.time()

        rule = settings.revisions["rules"]

        revs = {}
        for i in rule:
            revs[i] = []

        for r in rev:
            # Have to put the lambda key otherwise cannot order when one element is None
            for span in sorted(rule, key=lambda x: x if x else 60 * 60 * 24 * 30 * 365):
                if not span or now - r[0] < span:
                    revs[span].append(r)
                    break

        for span in revs:
            sortedRev = sorted(revs[span], key=lambda x: x[0])
            last = None
            for r in sortedRev:
                if not last:
                    rev2.append(r)
                    last = r[0]
                elif r[0] - last >= rule[span]:
                    rev2.append(r)
                    last = r[0]

        if rev2 != rev:
            self._data[Outline.revisions] = rev2
            self.emitDataChanged([Outline.revisions.value])
