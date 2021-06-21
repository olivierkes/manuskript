#!/usr/bin/env python
# --!-- coding: utf8 --!--

from PyQt5.QtCore import QAbstractItemModel, QMimeData
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QVariant
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QTextEdit, qApp
from lxml import etree as ET
import re

from manuskript import enums

import logging
LOGGER = logging.getLogger(__name__)

class abstractItem():

    # Enum kept on the class for easier access
    enum = enums.Abstract

    # Used for XML export
    name = "abstractItem"

    # Regexp from https://stackoverflow.com/questions/8733233/filtering-out-certain-bytes-in-python
    valid_xml_re = re.compile(u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\U00010000-\U0010FFFF]+')

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

        if xml != None:
            self.setFromXML(xml)

        if parent:
            # add this as a child to the parent, and link to the outlineModel of the parent
            parent.appendChild(self)

        if ID:
            self._data[self.enum.ID] = ID



    #######################################################################
    # Model
    #######################################################################

    def setModel(self, model):
        self._model = model
        if not self.ID():
            self.getUniqueID()
        elif model:
            # if we are setting a model update it's ID
            self._model.updateAvailableIDs(self.ID())
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
        return self._data.get(self.enum.ID)

    def columnCount(self):
        return len(self.enum)

    def type(self):
        return self._data[self.enum.type]

    #######################################################################
    # Parent / Children management
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
        return None

    def appendChild(self, child):
        self.insertChild(self.childCount(), child)

    def insertChild(self, row, child):
        self.childItems.insert(row, child)
        child._parent = self
        child.setModel(self._model)

    def removeChild(self, row):
        """
        Removes child at position `row` and returns it.
        @param row: index (int) of the child to remove.
        @return: the removed abstractItem
        """
        r = self.childItems.pop(row)
        # Disassociate the child from its parent and the model.
        r._parent = None
        r.setModel(None)
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

    def siblings(self):
        if self.parent():
            return self.parent().children()
        return []

    ###############################################################################
    # IDS
    ###############################################################################

    def getUniqueID(self, recursive=False):
        if not self._model:
            return

        self.setData(self.enum.ID, self._model.requestNewID())

        if recursive:
            for c in self.children():
                c.getUniqueID(recursive)

    def checkIDs(self):
        """This is called when a model is loaded.

        Makes a list of all sub-items IDs, that is used to generate unique IDs afterwards.
        """
        self.IDs = self.listAllIDs()

        if max([self.IDs.count(i) for i in self.IDs if i]) != 1:
            LOGGER.warning("There are some items with overlapping IDs: %s", [i for i in self.IDs if i and self.IDs.count(i) != 1])

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

    #######################################################################
    # Data
    #######################################################################

    def data(self, column, role=Qt.DisplayRole):
        # Return value in self._data
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self._data.get(column, "")

        # Or return QVariant
        return QVariant()

    def setData(self, column, data, role=Qt.DisplayRole):
        # Setting data
        self._data[column] = data

        # The _model will be none during splitting
        if self._model and column == self.enum.ID:
            self._model.updateAvailableIDs(data)

        # Emit signal
        self.emitDataChanged(cols=[column]) # new in 0.5.0

    ###############################################################################
    # XML
    ###############################################################################

    # We don't want to write some datas (computed)
    XMLExclude = []
    # We want to force some data even if they're empty
    XMLForce = []

    def cleanTextForXML(self, text):
        return self.valid_xml_re.sub('', text)

    def toXML(self):
        """
        Returns a string containing the item (and children) in XML.
        By default, saves all attributes from self.enum and lastPath.
        You can define in XMLExclude and XMLForce what you want to be
        excluded or forcibly included.
        """
        item = ET.Element(self.name)

        for attrib in self.enum:
            if attrib in self.XMLExclude:
                continue
            val = self.data(attrib)
            if val or attrib in self.XMLForce:
                item.set(attrib.name, self.cleanTextForXML(str(val)))

        # Saving lastPath
        item.set("lastPath", self._lastPath)

        # Additional stuff for subclasses
        item = self.toXMLProcessItem(item)

        for i in self.childItems:
            item.append(ET.XML(i.toXML()))

        return ET.tostring(item)

    def toXMLProcessItem(self, item):
        """
        Subclass this to change the behavior of `toXML`.
        """
        return item

    def setFromXML(self, xml):
        root = ET.XML(xml)

        for k in self.enum:
            if k.name in root.attrib:
                self.setData(k, str(root.attrib[k.name]))

        if "lastPath" in root.attrib:
            self._lastPath = root.attrib["lastPath"]

        self.setFromXMLProcessMore(root)

        for child in root:
            if child.tag == self.name:
                item = self.__class__(self._model, xml=ET.tostring(child), parent=self)

    def setFromXMLProcessMore(self, root):
        """
        Additional stuff that subclasses must do with the XML to restore
        item.
        """
        return
