#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from functions import *
from models.plotsProxyModel import *

class plotModel(QStandardItemModel):
    
    def __init__(self):
        QStandardItemModel.__init__(self, 0, 3)
        self.setHorizontalHeaderLabels([i.name for i in Plot])
        self.mw = mainWindow()
        #self._proxy = plotsProxyModel()
        #self._proxy.setSourceModel(self)
        
        self.updatePlotPersoButton()
        self.mw.mdlPersos.dataChanged.connect(self.updatePlotPersoButton)
        
####################################################################################################
#                                            QUERIES                                               #
####################################################################################################

    def getPlotsByImportance(self):
        plots = [[], [], []]
        for i in range(self.rowCount()):
            importance = self.item(i, Plot.importance.value).text()
            ID = self.item(i, Plot.ID.value).text()
            plots[2-toInt(importance)].append(ID)
        return plots
    
    def getSubPlotsByID(self, ID):
        index = self.getIndexFromID(ID)
        if not index.isValid():
            return
        index = index.sibling(index.row(), Plot.subplots.value)
        item = self.itemFromIndex(index)
        lst = []
        for i in range(item.rowCount()):
            _ID = item.child(i, Plot.ID.value).text()
            name = item.child(i, Plot.name.value).text()
            lst.append((_ID, name))
        return lst
    
    def getPlotNameByID(self, ID):
        for i in range(self.rowCount()):
            _ID = self.item(i, Plot.ID.value).text()
            if _ID == ID or toInt(_ID) == ID:
                name = self.item(i, Plot.name.value).text()
                return name
        return None
    
    def getIndexFromID(self, ID):
        for i in range(self.rowCount()):
            _ID = self.item(i, Plot.ID.value).text()
            if _ID == ID or toInt(_ID) == ID:
                return self.index(i, 0)
        return QModelIndex()
        
    def currentIndex(self):
        i = self.mw.lstPlots.currentIndex()
        if i .isValid():
            return i
        else:
            return None

####################################################################################################
#                                       ADDING / REMOVING                                          #
####################################################################################################
    
    def addPlot(self):
        p = QStandardItem(self.tr("New plot"))
        _id = QStandardItem(self.getUniqueID())
        importance = QStandardItem(str(0))
        self.appendRow([p, _id, importance, QStandardItem("Persos"), 
                        QStandardItem(), QStandardItem(), QStandardItem("Subplots")])
            
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

####################################################################################################
#                                           SUBPLOTS                                               #
####################################################################################################
        
    def addSubPlot(self):
        index = self.mw.lstPlots.currentPlotIndex()
        if not index.isValid():
            return
        
        parent = index.sibling(index.row(), Plot.subplots.value)
        parentItem = self.item(index.row(), Plot.subplots.value)
        
        if not parentItem:
            return
        
        p = QStandardItem(self.tr("New subplot"))
        _id = QStandardItem(self.getUniqueID(parent))
        summary = QStandardItem()
        
        # Don't know why, if summary is in third position, then drag/drop deletes it...
        parentItem.appendRow([p, _id, QStandardItem(), summary])
    
    def removeSubPlot(self):
        index = self.mw.lstSubPlots.currentIndex()
        if not index.isValid():
            return
        parent = index.parent()
        parentItem = self.itemFromIndex(parent)
        parentItem.takeRow(index.row())
    
    def flags(self, index):
        parent = index.parent()
        if parent.isValid(): # this is a subitem
            return  Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
        else:
            return QStandardItemModel.flags(self, index)
        
####################################################################################################
#                                         PLOT PERSOS                                              #
####################################################################################################
        
    def addPlotPerso(self, v):
        index = self.mw.lstPlots.currentPlotIndex()
        if index.isValid():
            if not self.item(index.row(), Plot.persos.value):
                self.setItem(index.row(), Plot.persos.value, QStandardItem())
                
            item = self.item(index.row(), Plot.persos.value)
            
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

####################################################################################################
#                                   PROXY MODEL (UNUSED)                                           #
####################################################################################################
        
    def viewModel(self):
        "Returns proxy model if any, else self"
        if self._proxy:
            return self._proxy
        else:
            return self
    
    def toSource(self, index):
        if self._proxy:
            return self._proxy.mapToSource(index)
        else:
            return index