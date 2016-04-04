#!/usr/bin/env python
# --!-- coding: utf8 --!--
import os
from collections import OrderedDict

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from manuskript import exporter
from manuskript.functions import lightBlue
from manuskript.ui.exporters.exporter_ui import Ui_exporter
from manuskript.ui.exporters.exportersManager import exportersManager


class exporterDialog(QWidget, Ui_exporter):
    def __init__(self, parent=None, mw=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        # Var
        self.mw = mw
        self.currentExporter = None

        # Populates lite
        self.cmbExporters.clear()
        for E in exporter.exporters:

            if not E.isValid():
                continue

            self.cmbExporters.addItem(E.name)
            self.cmbExporters.setItemData(self.cmbExporters.count() - 1, QBrush(QColor(Qt.darkBlue)), Qt.ForegroundRole)
            self.cmbExporters.setItemData(self.cmbExporters.count() - 1, QBrush(lightBlue()), Qt.BackgroundRole)
            item = self.cmbExporters.model().item(self.cmbExporters.count() - 1)
            item.setFlags(Qt.ItemIsEnabled)

            for f in E.exportTo:
                name = f.name if f.implemented else self.tr("{} (not implemented yet)").format(f.name)
                self.cmbExporters.addItem(name, E.name)

        self.btnManageExporters.clicked.connect(self.openManager)

        self.cmbExporters.currentIndexChanged.connect(self.updateUi)
        self.cmbExporters.setCurrentIndex(1)

        print(exporter.basic.basicFormat.concatenate(mw.mdlOutline.rootItem))

    def updateUi(self, index):
        name = self.cmbExporters.currentText()
        exporterName = self.cmbExporters.currentData()

        E = exporter.getExporterByName(exporterName)

        if not E:
            self.setWidgetsEnabled(False)
            return

        F = E.getFormatByName(name)

        if not F or not F.implemented:
            self.setWidgetsEnabled(False)
            return

        self.setWidgetsEnabled(True)

        self.grpSettings.setVisible(F.requires["Settings"])
        self.grpPreviewBefore.setVisible(F.requires["PreviewBefore"])
        self.grpPreviewAfter.setVisible(F.requires["PreviewAfter"])

        # if F.requires["Settings"]:
        #     self.settingsWidget = F.settingsWidget()
        #
        # if F.requires["PreviewBefore"]:
        #     self.previewBefore = F.previewWidgetBefore()
        #
        # if F.requires["PreviewAfter"]:
        #     self.previewAfter = F.previewWidgetAfter()

    def setWidgetsEnabled(self, value):
        self.grpSettings.setEnabled(value)
        self.grpPreviewBefore.setEnabled(value)
        self.grpPreviewAfter.setEnabled(value)

    def openManager(self):
        self.dialog = exportersManager()
        self.dialog.show()

        r = self.dialog.geometry()
        r2 = self.geometry()
        self.dialog.move(r2.center() - r.center())