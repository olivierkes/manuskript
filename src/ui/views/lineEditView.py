#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from functions import *

class lineEditView(QLineEdit):
    
    def __init__(self, parent=None):
        QLineEdit.__init__(self, parent)
        self._column = Outline.title.value
        self._indexes = None
        self._index = None
        self._placeholderText = None
        self._updating = False
        
    def setModel(self, model):
        self._model = model
        
    def setColumn(self, col):
        self._column = col
        
    def setCurrentModelIndex(self, index):
        self._indexes = None
        if index.isValid():
            if index.column() != self._column:
                index = index.sibling(index.row(), self._column)
            self._index = index
            self.item = index.internalPointer()
            if self._placeholderText != None:
                self.setPlaceholderText(self._placeholderText)
            self.textEdited.connect(self.submit)
            self._model.dataChanged.connect(self.update)
            self.updateText()
            
    def setCurrentModelIndexes(self, indexes):
        self._indexes = []
        self._index = None
        
        for i in indexes:
            if i.isValid():
                if i.column() != self._column:
                    i = i.sibling(i.row(), self._column)
                self._indexes.append(i)
        
        self.textEdited.connect(self.submit)
        self._model.dataChanged.connect(self.update)
        self.updateText()
        
    def submit(self):
        if self._index:
            item = self._index.internalPointer()
            if self.text() != item.data(self._column):
                self._model.setData(self._index, self.text())
                
        elif self._indexes:
            self._updating = True
            for i in self._indexes:
                item = i.internalPointer()
                if self.text() != item.data(self._column):
                    self._model.setData(i, self.text())
            self._updating = False
        
    def update(self, topLeft, bottomRight):
        
        if self._updating:
            # We are currently putting data in the model, so no updates
            return
        
        if self._index:
            if topLeft.row() <= self._index.row() <= bottomRight.row():
                self.updateText()
                
        elif self._indexes:
            update = False
            for i in self._indexes:
                if topLeft.row() <= i.row() <= bottomRight.row():
                    update = True
            if update:
                self.updateText()
            
    def updateText(self):
        
        if self._index:
            item = self._index.internalPointer()
            txt = toString(item.data(self._column))
            if self.text() != txt:
                self.setText(txt)
        
        elif self._indexes:
            t = []
            same = True
            for i in self._indexes:
                item = i.internalPointer()
                t.append(str(item.data(self._column)))
                
            for t2 in t[1:]:
                if t2 != t[0]:
                    same = False
            
            if same:
                self.setText(t[0])
            else:
                self.setText("")
                self._placeholderText = self.placeholderText()
                self.setPlaceholderText("Various")
                