#!/usr/bin/env python
# --!-- coding: utf8 --!--
import json
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QIcon
from PyQt5.QtWidgets import QWidget, QStyle

from manuskript import exporter
from manuskript.functions import writablePath, openURL
from manuskript.ui.exporters.exporter_ui import Ui_exporter
from manuskript.ui.exporters.exportersManager import exportersManager
from manuskript.ui import style as S


class exporterDialog(QWidget, Ui_exporter):
    def __init__(self, parent=None, mw=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        # Var
        self.mw = mw
        self.currentExporter = None
        self.settingsWidget = None
        self.previewWidget = None

        self.populateExportList()

        self.btnManageExporters.clicked.connect(self.openManager)

        self.cmbExporters.currentIndexChanged.connect(self.updateUi)
        self.cmbExporters.setCurrentIndex(1)

        self.btnPreview.clicked.connect(self.preview)
        self.btnExport.clicked.connect(self.export)

        #FIXME: load last export format

    def populateExportList(self):

        # Populates list
        self.cmbExporters.clear()
        for E in exporter.exporters:

            if not E.isValid() and not E.absentTip:
                continue

            self.cmbExporters.addItem(QIcon(E.icon), E.name)
            self.cmbExporters.setItemData(self.cmbExporters.count() - 1, QBrush(QColor(S.highlightedTextDark)), Qt.ForegroundRole)
            self.cmbExporters.setItemData(self.cmbExporters.count() - 1, QBrush(QColor(S.highlightLight)), Qt.BackgroundRole)
            item = self.cmbExporters.model().item(self.cmbExporters.count() - 1)
            item.setFlags(Qt.ItemIsEnabled)

            if not E.isValid() and E.absentTip:
                self.cmbExporters.addItem(self.style().standardIcon(QStyle.SP_MessageBoxWarning), E.absentTip, "::URL::" + E.absentURL)
                continue

            for f in E.exportTo:

                if not f.isValid():
                    continue

                name = f.name if f.implemented else self.tr("{} (not implemented yet)").format(f.name)
                self.cmbExporters.addItem(QIcon.fromTheme(f.icon), name, E.name)

    def updateUi(self, index):

        # We check if we have an URL to open
        data = self.cmbExporters.currentData()
        if data and data[:7] == "::URL::" and data[7:]:
            openURL(data[7:])

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

            self.splitter.setStretchFactor(0, 3)
            self.splitter.setStretchFactor(1, 6)

    def preview(self):
        E, F = self.getSelectedExporter()
        if not E or not F or not F.implemented:
            return
        F.preview(self.settingsWidget, self.previewWidget)

    def export(self):
        E, F = self.getSelectedExporter()
        if not E or not F or not F.implemented:
            return
        F.export(self.settingsWidget)

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

        self.dialog.exportersMightHaveChanged.connect(self.populateExportList)

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