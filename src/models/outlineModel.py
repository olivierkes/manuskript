#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from __future__ import print_function
from __future__ import unicode_literals

from qt import *
from enums import *

from enum import Enum
from lxml import etree as ET

class outlineModel(QAbstractItemModel):
    
    newStatuses = pyqtSignal()
    
    def __init__(self):
        QAbstractItemModel.__init__(self)
        
        self.rootItem = outlineItem("root", "folder")
        self.generateStatuses()
    
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
    
    def parent(self, index=QModelIndex()):
        if not index.isValid():
            return QModelIndex()
        
        childItem = index.internalPointer()
        parentItem = childItem.parent()
        
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
        item.setData(index.column(), value)
        
        if index.column() == Outline.status.value:
            self.generateStatuses()
        
        self.dataChanged.emit(index, index)
        return True
        
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return [i.name for i in Outline][section]
        else:
            return QVariant()
        return True
    
    #################### DRAG AND DROP ########################
    # http://doc.qt.io/qt-5/model-view-programming.html#using-drag-and-drop-with-item-views
    
    def flags(self, index):
        #FIXME when dragging folders, sometimes flags is not called
        
        flags = QAbstractItemModel.flags(self, index) | Qt.ItemIsEditable 
        
        if index.isValid() and index.internalPointer().isFolder():
            flags |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled 
            
        elif index.isValid():
            flags |= Qt.ItemIsDragEnabled
            
        else:
            flags |= Qt.ItemIsDropEnabled
        
        if index.isValid() and index.column() == Outline.compile.value:
            flags |= Qt.ItemIsUserCheckable
        
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
        
        #return Qt.MoveAction # Qt.CopyAction | 
        return Qt.CopyAction | Qt.MoveAction
    
    def canDropMomeData(data, action, row, column, parent):
        if not data.hasFormat("application/xml"):
            return False

        if column > 0:
            return False

        return True
    
    def dropMimeData(self, data, action, row, column, parent):
        
        if action == Qt.IgnoreAction:
            return True  # What is that?
        
        if not data.hasFormat("application/xml"):
            return False
        
        if column > 0:
            column = 0
        
        if row <> -1:
            beginRow = row
        elif parent.isValid():
            beginRow = self.rowCount(parent) + 1
        else:
            beginRow = self.rowCount() + 1
            
        encodedData = str(data.data("application/xml"))
        
        root = ET.XML(encodedData)
        
        if root.tag <> "outlineItems":
            return False
        
        items = []
        for child in root:
            if child.tag == "outlineItem":
                items.append(outlineItem(xml=ET.tostring(child)))
                
        if not items:
            return False
        
        self.insertItems(items, beginRow, parent)
        
        return True
        
    ################# ADDING AND REMOVING #################
        
    def insertItem(self, item, row, parent=QModelIndex()):
        return self.insertItems([item], row, parent)
    
    def insertItems(self, items, row, parent=QModelIndex()):
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
            
        # Insert only if parent is folder
        if parentItem.isFolder():
            self.beginInsertRows(parent, row, row + len(items) - 1)
            
            for i in items:
                parentItem.insertChild(row + items.index(i), i)
            
            self.endInsertRows()
            
        return True
        
    def appendItem(self, item, parent=QModelIndex()):
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        
        # If parent is folder, write into
        if parentItem.isFolder():
            self.insertItem(item, self.rowCount(parent), parent)
            
        # If parent is not folder, write next to
        else:
            self.insertItem(item, parent.row()+1, parent.parent())
        
    def removeIndex(self, index):
        item = index.internalPointer()
        self.removeRow(item.row(), index.parent())
            
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
    
    #def insertRow(self, row, item, parent=QModelIndex()):
        #self.beginInsertRows(parent, row, row)
        
        #if not parent.isValid():
            #parentItem = self.rootItem
        #else:
            #parentItem = parent.internalPointer()
            
        #parentItem.insertChild(row, item)
        
        #self.endInsertRows()
        
        
    ################# XML #################
    
    def saveToXML(self, xml):
        root = ET.XML(self.rootItem.toXML())
        ET.ElementTree(root).write(xml, encoding="UTF-8", xml_declaration=True, pretty_print=True)
    
    def loadFromXML(self, xml):
        try:
            root = ET.parse(xml)
            self.rootItem = outlineItem(xml=ET.tostring(root))
            self.generateStatuses()
        except:
            print("N'arrive pas à ouvrir {}".format(xml))
            return
        
        
    ################# DIVERS #################
        
    def generateStatuses(self, item=None):
        if item == None:
            self.statuses = [
                "TODO",
                "First draft",
                "Second draft",
                "Final"
                ]
            item = self.rootItem
        
        val = item.data(Outline.status.value)
        if val and not val in self.statuses:
            self.statuses.append(val)
            self.newStatuses.emit()
            
        for c in item.children():
            self.generateStatuses(c)
            
        
    
class outlineItem():
    
    def __init__(self, title="", type="folder", xml=None):
        
        self._data = {}
        self.childItems = []
        
        if title: self._data[Outline.title] = title
        self._data[Outline.type] = type
        
        if xml is not None:
            self.setFromXML(xml)
        
        
    def child(self, row):
        return self.childItems[row]
    
    def childCount(self):
        return len(self.childItems)
    
    def children(self):
        return self.childItems
    
    def columnCount(self):
        return len(Outline)
    
    def data(self, column, role=Qt.DisplayRole):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if column == Outline.compile.value:
                return self.data(column, Qt.CheckStateRole)
            elif Outline(column) in self._data:
                return self._data[Outline(column)]
            else:
                return None
        elif role == Qt.DecorationRole and column == Outline.title.value:
            if self.isFolder():
                return QIcon.fromTheme("folder")
            elif self.isScene():
                return QIcon.fromTheme("document-new")
            
        elif role == Qt.CheckStateRole and column == Outline.compile.value:
            if Outline(column) in self._data and self._data[Outline(column)]:
                return Qt.Checked
            else:
                return Qt.Unchecked
    
    def setData(self, column, data):
        self._data[Outline(column)] = data
    
    def row(self):
        if self.parent:
            return self.parent().childItems.index(self)
        
    def appendChild(self, child):
        self.insertChild(self.childCount(), child)
        
    def insertChild(self, row, child):
        self.childItems.insert(row, child)
        child._parent = self
        
    def removeChild(self, row):
        self.childItems.pop(row)
        
    def parent(self):
        return self._parent
    
    def isFolder(self):
        return self._data[Outline.type] == "folder"
    
    def isScene(self):
        return self._data[Outline.type] == "scene"
    
    def toXML(self):
        item = ET.Element("outlineItem")
        
        for attrib in Outline:
            val = self.data(attrib)
            if val:
                item.set(attrib.name, unicode(val))
            
        for i in self.childItems:
            item.append(ET.XML(i.toXML()))
            
        return ET.tostring(item)
    
    def setFromXML(self, xml):
        root = ET.XML(xml)
        
        for k in root.attrib:
            if k in Outline.__members__:
                self._data[Outline.__members__[k]] = unicode(root.attrib[k])
                
        for child in root:
            item = outlineItem(xml=ET.tostring(child))
            self.appendChild(item)