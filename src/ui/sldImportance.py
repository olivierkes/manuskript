#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from __future__ import print_function
from __future__ import unicode_literals

from qt import *

from ui.sldImportance_ui import *

class sldImportance(QWidget, Ui_sldImportance):
    
    importanceChanged = pyqtSignal(str)
    
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.setupUi(self)
        
        self.lastValue = -1
        self.sld.valueChanged.connect(self.changed)
        self.setValue(0)
        
    def getImportance(self):
        return str(self.sld.value())
        
    def changed(self, v):
        val = [
            "Mineur",
            "Secondaire",
            "Principal",
            ]
        self.lbl.setText(val[v])
        
        self.importanceChanged.emit(str(v))
        
    def setValue(self, v):
        if v <> self.lastValue:    
            self.sld.setValue(int(v) if v else 0)
            self.changed(int(v) if v else 0)
            self.lastValue = v
        
    def setProperty():
        pass
        
    importance = pyqtProperty(str, fget=getImportance, fset=setValue, notify=importanceChanged)