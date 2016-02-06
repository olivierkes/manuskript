#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from functions import *
from ui.sldImportance_ui import *

class sldImportance(QWidget, Ui_sldImportance):
    
    importanceChanged = pyqtSignal(str)
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self._column = 0
        self._updating = False
        self._index = None
        
        self.lastValue = -1
        self.sld.valueChanged.connect(self.changed)
        self.setValue(0)
        
    def getImportance(self):
        return str(self.sld.value())
        
    def changed(self, v):
        val = [
            self.tr("Minor"),
            self.tr("Secondary"),
            self.tr("Main"),
            ]
        self.lbl.setText(val[v])
        
        self.importanceChanged.emit(str(v))
        
        if self._index and not self._updating:
            if str(v) != self._model.data(self._index):
                self._updating = True
                self._model.setData(self._index, str(v))
                self._updating = False
        
    def setValue(self, v):
        if v != self.lastValue:    
            self.sld.setValue(int(v) if v else 0)
            self.changed(int(v) if v else 0)
            self.lastValue = v
        
    def setProperty():
        pass
    
    # MODEL / VIEW
    
    def setColumn(self, column):
        self._column = column
    
    def setModel(self, model):
        self._model = model
        self._model.dataChanged.connect(self.update)
        
    def update(self, topLeft, bottomRight):
        
        if self._updating:
            return
        
        if self._index:
            if topLeft.row() <= self._index.row() <= bottomRight.row():
                self.updateValue()
        
    def setCurrentModelIndex(self, index):
        if index.isValid():
            if index.column() != self._column:
                index = index.sibling(index.row(), self._column)
            self._index = index
            
            self.updateValue()
            
    def updateValue(self):
        if self._index:
            val = toInt(self._model.data(self._index))
            if self.sld.value() != val:
                self._updating = True
                self.setValue(val)
                self._updating = False
        
        
    importance = pyqtProperty(str, fget=getImportance, fset=setValue, notify=importanceChanged)