#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from __future__ import print_function
from __future__ import unicode_literals

from qt import *
from enums import *

class cmbPersoChoser(QComboBox):
    
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
        if not self.currentModelIndex:
            self.setCurrentIndex(0)
        else:
            item = self.currentModelIndex.internalPointer()
            POV = item.data(Outline.POV)
            idx = self.findData(POV)
            if idx <> -1:
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
            except:
                pass
        if self.currentModelIndex:
            self.updateSelectedItem()
            
    #def setPOV(self, POV):
        #idx = self.findData(POV)
        #if idx <> -1:
            #self.setCurrentIndex(idx)
        #else:
            #self.setCurrentIndex(0)
            #print("cmbPersoChoser: POV {} not found.".format(POV))
        
    #def getPOV(self):
        #print("Getting data")
        #return self.currentData()