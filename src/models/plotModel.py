#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from functions import *

class plotModel(QStandardItemModel):
    
    def __init__(self):
        QStandardItemModel.__init__(self, 0, 3)
        self.setHorizontalHeaderLabels([i.name for i in Plot])
        self.mw = mainWindow()
        
        self.updatePlotPersoButton()
        self.mw.mdlPersos.dataChanged.connect(self.updatePlotPersoButton)
        
    def addPlot(self):
        p = QStandardItem(self.tr("New plot"))
        _id = QStandardItem(self.getUniqueID())
        importance = QStandardItem(str(0))
        self.appendRow([p, _id, importance])
            
    def getUniqueID(self, parent=QModelIndex()):
        "Returns an unused ID"
        parentItem = self.itemFromIndex(parent)
        vals = []
        for i in range(self.rowCount(parent)):
            index = self.index(i, Plot.ID.value, parent)
            #item = self.item(i, Plot.ID.value)
            if index.isValid() and index.data():
                vals.append(int(index.data()))
                
        k = 0
        while k in vals: k += 1
        return str(k)
        
    def removePlot(self, index):
        self.takeRow(index.row())
        
    def currentIndex(self):
        i = self.mw.lstPlots.selectionModel().currentIndex()
        if i .isValid():
            return i
        else:
            return None
        
    def addSubPlot(self):
        index = self.currentIndex()
        if not index:
            return
        parent = index.sibling(index.row(), Plot.subplots.value)
        parentItem = self.itemFromIndex(parent)
        p = QStandardItem(self.tr("New subplot"))
        _id = QStandardItem(self.getUniqueID(parent))
        summary = QStandardItem()
        parentItem.appendRow([p, _id, summary])
    
    def removeSubPlot(self):
        index = self.mw.lstSubPlots.currentIndex()
        if not index.isValid():
            return
        parent = index.parent()
        parentItem = self.itemFromIndex(parent)
        parentItem.takeRow(index.row())
        
    def addPlotPerso(self, v):
        if self.currentIndex():
            if not self.item(self.currentIndex().row(), Plot.persos.value):
                self.setItem(self.currentIndex().row(), Plot.persos.value, QStandardItem())
            item = self.item(self.currentIndex().row(), Plot.persos.value)
            
            # We check that the PersoID is not in the list yet
            for i in range(item.rowCount()):
                if item.child(i).text() == str(v):
                    return
            
            item.appendRow(QStandardItem(str(v)))
    
    def removePlotPerso(self):
        index = self.mw.lstPlotPerso.currentIndex()
        if not index.isValid():
            return
        parent = index.parent()
        parentItem = self.itemFromIndex(parent)
        parentItem.takeRow(index.row())
    
    def updatePlotPersoButton(self):
        menu = QMenu()
        
        menus = []
        for i in [self.tr("Main"), self.tr("Secondary"), self.tr("Minor")]:
            m = QMenu(i, menu)
            menus.append(m)
            menu.addMenu(m)
        
        mpr = QSignalMapper(menu)
        for i in range(self.mw.mdlPersos.rowCount()):
            if self.mw.mdlPersos.item(i, Perso.ID.value):
                a = QAction(self.mw.mdlPersos.item(i, Perso.name.value).text(), menu)
                a.triggered.connect(mpr.map)
                mpr.setMapping(a, int(self.mw.mdlPersos.item(i, Perso.ID.value).text()))
            
                imp = self.mw.mdlPersos.item(i, Perso.importance.value)
                if imp:
                    imp = toInt(imp.text())
                else:
                    imp = 0
                
                menus[2-imp].addAction(a)
            
        mpr.mapped.connect(self.addPlotPerso)
        self.mw.btnAddPlotPerso.setMenu(menu)
        
    def viewModel(self):
        "Returns proxy model if any, else self"
        return self
    
    def flags(self, index):
        parent = index.parent()
        if parent.isValid(): # this is a subitem
            return  Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
        else:
            return QStandardItemModel.flags(self, index)