#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from functions import *
from ui.welcome_ui import *
from models.outlineModel import *
from models.plotModel import *
from models.persosProxyModel import *
import settings
import locale
locale.setlocale(locale.LC_ALL, '')


class welcome(QWidget, Ui_welcome):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        
        self.mw = mainWindow()
        self.btnOpen.clicked.connect(self.openFile)
        self.btnCreate.clicked.connect(self.createFile)
        self.chkLoadLastProject.toggled.connect(self.setAutoLoad)
        self.tree.itemActivated.connect(self.changeTemplate)
        self.btnAddLevel.clicked.connect(self.templateAddLevel)
        self.btnAddWC.clicked.connect(self.templateAddWordCount)
        
        self.populateTemplates()
        
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
        
        if autoLoad and last:
            self.mw.loadProject(last)
    
    def getAutoLoadValues(self):
        sttgns = QSettings()
        if sttgns.contains("autoLoad"):
            autoLoad = True if sttgns.value("autoLoad") == "true" else False
        else:
            autoLoad = False
        if autoLoad and sttgns.contains("lastProject"):
            last = sttgns.value("lastProject")
        else:
            last = ""
        
        return autoLoad, last
    
    def setAutoLoad(self, v):
        QSettings().setValue("autoLoad", v)

###############################################################################
# RECENTS
###############################################################################
        
    def loadRecents(self):
        sttgns = QSettings()
        if sttgns.contains("recentFiles"):
            lst = sttgns.value("recentFiles")
            self.mw.menuRecents.clear()
            for f in lst:
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
        self.mw.loadProject(act.data())

###############################################################################
# DIALOGS
###############################################################################
            
    def openFile(self):
        """File dialog that request an existing file. For opening project."""
        filename = QFileDialog.getOpenFileName(self, 
                        self.tr("Open project"),
                        ".", 
                        self.tr("Manuskript project (*.msk)"))[0]
        if filename:
            self.appendToRecentFiles(filename)
            self.mw.loadProject(filename)
            
    def saveAsFile(self):
        """File dialog that request a file, existing or not. 
        Save datas to that file, which then becomes the current project."""
        filename = QFileDialog.getSaveFileName(self, 
                        self.tr("Save project as..."),
                        ".", 
                        self.tr("Manuskript project (*.msk)"))[0]
        
        if filename:
            self.appendToRecentFiles(filename)
            self.mw.saveDatas(filename)
            
    def createFile(self):
        """When starting a new project, ask for a place to save it.
        Datas are not loaded from file, so they must be populated another way."""
        filename = QFileDialog.getSaveFileName(self, 
                        self.tr("Create New Project"),
                        ".", 
                        self.tr("Manuskript project (*.msk)"))[0]
        
        if filename:
            self.appendToRecentFiles(filename)
            self.loadDefaultDatas()
            self.mw.loadProject(filename, loadFromFile=False)

###############################################################################
# TEMPLATES
###############################################################################            
           
    def templates(self):
        return [
            (self.tr("Empty"), []),
            (self.tr("Novel"), [
                (  20, self.tr("Chapter")),
                (   5, self.tr("Scene")),
                ( 500, None)                   # A line with None is word count
                ]),
            (self.tr("Novella"), [
                (  10, self.tr("Chapter")),
                (   5, self.tr("Scene")),
                ( 500, None)
                ]),
            (self.tr("Short Story"), [
                (  10, self.tr("Scene")),
                (1000, None)
                ]),
            (self.tr("Trilogy"), [
                (   3, self.tr("Book")),
                (   3, self.tr("Section")),
                (  10, self.tr("Chapter")),
                (   5, self.tr("Scene")),
                ( 500, None)
                ]),
            (self.tr("Research paper"), [
                (   3, self.tr("Section")),
                (1000, None)
                ])
            ]
           
    def changeTemplate(self, item, column):
        self.template = [i for i in self.templates() if i[0] == item.text(0)][0][1]
        self.updateTemplate()
        
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
            
        #self.templateLayout.addStretch()
        #l = QGridLayout()
        #self.templateLayout.addLayout(l)
        
        k = 0
        hasWC = False
        for d in self.template:
            spin = QSpinBox(self)
            spin.setRange(0, 999999)
            spin.setValue(d[0])
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
                btn.clicked.connect(self.deleteTemplateRow)
                
                self.lytTemplate.addWidget(btn, k, 3)
                
                
            self.lytTemplate.addWidget(spin, k, 1)
            self.lytTemplate.addWidget(txt, k, 2)
            k += 1
        
        self.btnAddWC.setEnabled(not hasWC and len(self.template) > 0)
        self.btnAddLevel.setEnabled(True)
        self.lblTotal.setVisible(hasWC)
        self.updateWordCount()
            
    def templateAddLevel(self):
        if len(self.template) > 0 and \
           self.template[len(self.template) - 1][1] == None:
            # has word cound, so insert before
            self.template.insert(len(self.template) - 1, (10, self.tr("Text")))
        else:
            # No word count, so insert at end
            self.template.append((10, self.tr("Something")))
        self.updateTemplate()
            
    def templateAddWordCount(self):
        self.template.append((500, None))
        self.updateTemplate()
            
    def deleteTemplateRow(self):
        btn = self.sender()
        row = btn.property("deleteRow")
        self.template.pop(row)
        self.updateTemplate()
            
    def updateWordCount(self):
        total = 1
        for s in self.findChildren(QSpinBox, QRegExp(".*"),
                                   Qt.FindChildrenRecursively):
            total = total * s.value()
        
        if total == 1: 
            total = 0
            
        self.lblTotal.setText(self.tr("<b>Total:</b> {} words (~ {} pages)").format(
            locale.format("%d", total, grouping=True),
            locale.format("%d", total / 250, grouping=True)
        ))
           
    def addTopLevelItem(self, name):
        item = QTreeWidgetItem(self.tree, [name])
        item.setBackground(0, QBrush(QColor(Qt.blue).lighter(190)))
        item.setForeground(0, QBrush(Qt.darkBlue))
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
        item = self.addTopLevelItem(self.tr("Templates"))
        templates = self.templates()
        for t in templates:
            sub = QTreeWidgetItem(item, [t[0]])
        
        # Add Demo project
        item = self.addTopLevelItem(self.tr("Demo projects"))
        # FIXME: none yet
        
        self.tree.expandAll()
           
    def loadDefaultDatas(self):
        # Données
        self.mw.mdlFlatData = QStandardItemModel(2, 8)

        # Persos
        self.mw.mdlPersos = QStandardItemModel(0, 0)
        #self.mdlPersosProxy = None # persosProxyModel() # None
        self.mw.mdlPersosProxy = persosProxyModel(self)

        self.mw.mdlPersosInfos = QStandardItemModel(1, 0)
        self.mw.mdlPersosInfos.insertColumn(0, [QStandardItem("ID")])
        self.mw.mdlPersosInfos.setHorizontalHeaderLabels(["Description"])

        # Labels
        self.mw.mdlLabels = QStandardItemModel()
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
        self.mw.mdlStatus = QStandardItemModel()
        for text in [
                "",
                self.tr("TODO"),
                self.tr("First draft"),
                self.tr("Second draft"),
                self.tr("Final")
                ]:
            self.mw.mdlStatus.appendRow(QStandardItem(text))

        # Plot
        self.mw.mdlPlots = plotModel()

        # Outline
        self.mw.mdlOutline = outlineModel()
        
        
        root = self.mw.mdlOutline.rootItem
        
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
                                       type="text")
                    if len(datas) == 2:
                        item.setData(Outline.setGoal.value, datas[1][0])
                    parent.appendChild(item)
            else:
                n = 0
                for i in range(datas[0][0]):
                    n += 1
                    item = outlineItem(title="{} {}".format(
                                                datas[0][1], 
                                                str(n)),
                                       type="folder")
                    parent.appendChild(item)
                    addElement(item, datas[1:])
            
        addElement(root, self.template)
        