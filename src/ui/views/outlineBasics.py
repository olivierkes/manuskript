#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from functions import *
from models.outlineModel import *

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
            
            self.menu = QMenu()
            
            # Add / remove items
            self.actAddFolder = QAction(QIcon.fromTheme("folder-new"), qApp.translate("outlineBasics", "New Folder"), self.menu)
            self.actAddFolder.triggered.connect(self.addFolder)
            self.menu.addAction(self.actAddFolder)
            
            self.actAddScene = QAction(QIcon.fromTheme("document-new"), qApp.translate("outlineBasics", "New Scene"), self.menu)
            self.actAddScene.triggered.connect(self.addScene)
            self.menu.addAction(self.actAddScene)
            
            self.actDelete = QAction(QIcon.fromTheme("edit-delete"), qApp.translate("outlineBasics", "Delete"), self.menu)
            self.actDelete.triggered.connect(self.delete)
            self.menu.addAction(self.actDelete)
            
            self.menu.addSeparator()
            
            # Copy, cut, paste
            self.actCopy = QAction(QIcon.fromTheme("edit-copy"), qApp.translate("outlineBasics", "Copy"), self.menu)
            self.actCopy.triggered.connect(self.copy)
            self.menu.addAction(self.actCopy)
            
            self.actCut = QAction(QIcon.fromTheme("edit-cut"), qApp.translate("outlineBasics", "Cut"), self.menu)
            self.actCut.triggered.connect(self.cut)
            self.menu.addAction(self.actCut)
            
            self.actPaste = QAction(QIcon.fromTheme("edit-paste"), qApp.translate("outlineBasics", "Paste"), self.menu)
            self.actPaste.triggered.connect(self.paste)
            self.menu.addAction(self.actPaste)
            
            self.menu.addSeparator()
                
            self.menuPOV = QMenu(qApp.translate("outlineBasics", "Set POV"), self.menu)
            mw = mainWindow()
            a = QAction(QIcon.fromTheme("edit-delete"), qApp.translate("outlineBasics", "None"), self.menuPOV)
            a.triggered.connect(lambda: self.setPOV(""))
            self.menuPOV.addAction(a)
            self.menuPOV.addSeparator()
            
            mpr = QSignalMapper(self.menuPOV)
            for i in range(mw.mdlPersos.rowCount()):
                a = QAction(mw.mdlPersos.item(i, Perso.name.value).text(), self.menuPOV)
                a.triggered.connect(mpr.map)
                mpr.setMapping(a, int(mw.mdlPersos.item(i, Perso.ID.value).text()))
                self.menuPOV.addAction(a)
            mpr.mapped.connect(self.setPOV)
            self.menu.addMenu(self.menuPOV)
            
            
            self.menuStatus = QMenu(qApp.translate("outlineBasics", "Set Status"), self.menu)
            if self.model():
                a = QAction(QIcon.fromTheme("edit-delete"), qApp.translate("outlineBasics", "None"), self.menuStatus)
                a.triggered.connect(lambda: self.setStatus(""))
                self.menuStatus.addAction(a)
                self.menuStatus.addSeparator()
                
                mpr = QSignalMapper(self.menuStatus)
                for status in self.model().statuses:
                    a = QAction(status, self.menuStatus)
                    a.triggered.connect(mpr.map)
                    mpr.setMapping(a, status)
                    self.menuStatus.addAction(a)
                mpr.mapped[str].connect(self.setStatus)
            
            self.menu.addMenu(self.menuStatus)
            
            
            self.menuLabel = QMenu(qApp.translate("outlineBasics", "Set Label"), self.menu)
            mpr = QSignalMapper(self.menuLabel)
            for i in range(mw.mdlLabels.rowCount()):
                a = QAction(mw.mdlLabels.item(i, 0).icon(),
                            mw.mdlLabels.item(i, 0).text(), 
                            self.menuLabel)
                a.triggered.connect(mpr.map)
                mpr.setMapping(a, i)
                self.menuLabel.addAction(a)
            mpr.mapped.connect(self.setLabel)
            self.menu.addMenu(self.menuLabel)
            
            self.menu.popup(event.globalPos())
            
            if len(sel) > 0 and index.isValid() and not index.internalPointer().isFolder() \
                or not clipboard.mimeData().hasFormat("application/xml"):
                self.actPaste.setEnabled(False)
                self.actAddFolder.setEnabled(False)
                self.actAddScene.setEnabled(False)
            
            if len(sel) == 0:
                self.actCopy.setEnabled(False)
                self.actCut.setEnabled(False)
                self.actDelete.setEnabled(False)
                self.menuPOV.setEnabled(False)
                self.menuStatus.setEnabled(False)
                self.menuLabel.setEnabled(False)
            
    def addFolder(self):
        self.addItem("folder")
        
    def addScene(self):
        self.addItem("scene")
        
    def addItem(self, type="folder"):
        if len(self.selectedIndexes()) == 0:
            parent = self.rootIndex()
        else:
            parent = self.currentIndex()
            
        item = outlineItem(title=qApp.translate("outlineBasics", "New"), type=type)
        self.model().appendItem(item, parent)
            
    def copy(self):
        mimeData = self.model().mimeData(self.selectionModel().selectedIndexes())
        qApp.clipboard().setMimeData(mimeData)
        
    def paste(self):
        index = self.currentIndex()
        if len(self.getSelection()) == 0:
            index = self.rootIndex()
        data = qApp.clipboard().mimeData()
        self.model().dropMimeData(data, Qt.CopyAction, -1, 0, index)
        
    def cut(self):
        self.copy()
        self.delete()
            
    def delete(self):
        for i in self.getSelection():
            self.model().removeIndex(i)
            
    def setPOV(self, POV):
        for i in self.getSelection():
            self.model().setData(i.sibling(i.row(), Outline.POV.value), str(POV))
    
    def setStatus(self, status):
        for i in self.getSelection():
            self.model().setData(i.sibling(i.row(), Outline.status.value), str(status))
    
    def setLabel(self, label):
        for i in self.getSelection():
            self.model().setData(i.sibling(i.row(), Outline.label.value), str(label))