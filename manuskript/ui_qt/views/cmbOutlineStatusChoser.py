#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QComboBox

from manuskript.enums import Outline


class cmbOutlineStatusChoser(QComboBox):
    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        self.activated[int].connect(self.submit)
        self._column = Outline.status
        self._index = None
        self._indexes = None
        self._updating = False
        self._various = False

    def setModels(self, mdlStatus, mdlOutline):
        self.mdlStatus = mdlStatus
        self.mdlStatus.dataChanged.connect(self.updateItems)
        self.mdlOutline = mdlOutline
        self.mdlOutline.dataChanged.connect(self.update)
        self.updateItems()

    def updateItems(self):
        self.clear()
        for i in range(self.mdlStatus.rowCount()):
            item = self.mdlStatus.item(i, 0)
            if item:
                self.addItem(item.text())

        self._various = False

        if self._index or self._indexes:
            self.updateSelectedItem()

    def setCurrentModelIndex(self, index):
        self._indexes = None
        if index.column() != self._column:
            index = index.sibling(index.row(), self._column)
        self._index = index
        self.updateItems()
        self.updateSelectedItem()

    def setCurrentModelIndexes(self, indexes):
        self._indexes = []
        self._index = None

        for i in indexes:
            if i.isValid():
                if i.column() != self._column:
                    i = i.sibling(i.row(), self._column)
                self._indexes.append(i)

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

    def getStatus(self, index):
        item = index.internalPointer()
        status = item.data(self._column)
        if not status:
            status = 0
        return int(status)

    def updateSelectedItem(self):

        if self._updating:
            return

        if self._index:
            status = self.getStatus(self._index)
            self.setCurrentIndex(status)

        elif self._indexes:
            statuses = []
            same = True

            for i in self._indexes:
                statuses.append(self.getStatus(i))

            for s in statuses[1:]:
                if s != statuses[0]:
                    same = False
                    break

            if same:
                self._various = False
                self.setCurrentIndex(statuses[0])

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
            self.mdlOutline.setData(self._index, self.currentIndex())

        elif self._indexes:
            value = self.currentIndex()

            if self._various:
                if value == 0:
                    return

                value -= 1

            self._updating = True
            for i in self._indexes:
                self.mdlOutline.setData(i, value)
            self._updating = False
