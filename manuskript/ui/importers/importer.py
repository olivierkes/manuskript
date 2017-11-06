#!/usr/bin/env python
# --!-- coding: utf8 --!--
import json
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QIcon
from PyQt5.QtWidgets import QWidget, QFileDialog

from manuskript import exporter
from manuskript.functions import lightBlue, writablePath, appPath
from manuskript.ui.importers.importer_ui import Ui_importer

class importFormat:
    def __init__(self, name, icon, fileFormat):
        self.name = name
        self.icon = icon
        self.fileFormat = fileFormat

class importerDialog(QWidget, Ui_importer):

    formatsIcon = {
        ".epub": "application-epub+zip",
        ".odt": "application-vnd.oasis.opendocument.text",
        ".docx": "application-vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".md": "text-x-markdown",
        ".rst": "text-plain",
        ".tex": "text-x-tex",
        ".opml": "text-x-opml+xml",
        ".html": "text-html",
        }

    def __init__(self, parent=None, mw=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        # Var
        self.mw = mw
        self.fileName = ""

        # Register importFormats:
        self.formats = []
        self.formats.append(importFormat("OPML", "text-x-opml+xml",
                                         "OPML Files (*.opml)"))
        self.formats.append(importFormat("Markdown", "text-x-markdown",
                                         "Markdown files (*.md; *.txt; *)"))
        self.formats.append(importFormat("Folder", "folder",
                                         "<<folder>>"))

        # Populate combo box with formats
        self.populateImportList()

        # Connections
        self.btnChoseFile.clicked.connect(self.selectFile)
        self.btnClearFileName.clicked.connect(self.setFileName)
        self.btnPreview.clicked.connect(self.preview)
        self.setFileName("")

    ############################################################################
    # Combobox / Formats
    ############################################################################

    def populateImportList(self):

        def addFormat(name, icon):
            self.cmbImporters.addItem(QIcon.fromTheme(icon), name)

        for f in self.formats:
            addFormat(f.name, f.icon)

    ############################################################################
    # Import file
    ############################################################################

    def selectFile(self):

        # We find the current selected format
        formatName = self.cmbImporters.currentText()
        F = [F for F in self.formats if F.name == formatName][0]

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        if F.fileFormat == "<<folder>>":
            options = QFileDialog.DontUseNativeDialog | QFileDialog.ShowDirsOnly
            fileName = QFileDialog.getExistingDirectory(self, "Select import folder",
                                                        "", options=options)
        else:
            fileName, _ = QFileDialog.getOpenFileName(self, "Import from file", "",
                                                      F.fileFormat, options=options)
        self.setFileName(fileName)

    def setFileName(self, fileName):
        if fileName:
            self.fileName = fileName
            self.btnPreview.setEnabled(True)
            self.lblFileName.setText(os.path.basename(fileName))
            self.lblFileName.setToolTip(fileName)
            self.btnClearFileName.setVisible(True)
            ext = os.path.splitext(fileName)[1]
            if ext and ext in self.formatsIcon:
                self.lblIcon.setVisible(True)
                h = self.lblFileName.height()
                self.lblIcon.setPixmap(
                    QIcon.fromTheme(self.formatsIcon[ext]).pixmap(h, h)
                )
            elif os.path.isdir(fileName):
                self.lblIcon.setVisible(True)
                h = self.lblFileName.height()
                self.lblIcon.setPixmap(QIcon.fromTheme("folder").pixmap(h, h))

        else:
            self.fileName = None
            self.btnPreview.setEnabled(False)
            self.lblFileName.setText("")
            self.btnClearFileName.setVisible(False)
            self.lblIcon.setVisible(False)

    ############################################################################
    # Preview
    ############################################################################

    def preview(self):
        # TODO
        pass

    ############################################################################
    #
    ############################################################################

    def getParentIndex(self):
        if len(self.mw.treeRedacOutline.selectionModel().
                        selection().indexes()) == 0:
            idx = QModelIndex()
        else:
            idx = self.mw.treeRedacOutline.currentIndex()
        return idx
