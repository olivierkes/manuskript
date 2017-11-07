#!/usr/bin/env python
# --!-- coding: utf8 --!--
import json
import os

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QBrush, QColor, QIcon
from PyQt5.QtWidgets import QWidget, QFileDialog

from manuskript.functions import lightBlue, writablePath, appPath
from manuskript.ui.importers.importer_ui import Ui_importer
from manuskript.ui.importers.generalSettings import generalSettings
from manuskript.ui import style
from manuskript import importer
from manuskript.models.outlineModel import outlineModel
from manuskript.enums import Outline

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
        self.setStyleSheet(style.mainWindowSS())
        self.tree.setStyleSheet("QTreeView{background:transparent;}")
        self.editor.setStyleSheet("QWidget{background:transparent;}")

        # Register importFormats:
        self.importers = importer.importers

        # Populate combo box with formats
        self.populateImportList()

        # Connections
        self.btnChoseFile.clicked.connect(self.selectFile)
        self.btnClearFileName.clicked.connect(self.setFileName)
        self.btnPreview.clicked.connect(self.preview)
        self.cmbImporters.currentTextChanged.connect(self.updateSettings)

        #self.setFileName("")
        QTimer.singleShot(50, lambda:
            self.cmbImporters.setCurrentText("OPML"))
        QTimer.singleShot(50, lambda:
            self.setFileName("/home/olivier/Dropbox/Documents/Travail/Geekeries/Python/PyCharmProjects/manuskript/test-projects/IMPORTS/End Plan 2.opml")
            )

    ############################################################################
    # Combobox / Formats
    ############################################################################

    def populateImportList(self):

        def addFormat(name, icon):
            self.cmbImporters.addItem(QIcon.fromTheme(icon), name)

        for f in self.importers:
            addFormat(f.name, f.icon)

    def currentFormat(self):
        formatName = self.cmbImporters.currentText()
        F = [F for F in self.importers if F.name == formatName][0]
        return F

    ############################################################################
    # Import file
    ############################################################################

    def selectFile(self):
        """
        Called to select a file in the file system. Uses QFileDialog.
        """

        # We find the current selected format
        F = self.currentFormat()

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
        """
        Updates Ui with given filename. Filename can be empty.
        """
        if fileName:
            self.fileName = fileName
            self.lblFileName.setText(os.path.basename(fileName))
            self.lblFileName.setToolTip(fileName)
            ext = os.path.splitext(fileName)[1]
            if ext and ext in self.formatsIcon:
                icon = QIcon.fromTheme(self.formatsIcon[ext])
            elif os.path.isdir(fileName):
                icon = QIcon.fromTheme("folder")

            #self.lblIcon.setVisible(True)
            h = self.lblFileName.height()
            self.lblIcon.setPixmap(icon.pixmap(h, h))

        else:
            self.fileName = None
            self.lblFileName.setText("")

        hasFile = True if fileName else False

        self.btnClearFileName.setVisible(hasFile)
        self.lblIcon.setVisible(hasFile)
        self.btnChoseFile.setVisible(not hasFile)
        self.btnPreview.setEnabled(hasFile)
        self.btnImport.setEnabled(hasFile)

    ############################################################################
    # UI
    ############################################################################

    def updateSettings(self):
        """
        When the current format change (through the combobox), we update the
        settings widget using the current format provided settings widget.
        """

        F = self.currentFormat()
        self.settingsWidget = generalSettings()
        self.setGroupWidget(self.grpSettings, self.settingsWidget)
        self.grpSettings.setMinimumWidth(200)

        #TODO: custom format widget
        #toolBox = self.settingsWidget.toolBox
        #w = QWidget()
        #toolBox.insertItem(toolBox.count(), w, "Pandoc")
        #See pandoc's abstractPlainText

    def setGroupWidget(self, group, widget):
        """
        Sets the given widget as main widget for QGroupBox group.
        """

        # Removes every items from given layout.
        l = group.layout()
        while l.count():
            item = l.itemAt(0)
            l.removeItem(item)
            item.widget().deleteLater()

        l.addWidget(widget)
        widget.setParent(group)

    ############################################################################
    # Preview / Import
    ############################################################################

    def preview(self):

        # We find the current selected format
        F = self.currentFormat()

        # Temporary outlineModel
        previewModel = outlineModel(self)
        previewModel.loadFromXML(
            self.mw.mdlOutline.saveToXML(),
            fromString=True)

        # Parent item
        ID = self.settingsWidget.importUnderID()
        parentItem = previewModel.getItemByID(ID)

        # Calling the importer in a temporary model
        items = F.startImport(self.fileName,
                              parentItem,
                              self.settingsWidget)

        # Do transformations
        # ------------------

        # Trim long titles
        if self.settingsWidget.trimLongTitles():
            def trim(item):
                if len(item.title()) > 32:
                    item.setData(Outline.title.value, item.title()[:32])
                for c in item.children():
                    trim(c)
            for i in items:
                trim(i)

        if items:
            self.tree.setModel(previewModel)
            for i in range(1, previewModel.columnCount()):
                self.tree.hideColumn(i)
            self.tree.selectionModel().currentChanged.connect(self.editor.setCurrentModelIndex)
            self.previewSplitter.setStretchFactor(0, 10)
            self.previewSplitter.setStretchFactor(1, 40)


    def startImport(self):
        pass

        # Note: dont forget to emit: mdl.layoutChanged.emit()
        # Maybe: mw.treeRedacOutline.viewport().update()


