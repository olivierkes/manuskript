#!/usr/bin/env python
#--!-- coding: utf8 --!--
 



from qt import *
from enums import *
from functions import *

class outlineBasics(QAbstractItemView):
    
    def __init__(self, parent=None):
        pass
    
    def getSelection(self):
        sel = []
        for i in self.selectedIndexes():
            if i.column() != 0: continue
            if not i in sel: sel.append(i)
        return sel
    
    def mouseReleaseEvent(self, event):
        
        if event.button() == Qt.RightButton:
            
            index = self.currentIndex()
            sel = self.getSelection()
            clipboard = qApp.clipboard()
            
            # Copy, cut, paste
            self.menu = QMenu()
            self.actCopy = QAction(QIcon.fromTheme("edit-copy"), self.tr("Copy"), self.menu)
            self.actCopy.triggered.connect(self.copy)
            self.menu.addAction(self.actCopy)
            
            self.actCut = QAction(QIcon.fromTheme("edit-cut"), self.tr("Cut"), self.menu)
            self.actCut.triggered.connect(self.cut)
            self.menu.addAction(self.actCut)
            
            self.actPaste = QAction(QIcon.fromTheme("edit-paste"), self.tr("Paste"), self.menu)
            self.actPaste.triggered.connect(self.paste)
            self.menu.addAction(self.actPaste)
            
            self.actDelete = QAction(QIcon.fromTheme("edit-delete"), self.tr("Delete"), self.menu)
            self.actDelete.triggered.connect(self.delete)
            self.menu.addAction(self.actDelete)
            
            self.menu.addSeparator()
            
            if len(sel) > 0 and index.isValid() and not index.internalPointer().isFolder() \
                or not clipboard.mimeData().hasFormat("application/xml"):
                self.actPaste.setEnabled(False)
            
            if len(sel) == 0:
                self.actCopy.setEnabled(False)
                self.actCut.setEnabled(False)
                self.actDelete.setEnabled(False)
                
            
            menuPOV = QMenu(self.tr("Set POV"), self.menu)
            menuPOV.addAction("Not yet")
            self.menu.addMenu(menuPOV)
            
            menuStatus = QMenu(self.tr("Set Status"), self.menu)
            menuStatus.addAction("Not yet")
            self.menu.addMenu(menuStatus)
            
            menuLabel = QMenu(self.tr("Set Label"), self.menu)
            menuLabel.addAction("Not yet")
            self.menu.addMenu(menuLabel)
            
            self.menu.popup(event.globalPos())
            
    def copy(self):
        mimeData = self.model().mimeData(self.selectionModel().selectedIndexes())
        qApp.clipboard().setMimeData(mimeData)
        
    def paste(self):
        index = self.currentIndex()
        if len(self.getSelection()) == 0:
            index = QModelIndex()
        data = qApp.clipboard().mimeData()
        self.model().dropMimeData(data, Qt.CopyAction, -1, 0, index)
        
    def cut(self):
        self.copy()
        self.delete()
            
    def delete(self):
        for i in self.getSelection():
            self.model().removeIndex(i)
        