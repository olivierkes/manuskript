#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from functions import *
import settings

class plotTreeView(QTreeWidget):
    
    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)
        self._model = None
        self._catRow = [-1, -1, -1]
        self._filter = ""
        self._lastID = -1
        self._updating = False
        self._showSubPlot = False
        self.setRootIsDecorated(False)
        self.setIndentation(10)
        
        self.setColumnCount(1)
        self._rootItem = QTreeWidgetItem()
        self.insertTopLevelItem(0, self._rootItem)
        #self.currentItemChanged.connect(self._currentItemChanged)
        
    def setShowSubPlot(self, v):
        self._showSubPlot = v
        self.updateItems()
        
    def setPlotModel(self, model):
        self._model = model
        self._model.dataChanged.connect(self.updateMaybe)
        self._model.rowsInserted.connect(self.updateMaybe2)
        self._model.rowsRemoved.connect(self.updateMaybe2)
        self.updateItems()
        
    def setFilter(self, text):
        self._filter = text
        self.updateItems()
        
    def updateMaybe(self, topLeft, bottomRight):
        if topLeft.parent() != QModelIndex():
            return
        
        if topLeft.column() <= Plot.name.value <= bottomRight.column():
            # Update name
            self.updateNames()
            
        elif topLeft.column() <= Plot.importance.value <= bottomRight.column():
            # Importance changed
            self.updateItems()
            
    def updateMaybe2(self, parent, first, last):
        "Rows inserted or removed"
        if parent == QModelIndex():
            self.updateItems()
            
    def updateNames(self):
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            
            for c in range(item.childCount()):
                sub = item.child(c)
                ID = sub.data(0, Qt.UserRole)
                if ID:
                    name = self._model.getPlotNameByID(ID)
                    sub.setText(0, name)
            
    def updateItems(self):
        if not self._model:
            return
        
        if self.currentItem():
            self._lastID = self.currentItem().data(0, Qt.UserRole)
        
        self._updating = True
        self.clear()
        plots = self._model.getPlotsByImportance()
        
        h = [self.tr("Main"), self.tr("Secondary"), self.tr("Minor")]
        for i in range(3):
            cat = QTreeWidgetItem(self, [h[i]])
            cat.setBackground(0, QBrush(QColor(Qt.blue).lighter(190)))
            cat.setForeground(0, QBrush(Qt.darkBlue))
            cat.setTextAlignment(0, Qt.AlignCenter)
            f = cat.font(0)
            f.setBold(True)
            cat.setFont(0, f)
            self.addTopLevelItem(cat)
            #cat.setChildIndicatorPolicy(cat.DontShowIndicator)
            
            for ID in plots[i]:
                name = self._model.getPlotNameByID(ID)
                if not self._filter.lower() in name.lower(): 
                    continue
                item = QTreeWidgetItem(cat, [name])
                item.setData(0, Qt.UserRole, ID)
                
                if self._showSubPlot:
                    
                    f = item.font(0)
                    f.setBold(True)
                    item.setFont(0, f)
                    
                    for subID, name in self._model.getSubPlotsByID(ID):
                        sub = QTreeWidgetItem(item, [name])
                        sub.setData(0, Qt.UserRole, "{}:{}".format(ID, subID))
                        
                if ID == self._lastID:
                    self.setCurrentItem(item)
                        
        self.expandAll()
        self._updating = False
        
    def getItemByID(self, ID):
        for i in range(self.topLevelItemCount()):
            if self.topLevelItem(i).data(0, Qt.UserRole) == ID:
                return self.topLevelItem(i)
        
    def currentPlotIndex(self):
        ID = None
        if self.currentItem():
            ID = self.currentItem().data(0, Qt.UserRole)
        
        return self._model.getIndexFromID(ID)
    
    def mouseDoubleClickEvent(self, event):
        item = self.currentItem()
        # Catching double clicks to forbid collapsing of toplevel items
        if item.parent():
            QTreeWidget.mouseDoubleClickEvent(self, event)
        