#!/usr/bin/env python
# --!-- coding: utf8 --!--
import json
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QWidget

from manuskript import exporter
from manuskript.functions import lightBlue, writablePath
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

                if not f.isValid():
                    continue

                name = f.name if f.implemented else self.tr("{} (not implemented yet)").format(f.name)
                self.cmbExporters.addItem(name, E.name)

        self.btnManageExporters.clicked.connect(self.openManager)

        self.cmbExporters.currentIndexChanged.connect(self.updateUi)
        self.cmbExporters.setCurrentIndex(1)

        self.btnPreview.clicked.connect(self.preview)

    def updateUi(self, index):
        E, F = self.getSelectedExporter()

        if not E or not F or not F.implemented:
            self.setWidgetsEnabled(False)
            return

        self.setWidgetsEnabled(True)

        self.grpSettings.setVisible(F.requires["Settings"])
        self.grpPreview.setVisible(F.requires["Preview"])
        self.btnPreview.setVisible(F.requires["Preview"])

        if F.requires["Settings"]:
            self.settingsWidget = F.settingsWidget()
            self.setGroupWidget(self.grpSettings, self.settingsWidget)

        if F.requires["Preview"]:
            self.previewWidget = F.previewWidget()
            self.setGroupWidget(self.grpPreview, self.previewWidget)

    def preview(self):
        E, F = self.getSelectedExporter()
        if not E or not F or not F.implemented:
            return
        F.preview(self.settingsWidget, self.previewWidget)

    ###################################################################################################################
    # UI
    ###################################################################################################################

    def getSelectedExporter(self):
        name = self.cmbExporters.currentText()
        exporterName = self.cmbExporters.currentData()

        E = exporter.getExporterByName(exporterName)

        if not E:
            return None, None

        F = E.getFormatByName(name)

        if not F:
            return E, F

        return E, F

    def setWidgetsEnabled(self, value):
        """One function to control them all. Enables or disables all groups."""
        self.grpSettings.setEnabled(value)
        self.grpPreview.setEnabled(value)

    def openManager(self):
        """Open exporters manager dialog"""
        self.dialog = exportersManager()
        self.dialog.show()

        r = self.dialog.geometry()
        r2 = self.geometry()
        self.dialog.move(r2.center() - r.center())

    def setGroupWidget(self, group, widget):
        """Sets the given widget as main widget for QGroupBox group."""

        # Removes every items from given layout.
        l = group.layout()
        while l.count():
            item = l.itemAt(0)
            l.removeItem(item)
            item.widget().deleteLater()

        l.addWidget(widget)
        widget.setParent(group)