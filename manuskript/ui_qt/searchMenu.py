#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtCore import QCoreApplication
from PyQt5 import QtCore

from manuskript.searchLabels import OutlineSearchLabels, CharacterSearchLabels, FlatDataSearchLabels, WorldSearchLabels, PlotSearchLabels
from manuskript.models.searchFilter import searchFilter
from manuskript.enums import Model


def filterKey(modelPreffix, column):
    return modelPreffix + str(column)


class searchMenu(QMenu):
    def __init__(self, parent=None):
        QMenu.__init__(self, parent)

        _translate = QCoreApplication.translate
        # Model keys must match the ones used in search widget class
        self.filters = {
            Model.Outline: searchFilter(_translate("MainWindow", "Outline"), True, list(OutlineSearchLabels.keys())),
            Model.Character: searchFilter(_translate("MainWindow", "Characters"), True, list(CharacterSearchLabels.keys())),
            Model.FlatData: searchFilter(_translate("MainWindow", "FlatData"), True, list(FlatDataSearchLabels.keys())),
            Model.World: searchFilter(_translate("MainWindow", "World"), True, list(WorldSearchLabels.keys())),
            Model.Plot: searchFilter(_translate("MainWindow", "Plot"), True, list(PlotSearchLabels.keys()))
        }

        self.options = {
            "CS": [self.tr("Case sensitive"), True],
            "MatchWords": [self.tr("Match words"), False],
            "Regex": [self.tr("Regex"), False]
        }

        self._generateOptions()

    def _generateOptions(self):
        a = QAction(self.tr("Search in:"), self)
        a.setEnabled(False)
        self.addAction(a)
        for filterKey in self.filters:
            a = QAction(self.tr(self.filters[filterKey].label()), self)
            a.setCheckable(True)
            a.setChecked(self.filters[filterKey].enabled())
            a.setData(filterKey)
            a.triggered.connect(self._updateFilters)
            self.addAction(a)
        self.addSeparator()

        a = QAction(self.tr("Options:"), self)
        a.setEnabled(False)
        self.addAction(a)
        for optionKey in self.options:
            a = QAction(self.options[optionKey][0], self)
            a.setCheckable(True)
            a.setChecked(self.options[optionKey][1])
            a.setData(optionKey)
            a.triggered.connect(self._updateOptions)
            self.addAction(a)
        self.addSeparator()

    def _updateFilters(self):
        a = self.sender()
        self.filters[a.data()].setEnabled(a.isChecked())

    def _updateOptions(self):
        a = self.sender()
        self.options[a.data()][1] = a.isChecked()

    def columns(self, modelName):
        if self.filters[modelName].enabled():
            return self.filters[modelName].modelColumns()
        else:
            return []

    def caseSensitive(self):
        return self.options["CS"][1]

    def matchWords(self):
        return self.options["MatchWords"][1]

    def regex(self):
        return self.options["Regex"][1]

    def mouseReleaseEvent(self, event):
        # Workaround for enabling / disabling actions without closing the menu.
        # Source: https://stackoverflow.com/a/14967212
        action = self.activeAction()
        if action:
            action.setEnabled(False)
            QMenu.mouseReleaseEvent(self, event)
            action.setEnabled(True)
            action.trigger()
        else:
            QMenu.mouseReleaseEvent(self, event)

    def keyPressEvent(self, event):
        # Workaround for enabling / disabling actions without closing the menu.
        # Source: https://stackoverflow.com/a/14967212
        action = self.activeAction()
        if action and event.key() == QtCore.Qt.Key_Return:
            action.setEnabled(False)
            QMenu.keyPressEvent(self, event)
            action.setEnabled(True)
            action.trigger()
        else:
            QMenu.keyPressEvent(self, event)
