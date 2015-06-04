#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from __future__ import print_function
from __future__ import unicode_literals

from qt import *
from enums import *

class cmbOutlineStatusChoser(QComboBox):
    
    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        self.activated[int].connect(self.changed)
        self.currentModelIndex = None
        self.setEditable(True)
        self.setAutoFillBackground(True)
        
    def setModel(self, mdlOutline):
        self.mdlOutline = mdlOutline
        self.mdlOutline.dataChanged.connect(self.updateItems)
        self.mdlOutline.dataChanged.connect(self.updateSelectedItem)
        self.mdlOutline.newStatuses.connect(self.updateItems)
        self.updateItems()
        
    def updateSelectedItem(self, idx1=None, idx2=None):
        if not self.currentModelIndex:
            self.setCurrentIndex(0)
        else:
            item = self.currentModelIndex.internalPointer()
            self.setCurrentIndex(self.findText(item.data(Outline.status.value)))
        
    def changed(self, idx):
        if self.currentModelIndex:
            modelIndex = self.mdlOutline.index(self.currentModelIndex.row(), Outline.status.value, self.currentModelIndex.parent())
            self.mdlOutline.setData(modelIndex, self.currentText())
        
    def setCurrentModelIndex(self, idx):
        self.currentModelIndex = idx
        self.updateSelectedItem()
        
    def updateItems(self):
        
        self.clear()
        
        self.addItem("")
        
        for status in self.mdlOutline.statuses:
            self.addItem(status)
            
        if self.currentModelIndex:
            self.updateSelectedItem()