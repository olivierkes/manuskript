#!/usr/bin/env python
#--!-- coding: utf8 --!--
 



from qt import *
from enums import *

class cmbOutlineStatusChoser(QComboBox):
    
    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        self.activated[int].connect(self.changed)
        self.currentModelIndex = None
        
    def setModels(self, mdlStatus, mdlOutline):
        self.mdlStatus = mdlStatus
        self.mdlStatus.dataChanged.connect(self.updateItems)  # Not emiting?
        self.mdlOutline = mdlOutline
        self.mdlOutline.dataChanged.connect(self.updateSelectedItem)
        self.updateItems()
        
    def updateSelectedItem(self, idx1=None, idx2=None):
        if not self.currentModelIndex or not self.currentModelIndex.isValid():
            self.setCurrentIndex(0)
        else:
            val = self.currentModelIndex.internalPointer().data(Outline.status.value)
            if not val: val = 0
            try:
                self.setCurrentIndex(int(val))
            except:
                pass
        
    def changed(self, idx):
        if self.currentModelIndex:
            modelIndex = self.mdlOutline.index(self.currentModelIndex.row(), Outline.status.value, self.currentModelIndex.parent())
            self.mdlOutline.setData(modelIndex, self.currentIndex())
        
    def setCurrentModelIndex(self, idx):
        self.currentModelIndex = idx
        self.updateItems()
        self.updateSelectedItem()
        
    def updateItems(self, topLeft=None, bottomRight=None, roles=None):
        self.clear()
        for i in range(self.mdlStatus.rowCount()):
            item = self.mdlStatus.item(i, 0)
            if item:
                self.addItem(item.text())
            
        if self.currentModelIndex:
            self.updateSelectedItem()