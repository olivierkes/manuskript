#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from __future__ import print_function
from __future__ import unicode_literals

from qt import *
from enums import *

# Because I have trouble with QDataWidgetMapper and the checkbox, I don't know why.

class chkOutlineCompile(QCheckBox):
    
    def __init__(self, parent=None):
        QCheckBox.__init__(self, parent)
        self.stateChanged.connect(self.changed)
        self.currentModelIndex = None
        
    def setModel(self, mdlOutline):
        self.mdlOutline = mdlOutline
        self.mdlOutline.dataChanged.connect(self.updateSelectedItem)
        
    def setCurrentModelIndex(self, idx):
        self.currentModelIndex = idx
        self.updateSelectedItem()
        
    def updateSelectedItem(self, idx1=None, idx2=None):
        if not self.currentModelIndex or not self.currentModelIndex.isValid():
            self.setChecked(False)
            self.setEnabled(False)
        else:
            self.setEnabled(True)
            item = self.currentModelIndex.internalPointer()
            c = item.data(Outline.compile)
            if c:
                c = int(c)
            else:
                c = Qt.Unchecked
            self.setCheckState(c)
        
    def changed(self, state):
        if self.currentModelIndex and self.currentModelIndex.isValid():
            mdl = self.currentModelIndex.model()
            modelIndex = mdl.index(self.currentModelIndex.row(), Outline.compile.value, self.currentModelIndex.parent())
            mdl.setData(modelIndex, state)