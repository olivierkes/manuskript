#!/usr/bin/env python
#--!-- coding: utf8 --!--
 



from qt import *
from enums import *
from functions import *

class dndView(QAbstractItemView):
    
    def __init__(self, parent=None):
        QAbstractItemView.__init__(self, parent)
        self.setDragDropMode(self.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(self.ExtendedSelection)
        
    def dragMoveEvent(self, event):
        #return QAbstractItemView.dragMoveEvent(self, event)
        #print(a)
        if event.keyboardModifiers() & Qt.ControlModifier:
            event.setDropAction(Qt.CopyAction)
        else:
            event.setDropAction(Qt.MoveAction)