#!/usr/bin/env python
# --!-- coding: utf8 --!--
import os
from collections import OrderedDict

from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QFileDialog

from manuskript import exporter
from manuskript.ui.exporters.exportersManager_ui import Ui_ExportersManager
from manuskript.ui import style as S


class exportersManager(QWidget, Ui_ExportersManager):

    exportersMightHaveChanged = pyqtSignal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.lblExporterName.setStyleSheet(S.titleLabelSS())

        # Var
        self.currentExporter = None

        # Populates lite
        self.lstExporters.clear()
        for E in exporter.exporters:
            item = QListWidgetItem(QIcon(E.icon), E.name)
            self.lstExporters.addItem(item)

        # UI
        for i in range(self.lstExporters.count()):
            item = self.lstExporters.item(i)
            item.setSizeHint(QSize(item.sizeHint().width(), 42))
            item.setTextAlignment(Qt.AlignCenter)
        self.lstExporters.setMaximumWidth(150)
        self.lstExporters.setMinimumWidth(150)

        self.lstExporters.currentTextChanged.connect(self.updateUi)
        self.lstExportTo.currentTextChanged.connect(self.updateFormatDescription)

        self.lstExporters.setCurrentRow(0)

        self.btnSetPath.clicked.connect(self.setAppPath)
        self.txtPath.editingFinished.connect(self.updateAppPath)

    def updateUi(self, name):
        E = exporter.getExporterByName(name)
        self.currentExporter = E

        if not E:
            self.stack.setEnabled(False)
            return

        self.stack.setEnabled(True)

        # Updates name and description
        self.lblExporterName.setText(E.name)
        self.lblExporterDescription.setText(E.description)

        # Updates formats
        self.lstExportTo.clear()

        for f in E.exportTo:
            item = QListWidgetItem(QIcon.fromTheme(f.icon), f.name)
            self.lstExportTo.addItem(item)

        self.grpExportTo.layout().setStretch(0, 4)
        self.grpExportTo.layout().setStretch(1, 6)

        self.lstExportTo.setCurrentRow(0)

        # Updates path & version
        self.grpPath.setVisible(E.name != "Manuskript")  # We hide if exporter is manuskript

        # Installed
        if E.isValid() == 2:
            self.lblStatus.setText(self.tr("Installed"))
            self.lblStatus.setStyleSheet("color: darkGreen;")
            self.lblHelpText.setVisible(False)
            self.lblVersion.setVisible(True)
            self.lblVersionName.setVisible(True)
        elif E.isValid() == 1:
            self.lblStatus.setText(self.tr("Custom"))
            self.lblStatus.setStyleSheet("color: darkOrange;")
            self.lblHelpText.setVisible(False)
            self.lblVersion.setVisible(True)
            self.lblVersionName.setVisible(True)
        else:
            self.lblStatus.setText(self.tr("Not found"))
            self.lblStatus.setStyleSheet("color: red;")
            self.lblHelpText.setVisible(True)
            self.lblHelpText.setText(self.tr("{} not found. Install it, or set path manually.").format(name))
            self.lblVersion.setVisible(False)
            self.lblVersionName.setVisible(False)

        # Version
        self.lblVersion.setText(E.version())

        # Path
        if E.path():
            self.txtPath.setText(E.path())
        else:
            self.txtPath.setText(E.customPath)

    def updateFormatDescription(self, name):
        if self.currentExporter:
            f = self.currentExporter.getFormatByName(name)

            if not f:
                self.lblExportToDescription.setText("")

            else:

                desc = "<b>{}:</b> {}".format(
                    name,
                    f.description)

                if not f.isValid():
                    desc += "<br><br>" + \
                            self.tr("<b>Status:</b> uninstalled.") + \
                            "<br><br>" + \
                            self.tr("<b>Requires:</b> ") + f.InvalidBecause

                self.lblExportToDescription.setText(desc)

    def setAppPath(self):
        if self.currentExporter:
            E = self.currentExporter
            fn = QFileDialog.getOpenFileName(self,
                                             caption=self.tr("Set {} executable path.").format(E.cmd),
                                             directory=E.customPath)
            if fn[0]:
                self.updateAppPath(fn[0])

    def updateAppPath(self, path=""):
        if not path:
            path = self.txtPath.text()

        if self.currentExporter:
            E = self.currentExporter
            E.setCustomPath(path)
            self.txtPath.setText(E.customPath)

            self.updateUi(E.name)
            self.exportersMightHaveChanged.emit()

