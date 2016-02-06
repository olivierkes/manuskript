#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *


class cmbOutlineTypeChoser(QComboBox):
    
    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        self.activated[int].connect(self.submit)
        self._column = Outline.type.value
        self._index = None
        self._indexes = None
        self._updating = False
        self._various = False
        
    def setModel(self, mdlOutline):
        self.mdlOutline = mdlOutline
        self.mdlOutline.dataChanged.connect(self.update)
        self.updateItems()
        
    def updateItems(self):
        self.clear()
        types = [
            ("t2t", self.tr("Txt2Tags"), "text-x-generic"),
            ("html", self.tr("Rich Text (html)"), "text-html"),
            ("txt", self.tr("Plain Text"), "text-x-generic"),
            ]
        for t in types:
            self.addItem(QIcon.fromTheme(t[2]), t[1], t[0])
            
        self._various = False
            
        if self._index or self._indexes:
            self.updateSelectedItem()
        
    def setCurrentModelIndex(self, index):
        self._indexes = None
        if index.column() != self._column:
            index = index.sibling(index.row(), self._column)
        self._index = index
        # Disabled if item type is not text
        self.setEnabled(index.internalPointer().type() in ["t2t", "html", "txt"])
        self.updateItems()
        self.updateSelectedItem()
            
    def setCurrentModelIndexes(self, indexes):
        self._indexes = []
        self._index = None
        
        hasText = False
        for i in indexes:
            if i.isValid():
                if i.column() != self._column:
                    i = i.sibling(i.row(), self._column)
                self._indexes.append(i)
                if i.internalPointer().type() in ["t2t", "html", "txt"]:
                    hasText = True
        
        self.setEnabled(hasText)
        
        self.updateItems()
        self.updateSelectedItem()
        
    def update(self, topLeft, bottomRight):
        
        if self._updating:
            # We are currently putting data in the model, so no updates
            return
        
        if self._index:
            if topLeft.row() <= self._index.row() <= bottomRight.row():
                self.updateSelectedItem()
                
        elif self._indexes:
            update = False
            for i in self._indexes:
                if topLeft.row() <= i.row() <= bottomRight.row():
                    update = True
            if update:
                self.updateSelectedItem()
        
    def getType(self, index):
        item = index.internalPointer()
        return item.type()
        
    def updateSelectedItem(self):
        
        if self._updating:
            return
        
        if self._index:
            _type = self.getType(self._index)
            i = self.findData(_type)
            if i != -1:
                self.setCurrentIndex(i)
                
        elif self._indexes:
            types = []
            same = True
            
            for i in self._indexes:
                types.append(self.getType(i))
                
            for t in types[1:]:
                if t != types[0]:
                    same = False
                    break
            
            if same:
                self._various = False
                i = self.findData(types[0])
                if i != -1:
                    self.setCurrentIndex(i)
                
            else:
                if not self._various:
                    self.insertItem(0, self.tr("Various"))
                    f = self.font()
                    f.setItalic(True)
                    self.setItemData(0, f, Qt.FontRole)
                    self.setItemData(0, QBrush(Qt.darkGray), Qt.ForegroundRole)
                self._various = True
                self.setCurrentIndex(0)
        
        else:
            self.setCurrentIndex(0)
        
    def submit(self, idx):
        if self._index:
            self.mdlOutline.setData(self._index, self.currentData())
            
        elif self._indexes:
            value = self.currentData()
            
            if self._various and self.currentIndex() == 0:
                return
                
            self._updating = True
            for i in self._indexes:
                self.mdlOutline.setData(i, value)
            self._updating = False