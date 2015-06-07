#!/usr/bin/env python
#--!-- coding: utf8 --!--
 



from qt import *
from enums import *

class cmbOutlinePersoChoser(QComboBox):
    
    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        self.activated[int].connect(self.changed)
        self.currentModelIndex = None
        
    def setModels(self, mdlPersos, mdlOutline):
        self.mdlPersos = mdlPersos
        self.mdlPersos.dataChanged.connect(self.updateItems)
        self.mdlOutline = mdlOutline
        self.mdlOutline.dataChanged.connect(self.updateSelectedItem)
        
    def updateSelectedItem(self, idx1=None, idx2=None):
        if not self.currentModelIndex or not self.currentModelIndex.isValid():
            self.setCurrentIndex(0)
        else:
            item = self.currentModelIndex.internalPointer()
            POV = item.data(Outline.POV.value)
            idx = self.findData(POV)
            if idx != -1:
                self.setCurrentIndex(idx)
            else:
                self.setCurrentIndex(0)
        
    def changed(self, idx):
        if self.currentModelIndex:
            modelIndex = self.mdlOutline.index(self.currentModelIndex.row(), Outline.POV.value, self.currentModelIndex.parent())
            self.mdlOutline.setData(modelIndex, self.currentData())
        
    def setCurrentModelIndex(self, idx):
        self.currentModelIndex = idx
        self.updateSelectedItem()
        
    def updateItems(self):
        self.clear()
        self.addItem("")
        for i in range(self.mdlPersos.rowCount()):
            try:
                self.addItem(self.mdlPersos.item(i, Perso.name.value).text(), self.mdlPersos.item(i, Perso.ID.value).text())
                self.setItemData(i+1, self.mdlPersos.item(i, Perso.name.value).text(), Qt.ToolTipRole)
            except:
                pass
        if self.currentModelIndex:
            self.updateSelectedItem()