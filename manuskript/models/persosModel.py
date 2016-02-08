#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QPixmap, QIcon
from PyQt5.QtWidgets import QColorDialog

from manuskript.enums import Perso
from manuskript.enums import Plot
from manuskript.functions import iconColor
from manuskript.functions import mainWindow
from manuskript.functions import randomColor
from manuskript.functions import toInt


class persosModel(QStandardItemModel):
    
    def __init__(self, parent):
        QStandardItemModel.__init__(self, 0, 3, parent)
        self.setHorizontalHeaderLabels([i.name for i in Perso])
        self.mw = mainWindow()
        # self._proxy = plotsProxyModel()
        # self._proxy.setSourceModel(self)

###############################################################################
# PERSOS QUERRIES
###############################################################################

    def name(self, row):
        return self.item(row, Perso.name.value).text()
    
    def icon(self, row):
        return self.item(row, Perso.name.value).icon()
    
    def ID(self, row):
        return self.item(row, Perso.ID.value).text()
    
    def importance(self, row):
        return self.item(row, Perso.importance.value).text()

###############################################################################
# MODEL QUERRIES
###############################################################################

    def getPersosByImportance(self):
        persos = [[], [], []]
        for i in range(self.rowCount()):
            importance = self.item(i, Perso.importance.value).text()
            ID = self.item(i, Perso.ID.value).text()
            persos[2-toInt(importance)].append(ID)
        return persos
    
    def getPersoNameByID(self, ID):
        index = self.getIndexFromID(ID)
        if index.isValid():
            return self.name(index.row())
        return ""
    
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
        self.colorDialog = QColorDialog(color, self.mw)
        color = self.colorDialog.getColor(color)
        if color.isValid():
            self.setPersoColor(item, color)
            self.updatePersoColor(idx)

###############################################################################
# UI
###############################################################################

    def updatePersoColor(self, idx):
        # idx = self.currentPersoIndex()
        color = self.getPersoColorName(idx)
        self.mw.btnPersoColor.setStyleSheet("background:{};".format(color))
        
###############################################################################
# PERSO INFOS
###############################################################################

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == Perso.infoName.value:
                return self.tr("Name")
            elif section == Perso.infoData.value:
                return self.tr("Value")
            else:
                return Perso(section).name
        else:
            return QStandardItemModel.headerData(self, section, orientation, role)

    def addPersoInfo(self):
        perso = self.itemFromIndex(self.currentPersoIndex())
        row = perso.rowCount()
        perso.setChild(row, Perso.infoName.value, QStandardItem(""))
        perso.setChild(row, Perso.infoData.value, QStandardItem(""))
        
        self.mw.updatePersoInfoView()
        
    def removePersoInfo(self):
        perso = self.itemFromIndex(self.currentPersoIndex())
        
        rm = []
        for idx in self.mw.tblPersoInfos.selectedIndexes():
            if not idx.row() in rm:
                rm.append(idx.row())
        
        rm.sort()
        rm.reverse()
        for r in rm:
            perso.takeRow(r)
            
    def listPersoInfos(self, index):
        infos = []
        for i in range(self.rowCount(index)):
            name = self.data(index.child(i, Perso.infoName.value))
            val = self.data(index.child(i, Perso.infoData.value))
            infos.append((name, val))
            
        return infos
