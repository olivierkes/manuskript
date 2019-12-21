#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.enums import FlatData, Model
from manuskript.searchLabels import FlatDataSearchLabels

from manuskript.models.searchableModel import searchableModel
from manuskript.models.searchableItem import searchableItem

"""
All searches are performed on models inheriting from searchableModel, but special metadata such as book summaries
are stored directly on a GUI element (QStandardItemModel). We wrap this GUI element inside this wrapper class
so it exposes the same interface for searches.
"""
class flatDataModelWrapper(searchableModel, searchableItem):
    def __init__(self, qstandardItemModel):
        self.qstandardItemModel = qstandardItemModel

    def searchableItems(self):
        return [flatDataItemWrapper(self.qstandardItemModel)]


class flatDataItemWrapper(searchableItem):
    def __init__(self, qstandardItemModel):
        super().__init__(FlatDataSearchLabels)
        self.qstandardItemModel = qstandardItemModel

    def searchModel(self):
        return Model.FlatData

    def searchID(self):
        return None

    def searchTitle(self, column):
        return self.translate(self.searchColumnLabel(column))

    def searchPath(self, column):
        return [self.translate("Summary"), self.translate(self.searchColumnLabel(column))]

    def searchData(self, column):
        return self.qstandardItemModel.item(1, self.searchDataIndex(column)).text()

    @staticmethod
    def searchDataIndex(column):
        columnIndices = {
            FlatData.summarySituation: 0,
            FlatData.summarySentence: 1,
            FlatData.summaryPara: 2,
            FlatData.summaryPage: 3,
            FlatData.summaryFull: 4
        }

        return columnIndices[column]