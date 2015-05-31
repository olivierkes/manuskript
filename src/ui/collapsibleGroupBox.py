#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from __future__ import print_function
from __future__ import unicode_literals

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class collapsibleGroupBox(QGroupBox):
    
    def __init__(self, parent=None):
        QGroupBox.__init__(self)
        
        self.toggled.connect(self.setExpanded)
        self.tempWidget = QWidget()
    
    def setExpanded(self, val):
        self.setCollapsed(not val)
        
    def setCollapsed(self, val):
        if val:
            # Save layout
            self.tempWidget.setLayout(self.layout())
            # Set empty layout
            l = QVBoxLayout()
            #print(l.contentsMargins().left(), l.contentsMargins().bottom(), l.contentsMargins().top(), )
            l.setContentsMargins(0, 0, 0, 0)
            self.setLayout(l)
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        else:
            # Delete layout
            QWidget().setLayout(self.layout())
            # Set saved layout
            self.setLayout(self.tempWidget.layout())
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)