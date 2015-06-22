#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from functions import *
import settings

class plotListView(QListWidget):
    
    def __init__(self, parent=None):
        QListWidget.__init__(self, parent)
        self._model = None
        self._catRow = [-1, -1, -1]
        self._catCheckedState = [True, True, True]
        self._filter = ""
        self._lastID = 1
        self._updating = False
        
        self.currentItemChanged.connect(self._currentItemChanged)
        
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
        for i in range(self.count()):
            ID = self.item(i).data(Qt.UserRole)
            if ID:
                name = self._model.getNameByID(ID)
                self.item(i).setText(name)
            
    def updateItems(self):
        self._updating = True
        self.clear()
        plots = self._model.getPlotsByImportance()
        
        h = [self.tr("Main"), self.tr("Secondary"), self.tr("Minor")]
        for i in range(3):
            b = QPushButton(h[i])
            b.setCheckable(True)
            #b.setFlat(True)
            b.setChecked(self._catCheckedState[i])
            b.toggled.connect(self.updateCatState)
            if self._catCheckedState[i]:
                b.setStyleSheet("background:#e6e6ff; color:darkBlue; border-radius:0px; font:bold;")
            else:
                b.setStyleSheet("background:#EEE; color:333; border-radius:0px; font:bold;")
            self.addItem(h[i])
            self.setItemWidget(self.item(self.count()-1), b)
            self._catRow[i] = self.count()-1
            
            if self._catCheckedState[i]:
                for ID in plots[i]:
                    name = self._model.getNameByID(ID)
                    if not self._filter.lower() in name.lower(): 
                        continue
                    item = QListWidgetItem(name)
                    item.setData(Qt.UserRole, ID)
                    self.addItem(item)
        
        self.setCurrentItem(self.getItemByID(self._lastID))
        self._updating = False
        
    def updateCatState(self):
        for i in range(3):
            row = self._catRow[i]
            b = self.itemWidget(self.item(row))
            self._catCheckedState[i] = b.isChecked()
        self.updateItems()

    def _currentItemChanged(self, current, previous):
        if self._updating:
            return
        
        if current.data(Qt.UserRole):
            self._lastID = current.data(Qt.UserRole)
        
    def getItemByID(self, ID):
        for i in range(self.count()):
            if self.item(i).data(Qt.UserRole) == ID:
                return self.item(i)
        
    def currentIndex(self):
        ID = None
        if self.currentItem():
            ID = self.currentItem().data(Qt.UserRole)
        
        return self._model.getIndexFromID(ID)