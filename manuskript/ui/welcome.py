#!/usr/bin/env python
# --!-- coding: utf8 --!--

import locale
import imp
import os

from PyQt5.QtCore import QSettings, QRegExp, Qt, QDir
from PyQt5.QtGui import QIcon, QBrush, QColor, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QAction, QFileDialog, QSpinBox, QLineEdit, QLabel, QPushButton, QTreeWidgetItem, \
    qApp, QMessageBox

from manuskript import loadSave
from manuskript import settings
from manuskript.enums import Outline
from manuskript.functions import mainWindow, iconFromColor, appPath
from manuskript.models.characterModel import characterModel
from manuskript.models import outlineItem, outlineModel
from manuskript.models.plotModel import plotModel
from manuskript.models.worldModel import worldModel
from manuskript.ui.welcome_ui import Ui_welcome
from manuskript.ui import style as S

try:
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

class welcome(QWidget, Ui_welcome):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        self.template = []

        self.mw = mainWindow()
        self.btnOpen.clicked.connect(self.openFile)
        self.btnCreate.clicked.connect(self.createFile)
        self.chkLoadLastProject.toggled.connect(self.setAutoLoad)
        self.tree.itemClicked.connect(self.changeTemplate)
        self.btnAddLevel.clicked.connect(self.templateAddLevel)
        self.btnAddWC.clicked.connect(self.templateAddWordCount)
        self.btnCreateText = self.btnCreate.text()

        self.populateTemplates()
        self._templates = self.templates()

    def updateValues(self):
        # Auto load
        autoLoad, last = self.getAutoLoadValues()
        self.chkLoadLastProject.setChecked(autoLoad)

        # Recent Files
        self.loadRecents()

    ###############################################################################
    # AUTOLOAD
    ###############################################################################

    def showEvent(self, event):
        """Waiting for things to be fully loaded to start opening projects."""
        QWidget.showEvent(self, event)

        # Auto load last project
        autoLoad, last = self.getAutoLoadValues()

        if self.mw._autoLoadProject:
            project = self.mw._autoLoadProject
            self.mw._autoLoadProject = None
            self.appendToRecentFiles(project)
            self.mw.loadProject(project)

        elif autoLoad and last:
            self.mw.loadProject(last)

    def getAutoLoadValues(self):
        """
        Reads manuskript system's settings and returns a tuple:
        - `bool`: whether manuskript should automatically load
                  the last opened project or display the
                  welcome widget.
        - `str`:  the absolute path to the last opened project.
        """
        sttgns = QSettings()
        autoLoad = sttgns.value("autoLoad", defaultValue=False, type=bool)
        if autoLoad and sttgns.contains("lastProject"):
            last = sttgns.value("lastProject")
        else:
            last = ""

        return autoLoad, last

    def setAutoLoad(self, v):
        if type(v) == bool:
            QSettings().setValue("autoLoad", v)

    ###############################################################################
    # RECENTS
    ###############################################################################

    def loadRecents(self):
        sttgns = QSettings()
        self.mw.menuRecents.setIcon(QIcon.fromTheme("folder-recent"))
        if sttgns.contains("recentFiles"):
            lst = sttgns.value("recentFiles")
            self.mw.menuRecents.clear()
            for f in [f for f in lst if os.path.exists(f)]:
                name = os.path.split(f)[1]
                a = QAction(name, self)
                a.setData(f)
                a.setStatusTip(f)
                a.triggered.connect(self.loadRecentFile)
                self.mw.menuRecents.addAction(a)

            self.btnRecent.setMenu(self.mw.menuRecents)

    def appendToRecentFiles(self, project):
        sttgns = QSettings()
        if sttgns.contains("recentFiles"):
            recentFiles = sttgns.value("recentFiles")
        else:
            recentFiles = []

        while project in recentFiles:
            recentFiles.remove(project)
        recentFiles.insert(0, project)
        recentFiles = recentFiles[:10]
        sttgns.setValue("recentFiles", recentFiles)

    def loadRecentFile(self):
        act = self.sender()
        self.appendToRecentFiles(act.data())
        self.mw.closeProject()
        self.mw.loadProject(act.data())

    ###############################################################################
    # DIALOGS
    ###############################################################################

    def openFile(self):
        """File dialog that request an existing file. For opening project."""
        filename = QFileDialog.getOpenFileName(self,
                                               self.tr("Open project"),
                                               ".",
                                               self.tr("Manuskript project (*.msk);;All files (*)"))[0]
        if filename:
            self.appendToRecentFiles(filename)
            self.mw.loadProject(filename)

    def saveAsFile(self):
        """File dialog that request a file, existing or not.
        Save data to that file, which then becomes the current project."""
        filename = QFileDialog.getSaveFileName(self,
                                               self.tr("Save project as..."),
                                               ".",
                                               self.tr("Manuskript project (*.msk)"))[0]

        if filename:
            if filename[-4:] != ".msk":
                filename += ".msk"
            self.appendToRecentFiles(filename)
            loadSave.clearSaveCache()  # Ensure all file(s) are saved under new filename
            self.mw.saveDatas(filename)
            # Update Window's project name with new filename
            pName = os.path.split(filename)[1]
            if pName.endswith('.msk'):
                pName=pName[:-4]
            self.mw.setWindowTitle(pName + " - " + self.tr("Manuskript"))

    def createFile(self, filename=None, overwrite=False):
        """When starting a new project, ask for a place to save it.
        Datas are not loaded from file, so they must be populated another way."""
        if not filename:
            filename = QFileDialog.getSaveFileName(
                           self,
                           self.tr("Create New Project"),
                           ".",
                           self.tr("Manuskript project (*.msk)"))[0]

        if filename:
            if filename[-4:] != ".msk":
                filename += ".msk"
            if os.path.exists(filename) and not overwrite:
                # Check if okay to overwrite existing project
                result = QMessageBox.warning(self, self.tr("Warning"),
                    self.tr("Overwrite existing project {} ?").format(filename),
                    QMessageBox.Ok|QMessageBox.Cancel, QMessageBox.Cancel)
                if result == QMessageBox.Cancel:
                    return
            # Create new project
            self.appendToRecentFiles(filename)
            self.loadDefaultDatas()
            self.mw.loadProject(filename, loadFromFile=False)

    ###############################################################################
    # TEMPLATES
    ###############################################################################

    def templates(self):
        return [
            (self.tr("Empty fiction"), [], "Fiction"),
            (self.tr("Novel"), [
                (20, self.tr("Chapter")),
                (5, self.tr("Scene")),
                (500, None)  # A line with None is word count
            ], "Fiction"),
            (self.tr("Novella"), [
                (10, self.tr("Chapter")),
                (5, self.tr("Scene")),
                (500, None)
            ], "Fiction"),
            (self.tr("Short Story"), [
                (10, self.tr("Scene")),
                (1000, None)
            ], "Fiction"),
            (self.tr("Trilogy"), [
                (3, self.tr("Book")),
                (3, self.tr("Section")),
                (10, self.tr("Chapter")),
                (5, self.tr("Scene")),
                (500, None)
            ], "Fiction"),
            (self.tr("Empty non-fiction"), [], "Non-fiction"),
            (self.tr("Research paper"), [
                (3, self.tr("Section")),
                (1000, None)
            ], "Non-fiction")
        ]

    def changeTemplate(self, item, column):
        template = [i for i in self._templates if i[0] == item.text(0)]
        self.btnCreate.setText(self.btnCreateText)

        # Selected item is a template
        if len(template):
            self.template = template[0]
            self.updateTemplate()

        # Selected item is a sample project
        elif item.data(0, Qt.UserRole):
            name = item.data(0, Qt.UserRole)
            # Clear templates
            self.template = self._templates[0]
            self.updateTemplate()
            # Change button text
            self.btnCreate.setText("Open {}".format(name))
            # Load project
            self.mw.loadProject(appPath("sample-projects/{}".format(name)))

    def updateTemplate(self):
        # Clear layout
        def clearLayout(l):
            while l.count() != 0:
                i = l.takeAt(0)
                if i.widget():
                    i.widget().deleteLater()
                if i.layout():
                    clearLayout(i.layout())

        clearLayout(self.lytTemplate)

        # self.templateLayout.addStretch()
        # l = QGridLayout()
        # self.templateLayout.addLayout(l)

        k = 0
        hasWC = False
        for d in self.template[1]:
            spin = QSpinBox(self)
            spin.setRange(0, 999999)
            spin.setValue(d[0])
            # Storing the level of the template in that spinbox, so we can use
            # it to update the template when valueChanged on that spinbox
            # (we do that in self.updateWordCount for convenience).
            spin.setProperty("templateIndex", self.template[1].index(d))
            spin.valueChanged.connect(self.updateWordCount)

            if d[1] != None:
                txt = QLineEdit(self)
                txt.setText(d[1])

            else:
                hasWC = True
                txt = QLabel(self.tr("words each."), self)

            if k != 0:
                of = QLabel(self.tr("of"), self)
                self.lytTemplate.addWidget(of, k, 0)

                btn = QPushButton("", self)
                btn.setIcon(QIcon.fromTheme("edit-delete"))
                btn.setProperty("deleteRow", k)
                btn.setFlat(True)
                btn.clicked.connect(self.deleteTemplateRow)

                self.lytTemplate.addWidget(btn, k, 3)

            self.lytTemplate.addWidget(spin, k, 1)
            self.lytTemplate.addWidget(txt, k, 2)
            k += 1

        self.btnAddWC.setEnabled(not hasWC and len(self.template[1]) > 0)
        self.btnAddLevel.setEnabled(True)
        self.lblTotal.setVisible(hasWC)
        self.updateWordCount()

    def templateAddLevel(self):
        if len(self.template[1]) > 0 and \
                        self.template[1][len(self.template[1]) - 1][1] == None:
            # has word count, so insert before
            self.template[1].insert(len(self.template[1]) - 1, (10, self.tr("Text")))
        else:
            # No word count, so insert at end
            self.template[1].append((10, self.tr("Something")))
        self.updateTemplate()

    def templateAddWordCount(self):
        self.template[1].append((500, None))
        self.updateTemplate()

    def deleteTemplateRow(self):
        btn = self.sender()
        row = btn.property("deleteRow")
        self.template[1].pop(row)
        self.updateTemplate()

    def updateWordCount(self):
        """
        Updates the word count of the template, and displays it in a label.

        Also, updates self.template, which is used to create the items when
        calling self.createFile.
        """
        total = 1

        # Searching for every spinboxes on the widget, and multiplying
        # their values to get the number of words.
        for s in self.findChildren(QSpinBox, QRegExp(".*"),
                                   Qt.FindChildrenRecursively):
            total = total * s.value()

            # Update self.template to reflect the changed values
            templateIndex = s.property("templateIndex")
            self.template[1][templateIndex] = (
                s.value(),
                self.template[1][templateIndex][1])

        if total == 1:
            total = 0

        self.lblTotal.setText(self.tr("<b>Total:</b> {} words (~ {} pages)").format(
                locale.format_string("%d", total, grouping=True),
                locale.format_string("%d", total / 250, grouping=True)
        ))

    def addTopLevelItem(self, name):
        item = QTreeWidgetItem(self.tree, [name])
        item.setBackground(0, QBrush(QColor(S.highlightLight)))
        item.setForeground(0, QBrush(QColor(S.highlightedTextDark)))
        item.setTextAlignment(0, Qt.AlignCenter)
        item.setFlags(Qt.ItemIsEnabled)
        f = item.font(0)
        f.setBold(True)
        item.setFont(0, f)
        return item

    def populateTemplates(self):
        self.tree.clear()
        self.tree.setIndentation(0)

        # Add templates
        item = self.addTopLevelItem(self.tr("Fiction"))
        templates = [i for i in self.templates() if i[2] == "Fiction"]
        for t in templates:
            sub = QTreeWidgetItem(item, [t[0]])

        # Add templates: non-fiction
        item = self.addTopLevelItem(self.tr("Non-fiction"))
        templates = [i for i in self.templates() if i[2] == "Non-fiction"]
        for t in templates:
            sub = QTreeWidgetItem(item, [t[0]])


        # Add Demo project
        item = self.addTopLevelItem(self.tr("Demo projects"))
        dir = QDir(appPath("sample-projects"))
        for f in dir.entryList(["*.msk"], filters=QDir.Files):
            sub = QTreeWidgetItem(item, [f[:-4]])
            sub.setData(0, Qt.UserRole, f)

        self.tree.expandAll()

    def loadDefaultDatas(self):

        # Empty settings
        imp.reload(settings)
        settings.initDefaultValues()

        if self.template:
            t = [i for i in self._templates if i[0] == self.template[0]]
            if t and t[0][2] == "Non-fiction":
                settings.viewMode = "simple"

        # Tasks
        self.mw.mdlFlatData = QStandardItemModel(2, 8, self.mw)

        # Persos
        # self.mw.mdlPersos = QStandardItemModel(0, 0, self.mw)
        self.mw.mdlCharacter = characterModel(self.mw)
        # self.mdlPersosProxy = None # persosProxyModel() # None
        # self.mw.mdlPersosProxy = persosProxyModel(self.mw)

        # self.mw.mdlPersosInfos = QStandardItemModel(1, 0, self.mw)
        # self.mw.mdlPersosInfos.insertColumn(0, [QStandardItem("ID")])
        # self.mw.mdlPersosInfos.setHorizontalHeaderLabels(["Description"])

        # Labels
        self.mw.mdlLabels = QStandardItemModel(self.mw)
        for color, text in [
            (Qt.transparent, ""),
            (Qt.yellow, self.tr("Idea")),
            (Qt.green, self.tr("Note")),
            (Qt.blue, self.tr("Chapter")),
            (Qt.red, self.tr("Scene")),
            (Qt.cyan, self.tr("Research"))
        ]:
            self.mw.mdlLabels.appendRow(QStandardItem(iconFromColor(color), text))

        # Status
        self.mw.mdlStatus = QStandardItemModel(self.mw)
        for text in [
            "",
            self.tr("TODO"),
            self.tr("First draft"),
            self.tr("Second draft"),
            self.tr("Final")
        ]:
            self.mw.mdlStatus.appendRow(QStandardItem(text))

        # Plot
        self.mw.mdlPlots = plotModel(self.mw)

        # Outline
        self.mw.mdlOutline = outlineModel(self.mw)

        # World
        self.mw.mdlWorld = worldModel(self.mw)

        root = self.mw.mdlOutline.rootItem
        _type = "md"

        def addElement(parent, datas):
            if len(datas) == 2 and datas[1][1] == None or \
                            len(datas) == 1:
                # Next item is word count
                n = 0
                for i in range(datas[0][0]):
                    n += 1
                    item = outlineItem(title="{} {}".format(
                            datas[0][1],
                            str(n)),
                            _type=_type,
                            parent=parent)
                    if len(datas) == 2:
                        item.setData(Outline.setGoal, datas[1][0])
                        # parent.appendChild(item)
            else:
                n = 0
                for i in range(datas[0][0]):
                    n += 1
                    item = outlineItem(title="{} {}".format(
                            datas[0][1],
                            str(n)),
                            _type="folder",
                            parent=parent)
                    # parent.appendChild(item)
                    addElement(item, datas[1:])

        if self.template and self.template[1]:
            addElement(root, self.template[1])
