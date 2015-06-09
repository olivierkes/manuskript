#!/usr/bin/env python
#--!-- coding: utf8 --!--
 



from qt import *
from enums import *

class cmbOutlineLabelChoser(QComboBox):
    
    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        self.activated[int].connect(self.changed)
        self.currentModelIndex = None
        
    def setModels(self, mdlLabels, mdlOutline):
        self.mdlLabels = mdlLabels
        self.mdlLabels.dataChanged.connect(self.updateItems)
        self.mdlOutline = mdlOutline
        self.mdlOutline.dataChanged.connect(self.updateSelectedItem)
        self.updateItems()
        
    def updateSelectedItem(self, idx1=None, idx2=None):
        if not self.currentModelIndex or not self.currentModelIndex.isValid():
            self.setCurrentIndex(0)
        else:
            val = self.currentModelIndex.internalPointer().data(Outline.label.value)
            if not val: val = 0
            self.setCurrentIndex(int(val))
        
    def changed(self, idx):
        if self.currentModelIndex:
            modelIndex = self.mdlOutline.index(self.currentModelIndex.row(), Outline.label.value, self.currentModelIndex.parent())
            self.mdlOutline.setData(modelIndex, self.currentIndex())
        
    def setCurrentModelIndex(self, idx):
        self.currentModelIndex = idx
        self.updateSelectedItem()
        
    def updateItems(self):
        self.clear()
        for i in range(self.mdlLabels.rowCount()):
            self.addItem(self.mdlLabels.item(i, 0).icon(),
                        self.mdlLabels.item(i, 0).text())
            
        if self.currentModelIndex:
            self.updateSelectedItem()