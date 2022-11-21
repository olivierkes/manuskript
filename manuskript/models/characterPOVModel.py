#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import QModelIndex, QSortFilterProxyModel
from manuskript.enums import Character as C

class characterPOVModel(QSortFilterProxyModel):

    def __init__(self, sourceModel, parent=None):
        QSortFilterProxyModel.__init__(self, parent)

        self.setSourceModel(sourceModel)

        if sourceModel:
            sourceModel.dataChanged.connect(self.sourceDataChanged)

    def filterAcceptsRow(self, sourceRow, sourceParent):
        # Although I would prefer to reuse the existing characterModel.pov() method,
        # this is simpler to do, actually works and also more ideomatic Qt code.
        index = self.sourceModel().index(sourceRow, C.pov.value, sourceParent)
        value = self.sourceModel().data(index)
        return bool(value)

    def rowToSource(self, row):
        index = self.index(row, 0)
        sourceIndex = self.mapToSource(index)
        return sourceIndex.row()

    def sourceDataChanged(self, topLeft, bottomRight):
        self.invalidateFilter()

    ###############################################################################
    # CHARACTER QUERIES
    ###############################################################################

    def character(self, row):
        return self.sourceModel().character(self.rowToSource(row))

    def name(self, row):
        return self.sourceModel().name(self.rowToSource(row))

    def icon(self, row):
        return self.sourceModel().icon(self.rowToSource(row))

    def ID(self, row):
        return self.sourceModel().ID(self.rowToSource(row))

    def importance(self, row):
        return self.sourceModel().importance(self.rowToSource(row))

    def pov(self, row):
        return self.sourceModel().pov(self.rowToSource(row))
