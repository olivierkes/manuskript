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
from manuskript import enums
from manuskript.functions import mainWindow, toInt, wordCount
from manuskript.converters import HTML2PlainText

try:
    locale.setlocale(locale.LC_ALL, '')
except:
    # Invalid locale, but not really a big deal because it's used only for
    # number formating
    pass
import os


class abstractItem():

    # Enum kept on the class for easier acces
    enum = enums.Abstract

    # Used for XML export
    name = "abstractItem"

    def __init__(self, model=None, title="", _type="abstract", xml=None, parent=None, ID=None):

        self._data = {}
        self.childItems = []
        self._parent = None
        self._model = model

        self.IDs = ["0"]  # used by root item to store unique IDs
        self._lastPath = ""  # used by loadSave version_1 to remember which files the items comes from,
                             # in case it is renamed / removed

        self._data[self.enum.title] = title
        self._data[self.enum.type] = _type

        if xml is not None:
            self.setFromXML(xml)

        if parent:
            parent.appendChild(self)

        if ID:
            self._data[self.enum.ID] = ID

    #######################################################################
    # Model
    #######################################################################

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
        """
        Emits the dataChanged signal of the model, to signal views that data
        have changed.

        @param cols: an array of int (or None). The columns of the index that
                     have been changed.
        @param recursive: boolean. If true, all children will also emit the
                     dataChanged signal.
        """
        idx = self.index()
        if idx and self._model:
            if not cols:
                # Emit data changed for the whole item (all columns)
                self._model.dataChanged.emit(idx, self.index(len(self.enum)))

            else:
                # Emit only for the specified columns
                for c in cols:
                    self._model.dataChanged.emit(self.index(c), self.index(c))

            if recursive:
                for c in self.children():
                    c.emitDataChanged(cols, recursive=True)

    #######################################################################
    # Properties
    #######################################################################

    def title(self):
        return self._data.get(self.enum.title, "")

    def ID(self):
        return self._data.get(self.enum.ID, 0)

    def columnCount(self):
        return len(self.enum)

    def type(self):
        return self._data[self.enum.type]

    #######################################################################
    # Parent / Children managment
    #######################################################################

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def childCountRecursive(self):
        n = self.childCount()
        for c in self.children():
            n += c.childCountRecursive()
        return n

    def children(self):
        return self.childItems

    def row(self):
        if self.parent():
            return self.parent().childItems.index(self)

    def appendChild(self, child):
        self.insertChild(self.childCount(), child)

    def insertChild(self, row, child):
        self.childItems.insert(row, child)
        child._parent = self
        child.setModel(self._model)
        if not child.ID():
            child.getUniqueID()

    def removeChild(self, row):
        """
        Removes child at position `row` and returns it.
        @param row: index (int) of the child to remove.
        @return: the removed abstractItem
        """
        r = self.childItems.pop(row)
        return r

    def parent(self):
        return self._parent

    def path(self, sep=" > "):
        "Returns path to item as string."
        if self.parent().parent():
            return "{parent}{sep}{title}".format(
                parent=self.parent().path(),
                sep=sep,
                title=self.title())
        else:
            return self.title()

    def pathID(self):
        "Returns path to item as list of (ID, title)."
        if self.parent() and self.parent().parent():
            return self.parent().pathID() + [(self.ID(), self.title())]
        else:
            return [(self.ID(), self.title())]

    def level(self):
        """Returns the level of the current item. Root item returns -1."""
        if self.parent():
            return self.parent().level() + 1
        else:
            return -1

    def copy(self):
        """
        Returns a copy of item, with no parent, and no ID.
        """
        item = self.__class__(xml=self.toXML())
        item.setData(self.enum.ID, None)
        return item

    ###############################################################################
    # IDS
    ###############################################################################

    def getUniqueID(self, recursive=False):
        self.setData(Outline.ID, self._model.rootItem.findUniqueID())

        if recursive:
            for c in self.children():
                c.getUniqueID(recursive)

    def checkIDs(self):
        """This is called when a model is loaded.

        Makes a list of all sub-items IDs, that is used to generate unique IDs afterwards.
        """
        self.IDs = self.listAllIDs()

        if max([self.IDs.count(i) for i in self.IDs if i]) != 1:
            print("WARNING ! There are some items with same IDs:", [i for i in self.IDs if i and self.IDs.count(i) != 1])

        def checkChildren(item):
            for c in item.children():
                _id = c.ID()
                if not _id or _id == "0":
                    c.getUniqueID()
                checkChildren(c)

        checkChildren(self)

    def listAllIDs(self):
        IDs = [self.ID()]
        for c in self.children():
            IDs.extend(c.listAllIDs())
        return IDs

    def findUniqueID(self):
        IDs = [int(i) for i in self.IDs]
        k = 1
        while k in IDs:
            k += 1
        self.IDs.append(str(k))
        return str(k)

    #######################################################################
    # Data
    #######################################################################

    def data(self, column, role=Qt.DisplayRole):

        # print("Data: ", column, role)

        if role == Qt.DisplayRole or role == Qt.EditRole:
            # if column == Outline.compile:
            # return self.data(column, Qt.CheckStateRole)

            if Outline(column) in self._data:
                return self._data[Outline(column)]

            elif column == Outline.revisions:
                return []

            else:
                return ""

        elif role == Qt.DecorationRole and column == Outline.title:
            if self.customIcon():
                return QIcon.fromTheme(self.data(Outline.customIcon))
            if self.isFolder():
                return QIcon.fromTheme("folder")
            elif self.isMD():
                return QIcon.fromTheme("text-x-generic")

                # elif role == Qt.ForegroundRole:
                # if self.isCompile() in [0, "0"]:
                # return QBrush(Qt.gray)

        elif role == Qt.CheckStateRole and column == Outline.compile:
            # print(self.title(), self.compile())
            # if self._data[Outline(column)] and not self.compile():
            # return Qt.PartiallyChecked
            # else:
            return self._data[Outline(column)]

        elif role == Qt.FontRole:
            f = QFont()
            if column == Outline.wordCount and self.isFolder():
                f.setItalic(True)
            elif column == Outline.goal and self.isFolder() and self.data(Outline.setGoal) == None:
                f.setItalic(True)
            if self.isFolder():
                f.setBold(True)
            return f

    def setData(self, column, data, role=Qt.DisplayRole):
        if role not in [Qt.DisplayRole, Qt.EditRole, Qt.CheckStateRole]:
            print(column, column == Outline.text, data, role)
            return

        if column == Outline.text and self.isFolder():
            # Folder have no text
            return

        if column == Outline.goal:
            self._data[Outline.setGoal] = toInt(data) if toInt(data) > 0 else ""

        # Checking if we will have to recount words
        updateWordCount = False
        if column in [Outline.wordCount, Outline.goal, Outline.setGoal]:
            updateWordCount = not Outline(column) in self._data or self._data[Outline(column)] != data

        # Stuff to do before
        if column == Outline.text:
            self.addRevision()

        # Setting data
        self._data[Outline(column)] = data

        # Stuff to do afterwards
        if column == Outline.text:
            wc = wordCount(data)
            self.setData(Outline.wordCount, wc)
            self.emitDataChanged(cols=[Outline.text]) # new in 0.5.0

        if column == Outline.compile:
            self.emitDataChanged(cols=[Outline.title, Outline.compile], recursive=True)

        if column == Outline.customIcon:
            # If custom icon changed, we tell views to update title (so that icons
            # will be updated as well)
            self.emitDataChanged(cols=[Outline.title])

        if updateWordCount:
            self.updateWordCount()

    ###############################################################################
    # XML
    ###############################################################################

    # We don't want to write some datas (computed)
    XMLExclude = [Outline.wordCount, Outline.goal, Outline.goalPercentage, Outline.revisions]
    # We want to force some data even if they're empty
    XMLForce = [Outline.compile]

    def toXML(self):
        item = ET.Element(self.name)

        ## We don't want to write some datas (computed)
        #exclude = [Outline.wordCount, Outline.goal, Outline.goalPercentage, Outline.revisions]
        ## We want to force some data even if they're empty
        #force = [Outline.compile]

        for attrib in self.enum:
            if attrib in self.XMLExclude:
                continue
            val = self.data(attrib)
            if val or attrib in self.XMLForce:
                item.set(attrib.name, str(val))

        # Saving revisions
        rev = self.revisions()
        for r in rev:
            revItem = ET.Element("revision")
            revItem.set("timestamp", str(r[0]))
            revItem.set("text", r[1])
            item.append(revItem)

        # Saving lastPath
        item.set("lastPath", self._lastPath)

        for i in self.childItems:
            item.append(ET.XML(i.toXML()))

        return ET.tostring(item)

    def toXML_(self):
        item = ET.Element("outlineItem")

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

        # Saving lastPath
        item.set("lastPath", self._lastPath)

        for i in self.childItems:
            item.append(ET.XML(i.toXML()))

        return ET.tostring(item)

    def setFromXML(self, xml):
        root = ET.XML(xml)

        for k in root.attrib:
            if k in Outline.__members__:
                # if k == Outline.compile:
                # self.setData(Outline.__members__[k], unicode(root.attrib[k]), Qt.CheckStateRole)
                # else:
                self.setData(Outline.__members__[k], str(root.attrib[k]))

        if "lastPath" in root.attrib:
            self._lastPath = root.attrib["lastPath"]

        # If loading from an old file format, convert to md and remove html markup
        if self.type() in ["txt", "t2t"]:
            self.setData(Outline.type, "md")

        elif self.type() == "html":
            self.setData(Outline.type, "md")
            self.setData(Outline.text, HTML2PlainText(self.data(Outline.text)))
            self.setData(Outline.notes, HTML2PlainText(self.data(Outline.notes)))

        for child in root:
            if child.tag == "outlineItem":
                item = outlineItem(self._model, xml=ET.tostring(child), parent=self)
            elif child.tag == "revision":
                self.appendRevision(child.attrib["timestamp"], child.attrib["text"])

