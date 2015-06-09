#!/usr/bin/env python
#--!-- coding: utf8 --!--
 



from qt import *
from enums import *
from models.outlineModel import *

from enum import Enum
from lxml import etree as ET

class persosProxyModel(QAbstractProxyModel):
    
    newStatuses = pyqtSignal()
    
    def __init__(self, parent=None):
        QAbstractProxyModel.__init__(self, parent)
        
        self.rootItem = QStandardItem()
        self.p1 = QStandardItem("Principaux")
        self.p2 = QStandardItem("Secondaires")
        self.p3 = QStandardItem("Mineurs")
        
        self.cats = [
            self.p1,
            self.p2,
            self.p3
            ]
        
        
    def mapFromSource(self, sourceIndex):
        if not sourceIndex.isValid():
            return QModelIndex()
        
        row = sourceIndex.row()
        item = sourceIndex.internalPointer()
        
        if row in self._map[0]:
            row = self._map[0].index(row) + 1
        elif row in self._map[1]:
            row = len(self._map[0]) + 1 + self._map[1].index(row) + 1
        elif row in self._map[2]:
            row = len(self._map[0]) + 1 + len(self._map[1]) + 1 + self._map[2].index(row) + 1
        
        return self.createIndex(row, sourceIndex.column(), item)
        
    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        
        if index.isValid() and not self.mapToSource(index).isValid():
            return Qt.NoItemFlags#Qt.ItemIsEnabled
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        
    def mapToSource(self, proxyIndex):
        if not proxyIndex.isValid():
            return QModelIndex()
        
        row = proxyIndex.row()
        
        if row == 0:
            return QModelIndex()
        elif row < len(self._map[0]) + 1:
            row = self._map[0][row-1]
        elif row == len(self._map[0]) + 1:
            return QModelIndex()
        elif row < len(self._map[0]) + 1 + len(self._map[1]) + 1:
            row = self._map[1][row - 2 - len(self._map[0])]
        elif row == len(self._map[0]) + 1 + len(self._map[1]) + 1:
            return QModelIndex()
        else:
            row = self._map[2][row - 3 - len(self._map[0]) - len(self._map[1])]
        
        item = proxyIndex.internalPointer()
        
        return self.sourceModel().createIndex(row, proxyIndex.column(), item)
            
    def setSourceModel(self, model):
        QAbstractProxyModel.setSourceModel(self, model)
        self.sourceModel().dataChanged.connect(self.mapModel)
        self.sourceModel().rowsInserted.connect(self.mapModel)
        self.sourceModel().rowsRemoved.connect(self.mapModel)
        self.sourceModel().rowsMoved.connect(self.mapModel)
        
        self.mapModel()
        
    
    def mapModel(self):
        self.beginResetModel()
        src = self.sourceModel()
        
        self._map = [[], [], []]
        
        for i in range(src.rowCount()):
            item = src.item(i, Perso.importance.value)
            ID = src.item(i, Perso.ID.value)
            
            if item:
                imp = int(item.text())
            else:
                imp = 0
            
            self._map[2-imp].append(i)
        self.endResetModel()
    
    def numberOfPersosByImportance(self):
        return [len(i) for i in self._map]
    
    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        
        if index.isValid() and not self.mapToSource(index).isValid():
            if role == Qt.DisplayRole:
                n = self.numberOfPersosByImportance()
                p = 0 if row == 0 else \
                    1 if row == n[0] + 1 else \
                    2
                return self.cats[p].text()
            
            elif role == Qt.ForegroundRole:
                return QBrush(Qt.darkBlue)
            elif role == Qt.BackgroundRole:
                return QBrush(QColor(Qt.blue).lighter(190))
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
            elif role == Qt.FontRole:
                f = QFont()
                #f.setPointSize(f.pointSize() + 1)
                f.setWeight(QFont.Bold)
                return f
        else:
            #FIXME: sometimes, the name of the character is not displayed
            return self.sourceModel().data(self.mapToSource(index), role)
    
    def index(self, row, column, parent):
        
        n = self.numberOfPersosByImportance()
        
        if row == 0 or row == n[0] + 1 or row == n[0]+n[1]+2:
            p = 0 if row == 0 else \
                1 if row == n[0] + 1 else \
                2
            
            return self.createIndex(row, column, self.cats[p])
        
        else:
            if row < len(self._map[0]) + 1:
                nrow = self._map[0][row - 1]
            elif row < len(self._map[0]) + 1 + len(self._map[1]) + 1:
                nrow = self._map[1][row - 2 - len(self._map[0])]
            else:
                nrow = self._map[2][row - 3 - len(self._map[0]) - len(self._map[1])]
            
            return self.mapFromSource(self.sourceModel().index(nrow, column, QModelIndex()))
    
    def parent(self, index=QModelIndex()):
        return QModelIndex()
    
    def rowCount(self, parent=QModelIndex()):
        return self.sourceModel().rowCount(QModelIndex())+3
    
    def columnCount(self, parent=QModelIndex()):
        return self.sourceModel().columnCount(QModelIndex())
    
    def item(self, row, col, parent=QModelIndex()):
        idx = self.mapToSource(self.index(row, col, parent))
        return self.sourceModel().item(idx.row(), idx.column())
        
    
    #def setData(self, index, value, role=Qt.EditRole):
        #pass