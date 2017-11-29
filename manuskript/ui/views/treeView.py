#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QTreeView, QAction

from manuskript.enums import Outline
from manuskript.functions import mainWindow
from manuskript.ui.views.dndView import dndView
from manuskript.ui.views.outlineBasics import outlineBasics
from manuskript.ui.views.treeDelegates import treeTitleDelegate


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
        first = menu.actions()[3]

        # Open item in new tab
        #sel = self.selectedIndexes()
        pos = self.viewport().mapFromGlobal(QCursor.pos())
        mouseIndex = self.indexAt(pos)

        # Expand /collapse item
        if mouseIndex.isValid():
            # index = self.currentIndex()
            item = mouseIndex.internalPointer()
            if item.isFolder():
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

    def expandCurrentIndex(self, index=None):
        if index is None or type(index) == bool:
            index = self._indexesToOpen[0]  # self.currentIndex()

        self.expand(index)
        for i in range(self.model().rowCount(index)):
            idx = self.model().index(i, 0, index)
            self.expandCurrentIndex(index=idx)

    def collapseCurrentIndex(self, index=None):
        if index is None or type(index) == bool:
            index = self._indexesToOpen[0]  # self.currentIndex()

        self.collapse(index)
        for i in range(self.model().rowCount(index)):
            idx = self.model().index(i, 0, index)
            self.collapseCurrentIndex(index=idx)

    def dragMoveEvent(self, event):
        dndView.dragMoveEvent(self, event)
        QTreeView.dragMoveEvent(self, event)
