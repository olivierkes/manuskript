#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from __future__ import print_function
from __future__ import unicode_literals

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from enum import Enum

class Outline(Enum):
    title = 0
    ID = 1
    type = 2
    summarySentance = 3
    summaryFull = 4
    POV = 5
    notes = 6
    status = 7
    compile = 8
    

class outlineModel(QAbstractItemModel):
    def __init__(self):
        QAbstractItemModel.__init__(self)
        
        self.rootItem = outlineItem()
    
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
        self.dataChanged.emit(index, index)
        return True
    
    def flags(self, index):
        flags = Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
        
        if index.isValid() and index.internalPointer().isFolder():
            flags |= Qt.ItemIsDropEnabled
            
        return flags
        
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return [i.name for i in Outline][section]
        else:
            return QVariant()
    
    #def insertRow(self, row, item, parent=QModelIndex()):
        #self.beginInsertRows(parent, row, row)
        
        #if not parent.isValid():
            #parentItem = self.rootItem
        #else:
            #parentItem = parent.internalPointer()
            
        #parentItem.insertChild(row, item)
        
        #self.endInsertRows()
        
    def appendRow(self, item, parent=QModelIndex()):
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        
        if parentItem.isFolder():
            self.beginInsertRows(parent, parentItem.childCount(), parentItem.childCount())
            parentItem.appendChild(item)
            self.endInsertRows()
        
    def removeIndex(self, index):
        item = index.internalPointer()
        self.removeRow(item.row(), 1, index.parent())
            
        
    def removeRow(self, row, count, parent=QModelIndex()):
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
            
        self.beginRemoveRows(parent, row, row)
        parentItem.removeChild(row)
        self.endRemoveRows()
        return True
    
class outlineItem():
    def __init__(self, title="", type="folder", parent=None):
        
        self._parent = parent
        
        self._data = {}
        self.childItems = []
        
        self._data[Outline.title] = title
        self._data[Outline.type] = type
        
        
    def child(self, row):
        return self.childItems[row]
    
    def childCount(self):
        return len(self.childItems)
    
    def columnCount(self):
        return len(Outline)
    
    def data(self, column, role=Qt.DisplayRole):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if Outline(column) in self._data:
                return self._data[Outline(column)]
            else:
                return QVariant()
        elif role == Qt.DecorationRole and column == Outline.title.value:
            if self.isFolder():
                return QIcon.fromTheme("folder")
            elif self.isScene():
                return QIcon.fromTheme("document-new")
    
    def setData(self, column, data):
        self._data[Outline(column)] = data
    
    def row(self):
        if self.parent:
            return self.parent().childItems.index(self)
        
    def appendChild(self, child):
        self.childItems.append(child)
        child._parent = self
        
    def insertChild(self, row, child):
        self.childItems.insert(row, child)
        
    def removeChild(self, row):
        self.childItems.pop(row)
        
    def parent(self):
        return self._parent
    
    def isFolder(self):
        return self._data[Outline.type] == "folder"
    
    def isScene(self):
        return self._data[Outline.type] == "scene"