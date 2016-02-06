#!/usr/bin/env python
#--!-- coding: utf8 --!--
 



from qt import *
from enums import *
from functions import *
from ui.views.dndView import *
from ui.views.outlineBasics import *
from ui.views.treeDelegates import *

class treeView(QTreeView, dndView, outlineBasics):
    
    def __init__(self, parent=None):
        QTreeView.__init__(self, parent)
        dndView.__init__(self, parent)
        outlineBasics.__init__(self, parent)
        self._indexesToOpen = None
        
    def setModel(self, model):
        QTreeView.setModel(self, model)
        
        # Hiding columns
        for c in range(1, self.model().columnCount()):
            self.hideColumn(c)
            
        # Setting delegate
        self.titleDelegate = treeTitleDelegate()
        self.setItemDelegateForColumn(Outline.title.value, self.titleDelegate)
        
    def makePopupMenu(self):
        menu = outlineBasics.makePopupMenu(self)
        first = menu.actions()[0]
        
        # Open item in new tab
        sel = self.selectedIndexes()
        pos = self.viewport().mapFromGlobal(QCursor.pos())
        mouseIndex = self.indexAt(pos)
        
        if mouseIndex.isValid():
            mouseTitle = mouseIndex.internalPointer().title()
        else:
            mouseTitle = self.tr("Root")
        
        if mouseIndex in sel and len(sel) > 1:
            actionTitle = self.tr("Open {} items in new tabs").format(len(sel))
            self._indexesToOpen = sel
        else:
            actionTitle = self.tr("Open {} in a new tab").format(mouseTitle)
            self._indexesToOpen = [mouseIndex]
        
        self.actNewTab = QAction(actionTitle, menu)
        self.actNewTab.triggered.connect(self.openNewTab)
        menu.insertAction(first, self.actNewTab)
        menu.insertSeparator(first)
        
        # Expand /collapse item
        if mouseIndex.isValid():
            #index = self.currentIndex()
            item = mouseIndex.internalPointer()
            self.actExpand = QAction(self.tr("Expand {}").format(item.title()), menu)
            self.actExpand.triggered.connect(self.expandCurrentIndex)
            menu.insertAction(first, self.actExpand)
            
            self.actCollapse = QAction(self.tr("Collapse {}").format(item.title()), menu)
            self.actCollapse.triggered.connect(self.collapseCurrentIndex)
            menu.insertAction(first, self.actCollapse)
            
            menu.insertSeparator(first)
        
        # Expand /collapse all
        self.actExpandAll = QAction(self.tr("Expand All"), menu)
        self.actExpandAll.triggered.connect(self.expandAll)
        menu.insertAction(first, self.actExpandAll)
        
        self.actCollapseAll = QAction(self.tr("Collapse All"), menu)
        self.actCollapseAll.triggered.connect(self.collapseAll)
        menu.insertAction(first, self.actCollapseAll)
        
        menu.insertSeparator(first)
        
        return menu
        
    def openNewTab(self):
        mainWindow().mainEditor.openIndexes(self._indexesToOpen, newTab=True)
        
    def expandCurrentIndex(self, index=None):
        if index is None or type(index) == bool:
            index = self._indexesToOpen[0]  #self.currentIndex()
        
        self.expand(index)
        for i in range(self.model().rowCount(index)):
            idx = self.model().index(i, 0, index)
            self.expandCurrentIndex(index=idx)    
    
    def collapseCurrentIndex(self, index=None):
        if index is None or type(index) == bool:
            index = self._indexesToOpen[0]  #self.currentIndex()
        
        self.collapse(index)
        for i in range(self.model().rowCount(index)):
            idx = self.model().index(i, 0, index)
            self.collapseCurrentIndex(index=idx)
        
    def dragMoveEvent(self, event):
        dndView.dragMoveEvent(self, event)
        QTreeView.dragMoveEvent(self, event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            # Capture mouse press so that selection doesn't change
            # on right click
            pass
        else:
            QTreeView.mousePressEvent(self, event)