#!/usr/bin/env python
# --!-- coding: utf8 --!--
import json
import os

from PyQt5.QtCore import Qt, QSize, QSortFilterProxyModel
from PyQt5.QtGui import QIcon, QFontMetrics, QFont
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QListWidgetItem, QTreeView

from manuskript.functions import mainWindow, writablePath
from manuskript.ui.importers.generalSettings_ui import Ui_generalSettings
from manuskript.enums import Outline

class generalSettings(QWidget, Ui_generalSettings):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        self.mw = mainWindow()

        # TreeView to select parent
        # We use a proxy to display only folders
        proxy = QSortFilterProxyModel()
        proxy.setFilterKeyColumn(Outline.type.value)
        proxy.setFilterFixedString("folder")
        proxy.setSourceModel(self.mw.mdlOutline)
        self.treeGeneralParent.setModel(proxy)
        for i in range(1, self.mw.mdlOutline.columnCount()):
            self.treeGeneralParent.hideColumn(i)
        self.treeGeneralParent.setCurrentIndex(self.getParentIndex())
        self.chkGeneralParent.toggled.connect(self.treeGeneralParent.setVisible)
        self.treeGeneralParent.hide()
        self.treeGeneralParent.selectionModel().currentChanged.connect(
            lambda: print(self.treeGeneralParent.currentIndex().row()))

    def getParentIndex(self):
        """
        Returns the currently selected index in the mainWindow.
        """
        if len(self.mw.treeRedacOutline.selectionModel().
                        selection().indexes()) == 0:
            idx = QModelIndex()
        else:
            idx = self.mw.treeRedacOutline.currentIndex()
        return idx

