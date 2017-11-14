#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QBrush, QColor
from PyQt5.QtWidgets import QComboBox

from manuskript.enums import Outline
from manuskript.functions import toInt
from manuskript.ui import style as S


class cmbOutlineCharacterChoser(QComboBox):
    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        self.activated[int].connect(self.submit)
        self._column = Outline.POV.value
        self._index = None
        self._indexes = None
        self._updating = False
        self._various = False

    def setModels(self, mdlCharacter, mdlOutline):
        self.mdlCharacters = mdlCharacter
        self.mdlCharacters.dataChanged.connect(self.updateItems)
        self.mdlCharacters.rowsInserted.connect(self.updateItems)
        self.mdlCharacters.rowsRemoved.connect(self.updateItems)

        self.mdlOutline = mdlOutline
        self.mdlOutline.dataChanged.connect(self.update)
        self.updateItems()

    def updateItems(self):
        self.clear()
        self.addItem(QIcon.fromTheme("dialog-no"), self.tr("None"))

        l = [self.tr("Main"), self.tr("Secondary"), self.tr("Minor")]

        for importance in range(3):
            self.addItem(l[importance])
            self.setItemData(self.count() - 1, QBrush(QColor(S.highlightedTextDark)), Qt.ForegroundRole)
            self.setItemData(self.count() - 1, QBrush(QColor(S.highlightLight)), Qt.BackgroundRole)
            item = self.model().item(self.count() - 1)
            item.setFlags(Qt.ItemIsEnabled)
            for i in range(self.mdlCharacters.rowCount()):
                imp = toInt(self.mdlCharacters.importance(i))

                if not 2 - imp == importance:
                    continue

                self.addItem(self.mdlCharacters.icon(i), self.mdlCharacters.name(i), self.mdlCharacters.ID(i))
                self.setItemData(self.count() - 1, self.mdlCharacters.name(i), Qt.ToolTipRole)

        self._various = False

        if self._index or self._indexes:
            self.updateSelectedItem()

    def setCurrentModelIndex(self, index):
        self._indexes = None
        if index.column() != self._column:
            index = index.sibling(index.row(), self._column)
        self._index = index
        self.updateItems()

    def setCurrentModelIndexes(self, indexes):
        self._index = None

        idxes = []
        for i in indexes:
            if i.isValid():
                if i.column() != self._column:
                    i = i.sibling(i.row(), self._column)
                idxes.append(i)

        if idxes != self._indexes:
            self._indexes = idxes
            self.updateItems()

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

    def getPOV(self, index):
        item = index.internalPointer()
        POV = item.data(self._column)
        return POV

    def selectPOV(self, POV):
        idx = self.findData(POV)
        if idx != -1:
            self.setCurrentIndex(idx)
        else:
            self.setCurrentIndex(0)

    def updateSelectedItem(self, idx1=None, idx2=None):

        if self._updating:
            return

        if self._index:
            POV = self.getPOV(self._index)
            self.selectPOV(POV)

        elif self._indexes:
            POVs = []
            same = True

            for i in self._indexes:
                POVs.append(self.getPOV(i))

            for POV in POVs[1:]:
                if POV != POVs[0]:
                    same = False
                    break

            if same:
                self._various = False
                self.selectPOV(POVs[0])

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
            if self._various and self.currentIndex() == 0:
                return

            self._updating = True
            for i in self._indexes:
                self.mdlOutline.setData(i, self.currentData())
            self._updating = False
