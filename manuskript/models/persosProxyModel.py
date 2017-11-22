#!/usr/bin/env python
#--!-- coding: utf8 --!--

from manuskript import enums
from manuskript.ui import style as S


class persosProxyModel(QSortFilterProxyModel):

    newStatuses = pyqtSignal()

    def __init__(self, parent=None):
        QSortFilterProxyModel.__init__(self, parent)

        #self.rootItem = QStandardItem()
        self.p1 = QStandardItem(self.tr("Main"))
        self.p2 = QStandardItem(self.tr("Secundary"))
        self.p3 = QStandardItem(self.tr("Minors"))

        self._cats = [
            self.p1,
            self.p2,
            self.p3
            ]

    def mapFromSource(self, sourceIndex):
        if not sourceIndex.isValid():
            return QModelIndex()

        row = self._map.index(sourceIndex.row())
        #item = sourceIndex.internalPointer()
        item = self.sourceModel().itemFromIndex(sourceIndex)

        return self.createIndex(row, sourceIndex.column(), item)

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        if index.isValid() and not self.mapToSource(index).isValid():
            return Qt.NoItemFlags#Qt.ItemIsEnabled
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def mapToSource(self, proxyIndex):
        if not proxyIndex.isValid():
            return QModelIndex()

        row = self._map[proxyIndex.row()]

        if type(row) != int:
            return QModelIndex()

        #item = proxyIndex.internalPointer()
        item = self.sourceModel().item(row, proxyIndex.column())

        return self.sourceModel().indexFromItem(item)

    def setSourceModel(self, model):
        QSortFilterProxyModel.setSourceModel(self, model)
        self.sourceModel().dataChanged.connect(self.mapModelMaybe)
        self.sourceModel().rowsInserted.connect(self.mapModel)
        self.sourceModel().rowsRemoved.connect(self.mapModel)
        self.sourceModel().rowsMoved.connect(self.mapModel)

        self.mapModel()

    def mapModelMaybe(self, topLeft, bottomRight):
        if topLeft.column() <= Perso.importance.value <= bottomRight.column():
            self.mapModel()

    def mapModel(self):
        self.beginResetModel()
        src = self.sourceModel()

        self._map = []

        for i, cat in enumerate(self._cats):
            self._map.append(cat)

            for p in range(src.rowCount()):
                item = src.item(p, Perso.importance.value)

                if item and item.text():
                    imp = int(item.text())
                else:
                    imp = 0

                if 2-imp == i:
                    self._map.append(p)

        self.endResetModel()


    def data(self, index, role=Qt.DisplayRole):

        if index.isValid() and not self.mapToSource(index).isValid():
            row = index.row()

            if role == Qt.DisplayRole:
                return self._map[row].text()

            elif role == Qt.ForegroundRole:
                return QBrush(QColor(S.highlightedTextDark))
            elif role == Qt.BackgroundRole:
                return QBrush(QColor(S.highlightLight))
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
            elif role == Qt.FontRole:
                f = QFont()
                #f.setPointSize(f.pointSize() + 1)
                f.setWeight(QFont.Bold)
                return f
        else:
            #FIXME: sometimes, the name of the character is not displayed
            return self.sourceModel().data(self.mapToSource(index), role)

    def index(self, row, column, parent):

        i = self._map[row]

        if type(i) != int:

            return self.createIndex(row, column, i)

        else:

            return self.mapFromSource(self.sourceModel().index(i, column, QModelIndex()))

    def parent(self, index=QModelIndex()):
        return QModelIndex()

    def rowCount(self, parent=QModelIndex()):
        return len(self._map)

    def columnCount(self, parent=QModelIndex()):
        return self.sourceModel().columnCount(QModelIndex())

    def item(self, row, col, parent=QModelIndex()):
        idx = self.mapToSource(self.index(row, col, parent))
        return self.sourceModel().item(idx.row(), idx.column())


    #def setData(self, index, value, role=Qt.EditRole):
        #pass
