#!/usr/bin/env python
# --!-- coding: utf8 --!--


from manuskript.models.searchResultModel import searchResultModel
from manuskript.functions import search
from PyQt5.QtCore import QCoreApplication


class searchableItem:

    def __init__(self, searchColumnLabels):
        self._searchColumnLabels = searchColumnLabels

    def searchOccurrences(self, searchRegex, column):
        return [self.wrapSearchOccurrence(column, startPos, endPos, context) for (startPos, endPos, context) in search(searchRegex, self.searchData(column))]

    def wrapSearchOccurrence(self, column, startPos, endPos, context):
        return searchResultModel(self.searchModel(), self.searchID(), column, self.searchTitle(column), self.searchPath(column), [(startPos, endPos)], context)

    def searchModel(self):
        raise NotImplementedError

    def searchID(self):
        raise NotImplementedError

    def searchTitle(self, column):
        raise NotImplementedError

    def searchPath(self, column):
        return []

    def searchData(self, column):
        raise NotImplementedError

    def searchColumnLabel(self, column):
        return self._searchColumnLabels.get(column, "")

    def translate(self, text):
        return QCoreApplication.translate("MainWindow", text)
