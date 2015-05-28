#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from __future__ import print_function
from __future__ import unicode_literals

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui.sldImportance_ui import *

class sldImportance(QWidget, Ui_sldImportance):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.setupUi(self)
        
        self.sld.valueChanged.connect(self.changed)
        self.setValue(0)
        
    def changed(self, v):
        val = [
            "Principal",
            "Secondaire",
            "Mineur"
            ]
        self.lbl.setText(val[v])
        
    def setValue(self, v):
        self.sld.setValue(v)
        self.changed(v)
        