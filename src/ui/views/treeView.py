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
        
        
        if len(self.selectedIndexes()) != 0:
            index = self.currentIndex()
            item = index.internalPointer()
            self.actExpand = QAction(self.tr("Expand {}").format(item.title()), menu)
            self.actExpand.triggered.connect(self.expandCurrentIndex)
            menu.insertAction(first, self.actExpand)
            
            self.actCollapse = QAction(self.tr("Collapse {}").format(item.title()), menu)
            self.actCollapse.triggered.connect(self.collapseCurrentIndex)
            menu.insertAction(first, self.actCollapse)
            
            menu.insertSeparator(first)
            
        self.actExpandAll = QAction(self.tr("Expand All"), menu)
        self.actExpandAll.triggered.connect(self.expandAll)
        menu.insertAction(first, self.actExpandAll)
        
        self.actCollapseAll = QAction(self.tr("Collapse All"), menu)
        self.actCollapseAll.triggered.connect(self.collapseAll)
        menu.insertAction(first, self.actCollapseAll)
        
        menu.insertSeparator(first)
        
        return menu
        
    def expandCurrentIndex(self, index=None):
        if index is None or type(index) == bool:
            index = self.currentIndex()
        
        self.expand(index)
        for i in range(self.model().rowCount(index)):
            idx = self.model().index(i, 0, index)
            self.expandCurrentIndex(index=idx)    
    
    def collapseCurrentIndex(self, index=None):
        if index is None or type(index) == bool:
            index = self.currentIndex()
        
        self.collapse(index)
        for i in range(self.model().rowCount(index)):
            idx = self.model().index(i, 0, index)
            self.collapseCurrentIndex(index=idx)
        
    def dragMoveEvent(self, event):
        dndView.dragMoveEvent(self, event)
        QTreeView.dragMoveEvent(self, event)
        
    def mouseReleaseEvent(self, event):
        QTreeView.mouseReleaseEvent(self, event)
        outlineBasics.mouseReleaseEvent(self, event)