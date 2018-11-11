#!/usr/bin/env python
# --!-- coding: utf8 --!--
import json
import os

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QBrush, QColor, QIcon
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox, QStyle

from manuskript.functions import writablePath, appPath, openURL, statusMessage
from manuskript.ui.importers.importer_ui import Ui_importer
from manuskript.ui.importers.generalSettings import generalSettings
from manuskript.ui import style
from manuskript import importer
from manuskript.models import outlineModel, outlineItem
from manuskript.enums import Outline
from manuskript.exporter.pandoc import pandocExporter

class importerDialog(QWidget, Ui_importer):

    formatsIcon = {
        ".epub": "application-epub+zip",
        ".odt": "application-vnd.oasis.opendocument.text",
        ".docx": "application-vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".md": "text-x-markdown",
        ".rst": "text-plain",
        ".tex": "text-x-tex",
        ".opml": "text-x-opml+xml",
        ".xml": "text-x-opml+xml",
        ".html": "text-html",
        }

    def __init__(self, parent=None, mw=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        # Var
        self.mw = mw
        self.settingsWidget = None
        self.fileName = ""
        self.setStyleSheet(style.mainWindowSS())
        self.tree.setStyleSheet("QTreeView{background:transparent;}")
        self.editor.setStyleSheet("QWidget{background:transparent;}")
        self.editor.toggleSpellcheck(False)

        # Register importFormats:
        self.importers = importer.importers

        # Populate combo box with formats
        self.populateImportList()

        # Connections
        self.btnChoseFile.clicked.connect(self.selectFile)
        self.btnClearFileName.clicked.connect(self.setFileName)
        self.btnPreview.clicked.connect(self.preview)
        self.btnImport.clicked.connect(self.doImport)
        self.cmbImporters.currentTextChanged.connect(self.updateSettings)

        self.setFileName("")
        self.updateSettings()

    ############################################################################
    # Combobox / Formats
    ############################################################################

    def populateImportList(self):

        def addFormat(name, icon, identifier):
            # Identifier serves to distinguish 2 importers that would have the
            # same name.
            self.cmbImporters.addItem(QIcon.fromTheme(icon), name, identifier)

        def addHeader(name):
            self.cmbImporters.addItem(name, "header")
            self.cmbImporters.setItemData(self.cmbImporters.count() - 1, QBrush(QColor(style.highlightedTextDark)), Qt.ForegroundRole)
            self.cmbImporters.setItemData(self.cmbImporters.count() - 1, QBrush(QColor(style.highlightLight)), Qt.BackgroundRole)
            item = self.cmbImporters.model().item(self.cmbImporters.count() - 1)
            item.setFlags(Qt.ItemIsEnabled)

        lastEngine = ""

        for f in self.importers:
            # Header
            if f.engine != lastEngine:
                addHeader(f.engine)
                lastEngine = f.engine

            addFormat(f.name, f.icon, "{}:{}".format(f.engine, f.name))
            if not f.isValid():
                item = self.cmbImporters.model().item(self.cmbImporters.count() - 1)
                item.setFlags(Qt.NoItemFlags)

        if not pandocExporter().isValid():
            self.cmbImporters.addItem(
                self.style().standardIcon(QStyle.SP_MessageBoxWarning),
                "Install pandoc to import from much more formats",
                "::URL::http://pandoc.org/installing.html")

        self.cmbImporters.setCurrentIndex(1)

    def currentFormat(self):
        formatIdentifier = self.cmbImporters.currentData()

        if formatIdentifier == "header":
            return None

        F = [F for F in self.importers
               if formatIdentifier == "{}:{}".format(F.engine, F.name)][0]
        # We instantiate the class
        return F()

    ############################################################################
    # Import file
    ############################################################################

    def selectFile(self):
        """
        Called to select a file in the file system. Uses QFileDialog.
        """

        # We find the current selected format
        F = self._format

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
        self.preview()

    def setFileName(self, fileName):
        """
        Updates Ui with given filename. Filename can be empty.
        """
        if fileName:
            self.fileName = fileName
            self.lblFileName.setText(os.path.basename(fileName))
            self.lblFileName.setToolTip(fileName)
            ext = os.path.splitext(fileName)[1]
            icon = None
            if ext and ext in self.formatsIcon:
                icon = QIcon.fromTheme(self.formatsIcon[ext])
            elif os.path.isdir(fileName):
                icon = QIcon.fromTheme("folder")

            if icon:
                self.lblIcon.setVisible(True)
                h = self.lblFileName.height()
                self.lblIcon.setPixmap(icon.pixmap(h, h))
            else:
                self.lblIcon.hide()

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

        # We check if we have to open an URL
        data = self.cmbImporters.currentData()
        if data and data[:7] == "::URL::" and data[7:]:
            # FIXME: use functions.openURL after merge with feature/Exporters
            openURL(data[7:])
            return

        F = self.currentFormat()
        self._format = F

        # Checking if we have a valid importer (otherwise a header)
        if not F:
            self.grpSettings.setEnabled(False)
            self.grpPreview.setEnabled(False)
            return
        self.grpSettings.setEnabled(True)
        self.grpPreview.setEnabled(True)

        self.settingsWidget = generalSettings()
        #TODO: custom format widget
        # self.settingsWidget = F.settingsWidget(self.settingsWidget)

        # Set the settings widget in place
        self.setGroupWidget(self.grpSettings, self.settingsWidget)
        self.grpSettings.setMinimumWidth(200)

        # Clear file name
        self.setFileName("")

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

        if not self.fileName:
            return

        # Creating a temporary outlineModel
        previewModel = outlineModel(self)
        previewModel.loadFromXML(
            self.mw.mdlOutline.saveToXML(),
            fromString=True)

        # Inserting elements
        result = self.startImport(previewModel)

        if result:
            self.tree.setModel(previewModel)
            for i in range(1, previewModel.columnCount()):
                self.tree.hideColumn(i)
            self.tree.selectionModel().currentChanged.connect(self.editor.setCurrentModelIndex)
            self.previewSplitter.setStretchFactor(0, 10)
            self.previewSplitter.setStretchFactor(1, 40)

    def doImport(self):
        """
        Called by the Import button.
        """
        self.startImport(self.mw.mdlOutline)

        # Signal every views that important model changes have happened.
        self.mw.mdlOutline.layoutChanged.emit()

        # I'm getting segfault over this message sometimes...
        # Using status bar message instead...
        #QMessageBox.information(self, self.tr("Import status"),
                                #self.tr("Import Complete."))
        statusMessage("Import complete!", 5000)

        self.close()

    def startImport(self, outlineModel):
        """
        Where most of the magic happens.
        Is used by preview and by doImport (actual import).

        `outlineModel` is the model where the imported items are added.

        FIXME: Optimisation: when adding many outlineItems, outlineItem.updateWordCount
        is a bottleneck. It gets called a crazy number of time, and its not
        necessary.
        """

        items = []

        # We find the current selected format
        F = self._format

        # Parent item
        ID = self.settingsWidget.importUnderID()
        parentItem = outlineModel.getItemByID(ID)

        # Import in top-level folder?
        if self.settingsWidget.importInTopLevelFolder():
            parent = outlineItem(title=os.path.basename(self.fileName),
                                 parent=parentItem)
            parentItem = parent
            items.append(parent)

        # Calling the importer
        rItems = F.startImport(self.fileName,
                              parentItem,
                              self.settingsWidget)

        items.extend(rItems)

        # Do transformations
        items = self.doTransformations(items)

        return True

    def doTransformations(self, items):
        """
        Do general transformations.
        """

        # Trim long titles
        if self.settingsWidget.trimLongTitles():
            for item in items:
                if len(item.title()) > 32:
                    item.setData(Outline.title, item.title()[:32])

        # Split at
        if self.settingsWidget.splitScenes():
            for item in items:
                item.split(self.settingsWidget.splitScenes(), recursive=False)

        return items
