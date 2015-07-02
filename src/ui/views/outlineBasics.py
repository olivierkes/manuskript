#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from functions import *
from models.outlineModel import *
import settings

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
            self.menu = self.makePopupMenu()
            self.menu.popup(event.globalPos())
        else:
            QAbstractItemView.mouseReleaseEvent(self, event)
        
    def makePopupMenu(self):
        index = self.currentIndex()
        sel = self.getSelection()
        clipboard = qApp.clipboard()
        
        menu = QMenu(self)
        
        # Add / remove items
        self.actAddFolder = QAction(QIcon.fromTheme("folder-new"), qApp.translate("outlineBasics", "New Folder"), menu)
        self.actAddFolder.triggered.connect(self.addFolder)
        menu.addAction(self.actAddFolder)
        
        self.actAddText = QAction(QIcon.fromTheme("document-new"), qApp.translate("outlineBasics", "New Text"), menu)
        self.actAddText.triggered.connect(self.addText)
        menu.addAction(self.actAddText)
        
        self.actDelete = QAction(QIcon.fromTheme("edit-delete"), qApp.translate("outlineBasics", "Delete"), menu)
        self.actDelete.triggered.connect(self.delete)
        menu.addAction(self.actDelete)
        
        menu.addSeparator()
        
        # Copy, cut, paste
        self.actCopy = QAction(QIcon.fromTheme("edit-copy"), qApp.translate("outlineBasics", "Copy"), menu)
        self.actCopy.triggered.connect(self.copy)
        menu.addAction(self.actCopy)
        
        self.actCut = QAction(QIcon.fromTheme("edit-cut"), qApp.translate("outlineBasics", "Cut"), menu)
        self.actCut.triggered.connect(self.cut)
        menu.addAction(self.actCut)
        
        self.actPaste = QAction(QIcon.fromTheme("edit-paste"), qApp.translate("outlineBasics", "Paste"), menu)
        self.actPaste.triggered.connect(self.paste)
        menu.addAction(self.actPaste)
        
        menu.addSeparator()
            
        # POV
        self.menuPOV = QMenu(qApp.translate("outlineBasics", "Set POV"), menu)
        mw = mainWindow()
        a = QAction(QIcon.fromTheme("edit-delete"), qApp.translate("outlineBasics", "None"), self.menuPOV)
        a.triggered.connect(lambda: self.setPOV(""))
        self.menuPOV.addAction(a)
        self.menuPOV.addSeparator()
        
        menus = []
        for i in [self.tr("Main"), self.tr("Secondary"), self.tr("Minor")]:
            m = QMenu(i, self.menuPOV)
            menus.append(m)
            self.menuPOV.addMenu(m)
        
        mpr = QSignalMapper(self.menuPOV)
        for i in range(mw.mdlPersos.rowCount()):
            a = QAction(mw.mdlPersos.icon(i), mw.mdlPersos.name(i), self.menuPOV)
            a.triggered.connect(mpr.map)
            mpr.setMapping(a, int(mw.mdlPersos.ID(i)))
            
            imp = toInt(mw.mdlPersos.importance(i))
            
            menus[2-imp].addAction(a)
            
        mpr.mapped.connect(self.setPOV)
        menu.addMenu(self.menuPOV)
        
        # Status
        self.menuStatus = QMenu(qApp.translate("outlineBasics", "Set Status"), menu)
            #a = QAction(QIcon.fromTheme("edit-delete"), qApp.translate("outlineBasics", "None"), self.menuStatus)
            #a.triggered.connect(lambda: self.setStatus(""))
            #self.menuStatus.addAction(a)
            #self.menuStatus.addSeparator()
            
        mpr = QSignalMapper(self.menuStatus)
        for i in range(mw.mdlStatus.rowCount()):
            a = QAction(mw.mdlStatus.item(i, 0).text(), self.menuStatus)
            a.triggered.connect(mpr.map)
            mpr.setMapping(a, i)
            self.menuStatus.addAction(a)
        mpr.mapped.connect(self.setStatus)
        menu.addMenu(self.menuStatus)
        
        # Labels
        self.menuLabel = QMenu(qApp.translate("outlineBasics", "Set Label"), menu)
        mpr = QSignalMapper(self.menuLabel)
        for i in range(mw.mdlLabels.rowCount()):
            a = QAction(mw.mdlLabels.item(i, 0).icon(),
                        mw.mdlLabels.item(i, 0).text(), 
                        self.menuLabel)
            a.triggered.connect(mpr.map)
            mpr.setMapping(a, i)
            self.menuLabel.addAction(a)
        mpr.mapped.connect(self.setLabel)
        menu.addMenu(self.menuLabel)
        
        
        if len(sel) > 0 and index.isValid() and not index.internalPointer().isFolder() \
            or not clipboard.mimeData().hasFormat("application/xml"):
            self.actPaste.setEnabled(False)
            
        if len(sel) > 0 and index.isValid() and not index.internalPointer().isFolder():
            self.actAddFolder.setEnabled(False)
            self.actAddText.setEnabled(False)
        
        if len(sel) == 0:
            self.actCopy.setEnabled(False)
            self.actCut.setEnabled(False)
            self.actDelete.setEnabled(False)
            self.menuPOV.setEnabled(False)
            self.menuStatus.setEnabled(False)
            self.menuLabel.setEnabled(False)
            
        return menu
            
    def addFolder(self):
        self.addItem("folder")
        
    def addText(self):
        self.addItem("text")
        
    def addItem(self, _type="folder"):
        if len(self.selectedIndexes()) == 0:
            parent = self.rootIndex()
        else:
            parent = self.currentIndex()
        
        if _type == "text":
            _type = settings.defaultTextType
            
        item = outlineItem(title=qApp.translate("outlineBasics", "New"), _type=_type)
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
        self.model().removeIndexes(self.getSelection())
            
    def setPOV(self, POV):
        for i in self.getSelection():
            self.model().setData(i.sibling(i.row(), Outline.POV.value), str(POV))
    
    def setStatus(self, status):
        for i in self.getSelection():
            self.model().setData(i.sibling(i.row(), Outline.status.value), str(status))
    
    def setLabel(self, label):
        for i in self.getSelection():
            self.model().setData(i.sibling(i.row(), Outline.label.value), str(label))