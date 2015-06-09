#!/usr/bin/env python
#--!-- coding: utf8 --!--
 



from qt import *
from enums import *
from functions import *
from ui.views.dndView import *

class treeView(QTreeView, dndView):
    
    def __init__(self, parent=None):
        QTreeView.__init__(self, parent)
        dndView.__init__(self, parent)
        
        
    def setModel(self, model):
        QTreeView.setModel(self, model)
        
        # Hiding columns
        for c in range(1, self.model().columnCount()):
            self.hideColumn(c)
        
    def dragMoveEvent(self, event):
        dndView.dragMoveEvent(self, event)
        QTreeView.dragMoveEvent(self, event)