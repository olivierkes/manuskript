#!/usr/bin/env python
# --!-- coding: utf8 --!--
import json
import os

from PyQt5.QtCore import Qt, QSize, QSortFilterProxyModel, QModelIndex
from PyQt5.QtGui import QIcon, QFontMetrics, QFont
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QListWidgetItem, QTreeView

from manuskript.functions import mainWindow, writablePath
from manuskript.ui.importers.generalSettings_ui import Ui_generalSettings
from manuskript.enums import Outline
from manuskript.ui import style


class generalSettings(QWidget, Ui_generalSettings):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.toolBox.setStyleSheet(style.toolBoxSS())

        self.mw = mainWindow()
        self.txtGeneralSplitScenes.setStyleSheet(style.lineEditSS())

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

    def importUnderID(self):
        """
        Returns the ID of the item selected in treeGeneralParent, if checked.
        """
        if self.chkGeneralParent.isChecked():
            idx = self.treeGeneralParent.currentIndex()
            # We used a filter proxy model, so we have to map back to source
            # to get an index from mdlOutline
            idx = self.treeGeneralParent.model().mapToSource(idx)
            if idx.isValid():
                return idx.internalPointer().ID()

        return "0" # 0 is root's ID

    def importInTopLevelFolder(self):
        """
        Should the import be flat in the parent folder, or create a top-level
        folder?
        """
        return self.chkGeneralTopLevel.isChecked()

    def trimLongTitles(self):
        return self.chkGeneralTrimTitles.isChecked()

    def splitScenes(self):
        """
        Return wheter the user wants to split scenes.
        If unchecked, returns False.
        If checked, returns the escaped split mark, or default (in placeholderText).
        """
        if self.chkGeneralSplitScenes.isChecked():
            split = self.txtGeneralSplitScenes.text()

            if not split:
                split = self.txtGeneralSplitScenes.placeholderText()

            split = split.replace("\\n", "\n")
            split = split.replace("\\t", "\t")
            return split

        else:
            return False

