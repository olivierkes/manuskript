#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from functions import *

class persosModel(QStandardItemModel):
    
    def __init__(self, parent):
        QStandardItemModel.__init__(self, 0, 3, parent)
        self.setHorizontalHeaderLabels([i.name for i in Plot])
        self.mw = mainWindow()
        #self._proxy = plotsProxyModel()
        #self._proxy.setSourceModel(self)

###############################################################################
# QUERRIES
###############################################################################

    def getPersosByImportance(self):
        persos = [[], [], []]
        for i in range(self.rowCount()):
            importance = self.item(i, Perso.importance.value).text()
            ID = self.item(i, Perso.ID.value).text()
            persos[2-toInt(importance)].append(ID)
        return persos
    
    def getPersoNameByID(self, ID):
        for i in range(self.rowCount()):
            _ID = self.item(i, Perso.ID.value).text()
            if _ID == ID or toInt(_ID) == ID:
                name = self.item(i, Perso.name.value).text()
                return name
        return None
    
    def getIndexFromID(self, ID):
        for i in range(self.rowCount()):
            _ID = self.item(i, Perso.ID.value).text()
            if _ID == ID or toInt(_ID) == ID:
                return self.index(i, 0)
        return QModelIndex()
    
    def getPersoColorByID(self, ID):
        idx = self.getIndexFromID(ID)
        return self.getPersoColorName(idx)
    
    def getPersoColorName(self, index):
        icon = self.item(index.row()).icon()
        return iconColor(icon).name() if icon else ""
        
    def currentListIndex(self):
        i = self.mw.lstPersos.currentIndex()
        if i .isValid():
            return i
        else:
            return None
        
    def currentPersoIndex(self):
        return self.mw.lstPersos.currentPersoIndex()

###############################################################################
# ADDING / REMOVING
###############################################################################
    
    def addPerso(self):
        """Creates a perso by adding a row in mdlPersos
        and a column in mdlPersosInfos with same ID"""
        p = QStandardItem(self.tr("New character"))
        self.setPersoColor(p, randomColor(QColor(Qt.white)))
        pid = self.getUniqueID()
        self.appendRow([p, QStandardItem(pid), QStandardItem("0")])
            
    def getUniqueID(self, parent=QModelIndex()):
        """Returns an unused perso ID (row 1)."""
        vals = []
        for i in range(self.rowCount(parent)):
            index = self.index(i, Perso.ID.value, parent)
            if index.isValid() and index.data():
                vals.append(int(index.data()))

        k = 0
        while k in vals:
            k += 1
        return str(k)
        
    def removePerso(self):
        index = self.currentPersoIndex()
        self.takeRow(index.row())
        
    def setPersoColor(self, item, color):
        px = QPixmap(32, 32)
        px.fill(color)
        item.setIcon(QIcon(px))
        
    def chosePersoColor(self):
        idx = self.currentPersoIndex()
        item = self.item(idx.row(), Perso.name.value)
        if item:
            color = iconColor(item.icon())
        else:
            color = Qt.white
        self.colorDialog = QColorDialog(color, self)
        color = self.colorDialog.getColor(color)
        if color.isValid():
            self.setPersoColor(item, color)
            self.updatePersoColor(idx)

###############################################################################
# UI
###############################################################################

    def updatePersoColor(self, idx):
        #idx = self.currentPersoIndex()
        color = self.getPersoColorName(idx)
        self.mw.btnPersoColor.setStyleSheet("background:{};".format(color))
        
        
###############################################################################
# PERSO INFOS
###############################################################################

    def addPersoInfo(self):
        #FIXME
        pass
