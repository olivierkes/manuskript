#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QIntValidator

from manuskript.enums import Outline
from manuskript.ui.views.propertiesView_ui import Ui_propertiesView


class propertiesView(QWidget, Ui_propertiesView):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.setupUi(self)
        self.txtGoal.setColumn(Outline.setGoal.value)

    def setModels(self, mdlOutline, mdlCharacter, mdlLabels, mdlStatus):
        self.cmbPOV.setModels(mdlCharacter, mdlOutline)
        self.cmbLabel.setModels(mdlLabels, mdlOutline)
        self.cmbStatus.setModels(mdlStatus, mdlOutline)
        self.chkCompile.setModel(mdlOutline)
        self.txtTitle.setModel(mdlOutline)
        self.txtGoal.setModel(mdlOutline)
        self.txtGoal.setValidator(QIntValidator(0, 9999999))

    def getIndexes(self, sourceView):
        """Returns a list of indexes from list of QItemSelectionRange"""
        indexes = []

        for i in sourceView.selection().indexes():
            if i.column() != 0:
                continue

            if i not in indexes:
                indexes.append(i)

        return indexes

    def selectionChanged(self, sourceView):

        indexes = self.getIndexes(sourceView)
        # print(indexes)
        if len(indexes) == 0:
            self.setEnabled(False)

        elif len(indexes) == 1:
            self.setEnabled(True)
            self.setLabelsItalic(False)
            idx = indexes[0]
            self.cmbPOV.setCurrentModelIndex(idx)
            self.cmbLabel.setCurrentModelIndex(idx)
            self.cmbStatus.setCurrentModelIndex(idx)
            self.chkCompile.setCurrentModelIndex(idx)
            self.txtTitle.setCurrentModelIndex(idx)
            self.txtGoal.setCurrentModelIndex(idx)

        else:
            self.setEnabled(True)
            self.setLabelsItalic(True)
            self.txtTitle.setCurrentModelIndexes(indexes)
            self.txtGoal.setCurrentModelIndexes(indexes)
            self.chkCompile.setCurrentModelIndexes(indexes)
            self.cmbPOV.setCurrentModelIndexes(indexes)
            self.cmbLabel.setCurrentModelIndexes(indexes)
            self.cmbStatus.setCurrentModelIndexes(indexes)

    def setLabelsItalic(self, value):
        f = self.lblPOV.font()
        f.setItalic(value)
        for lbl in [
            self.lblPOV,
            self.lblStatus,
            self.lblLabel,
            self.lblCompile,
            self.lblGoal
        ]:
            lbl.setFont(f)
