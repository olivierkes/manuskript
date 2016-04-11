#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtWidgets import QWidget, QAbstractItemView

from manuskript.enums import Outline
from manuskript.ui.views.basicItemView_ui import Ui_basicItemView


class basicItemView(QWidget, Ui_basicItemView):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.setupUi(self)
        self.txtSummarySentence.setColumn(Outline.summarySentence.value)
        self.txtSummaryFull.setColumn(Outline.summaryFull.value)
        self.txtGoal.setColumn(Outline.setGoal.value)

    def setModels(self, mdlOutline, mdlCharacter, mdlLabels, mdlStatus):
        self.cmbPOV.setModels(mdlCharacter, mdlOutline)
        self.txtSummarySentence.setModel(mdlOutline)
        self.txtSummaryFull.setModel(mdlOutline)
        self.txtGoal.setModel(mdlOutline)

    def getIndexes(self, sourceView):
        """Returns a list of indexes from list of QItemSelectionRange"""
        indexes = []

        for i in sourceView.selection().indexes():
            if i.column() != 0:
                continue

            if i not in indexes:
                indexes.append(i)

        return indexes

    def selectionChanged(self):
        if isinstance(self.sender(), QAbstractItemView):
            selectionModel = self.sender().selectionModel()
        else:
            selectionModel = self.sender()

        indexes = self.getIndexes(selectionModel)

        if len(indexes) == 0:
            self.setEnabled(False)

        elif len(indexes) == 1:
            self.setEnabled(True)
            idx = indexes[0]
            self.txtSummarySentence.setCurrentModelIndex(idx)
            self.txtSummaryFull.setCurrentModelIndex(idx)
            self.cmbPOV.setCurrentModelIndex(idx)
            self.txtGoal.setCurrentModelIndex(idx)

        else:
            self.setEnabled(True)
            self.txtSummarySentence.setCurrentModelIndexes(indexes)
            self.txtSummaryFull.setCurrentModelIndexes(indexes)
            self.cmbPOV.setCurrentModelIndexes(indexes)
            self.txtGoal.setCurrentModelIndexes(indexes)

    def setDict(self, d):
        self.txtSummaryFull.setDict(d)

    def toggleSpellcheck(self, v):
        self.txtSummaryFull.toggleSpellcheck(v)
