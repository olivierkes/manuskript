#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import QModelIndex, QSortFilterProxyModel


class characterPOVModel(QSortFilterProxyModel):

    def __init__(self, sourceModel, parent=None):
        QSortFilterProxyModel.__init__(self, parent)

        self.setSourceModel(sourceModel)

        if sourceModel:
            sourceModel.dataChanged.connect(self.sourceDataChanged)

    def filterAcceptsRow(self, sourceRow, sourceParent):
        return self.sourceModel().pov(sourceRow)

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
