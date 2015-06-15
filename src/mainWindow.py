#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *

from ui.mainWindow import *
from ui.helpLabel import helpLabel
from loadSave import *
from enums import *
from models.outlineModel import *
from models.persosProxyModel import *
from functions import *
from settingsWindow import *
import settings

# Spell checker support
try:
    import enchant
except ImportError:
    enchant = None

class MainWindow(QMainWindow, Ui_MainWindow):
    
    dictChanged = pyqtSignal(str)
    
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        
        self.readSettings()
        
        # UI
        self.setupMoreUi()
        
        # Word count
        self.mprWordCount = QSignalMapper(self)
        for t, i in [
            (self.txtSummarySentance, 0),
            (self.txtSummaryPara, 1),
            (self.txtSummaryPage, 2),
            (self.txtSummaryFull, 3)
            ]:
            t.textChanged.connect(self.mprWordCount.map)
            self.mprWordCount.setMapping(t, i)
        self.mprWordCount.mapped.connect(self.wordCount)
        
        # Snowflake Method Cycle
        self.mapperCycle = QSignalMapper(self)
        for t, i in [
            (self.btnStepTwo,   0),
            (self.btnStepThree, 1),
            (self.btnStepFour,  2),
            (self.btnStepFive,  3),
            (self.btnStepSix,   4),
            (self.btnStepSeven, 5),
            (self.btnStepEight, 6)
            ]:
            t.clicked.connect(self.mapperCycle.map)
            self.mapperCycle.setMapping(t, i)
            
        self.mapperCycle.mapped.connect(self.clickCycle)
        
        
        # Données
        self.mdlFlatData = QStandardItemModel(2, 8)
        self.tblDebugFlatData.setModel(self.mdlFlatData)
        
        self.mprSummary = QDataWidgetMapper()
        self.mprSummary.setModel(self.mdlFlatData)
        self.mprSummary.addMapping(self.txtSummarySentance, 0)
        self.mprSummary.addMapping(self.txtSummarySentance_2, 0)
        self.mprSummary.addMapping(self.txtSummaryPara, 1)
        self.mprSummary.addMapping(self.txtSummaryPara_2, 1)
        self.mprSummary.addMapping(self.txtPlotSummaryPara, 1)
        self.mprSummary.addMapping(self.txtSummaryPage, 2)
        self.mprSummary.addMapping(self.txtSummaryPage_2, 2)
        self.mprSummary.addMapping(self.txtPlotSummaryPage, 2)
        self.mprSummary.addMapping(self.txtSummaryFull, 3)
        self.mprSummary.addMapping(self.txtPlotSummaryFull, 3)
        self.mprSummary.setCurrentIndex(1)
        
        self.mprInfos = QDataWidgetMapper()
        self.mprInfos.setModel(self.mdlFlatData)
        self.mprInfos.addMapping(self.txtGeneralTitle, 0)
        self.mprInfos.addMapping(self.txtGeneralSubtitle, 1)
        self.mprInfos.addMapping(self.txtGeneralSerie, 2)
        self.mprInfos.addMapping(self.txtGeneralVolume, 3)
        self.mprInfos.addMapping(self.txtGeneralGenre, 4)
        self.mprInfos.addMapping(self.txtGeneralLicense, 5)
        self.mprInfos.addMapping(self.txtGeneralAuthor, 6)
        self.mprInfos.addMapping(self.txtGeneralEmail, 7)
        self.mprInfos.setCurrentIndex(0)
        
        # Persos
        self.mdlPersos = QStandardItemModel(0, 10)
        self.mdlPersosProxy = persosProxyModel() # None
        #self.mdlPersoProxyFilter = QSortFilterProxyModel()
        if self.mdlPersosProxy:
            self.mdlPersosProxy.setSourceModel(self.mdlPersos)
            self.lstPersos.setModel(self.mdlPersosProxy)
        else:
            self.lstPersos.setModel(self.mdlPersos)
        
        self.mdlPersosInfos = QStandardItemModel(1, 0)
        self.mdlPersosInfos.insertColumn(0, [QStandardItem("ID")])
        self.mdlPersosInfos.setHorizontalHeaderLabels(["Description"])
        #self.lstPersos.setModel(self.mdlPersos)
        
        self.tblPersoInfos.setModel(self.mdlPersosInfos)
        self.tblPersoInfos.setRowHidden(0, True)
        
        self.btnAddPerso.clicked.connect(self.createPerso)
        self.btnRmPerso.clicked.connect(self.removePerso)
        self.btnPersoColor.clicked.connect(self.chosePersoColor)
        self.btnPersoAddInfo.clicked.connect(lambda: self.mdlPersosInfos.insertRow(self.mdlPersosInfos.rowCount()))
        self.mprPersos = QDataWidgetMapper()
        self.mprPersos.setModel(self.mdlPersos)
        
        mapping = [
            (self.txtPersoName, Perso.name.value),
            (self.txtPersoMotivation, Perso.motivation.value),
            (self.txtPersoGoal, Perso.goal.value),
            (self.txtPersoConflict, Perso.conflict.value),
            (self.txtPersoEpiphany, Perso.epiphany.value),
            (self.txtPersoSummarySentance, Perso.summarySentance.value),
            (self.txtPersoSummaryPara, Perso.summaryPara.value),
            (self.txtPersoSummaryFull, Perso.summaryFull.value),
            (self.txtPersoNotes, Perso.notes.value)
            ]
        for w, i in mapping:
                self.mprPersos.addMapping(w, i)    
        self.mprPersos.addMapping(self.sldPersoImportance, Perso.importance.value, "importance")
        self.sldPersoImportance.importanceChanged.connect(self.mprPersos.submit)
        self.tabMain.currentChanged.connect(self.mprPersos.submit)
        
        self.mprPersos.setCurrentIndex(0)
        self.lstPersos.selectionModel().currentChanged.connect(self.changeCurrentPerso)
        self.tabPersos.currentChanged.connect(self.resizePersosInfos)
        
        # Labels
        self.mdlLabels = QStandardItemModel()
        for color, text in [
            (Qt.transparent, ""),
            (Qt.yellow, self.tr("Idea")),
            (Qt.green, self.tr("Note")),
            (Qt.blue, self.tr("Chapter")),
            (Qt.red, self.tr("Scene")),
            (Qt.cyan, self.tr("Research"))
            ]:
            self.mdlLabels.appendRow(QStandardItem(iconFromColor(color), text))
            
        # Status
        self.mdlStatus = QStandardItemModel()
        for text in [
                "",
                self.tr("TODO"),
                self.tr("First draft"),
                self.tr("Second draft"),
                self.tr("Final")
                ]:
            self.mdlStatus.appendRow(QStandardItem(text))
            
        # Outline
        self.mdlOutline = outlineModel()
        self.treeRedacOutline.setModel(self.mdlOutline)
        self.treePlanOutline.setModelPersos(self.mdlPersos)
        self.treePlanOutline.setModelLabels(self.mdlLabels)
        self.treePlanOutline.setModelStatus(self.mdlStatus)
        self.redacMetadata.setModels(self.mdlOutline, self.mdlPersos, self.mdlLabels, self.mdlStatus)
        self.outlineItemEditor.setModels(self.mdlOutline, self.mdlPersos, self.mdlLabels, self.mdlStatus)
        
        self.treePlanOutline.setModel(self.mdlOutline)
        self.redacEditor.setModel(self.mdlOutline)
        
        self.treePlanOutline.selectionModel().selectionChanged.connect(
            lambda: self.outlineItemEditor.selectionChanged(self.treePlanOutline))
        self.treePlanOutline.clicked.connect(
            lambda: self.outlineItemEditor.selectionChanged(self.treePlanOutline))
        
        self.treeRedacOutline.setSelectionModel(self.treePlanOutline.selectionModel())
        
        self.btnRedacAddFolder.clicked.connect(self.treeRedacOutline.addFolder)
        self.btnPlanAddFolder.clicked.connect(self.treePlanOutline.addFolder)
        self.btnRedacAddText.clicked.connect(self.treeRedacOutline.addText)
        self.btnPlanAddText.clicked.connect(self.treePlanOutline.addText)
        self.btnRedacRemoveItem.clicked.connect(self.outlineRemoveItems)
        self.btnPlanRemoveItem.clicked.connect(self.outlineRemoveItems)
        
        self.treeRedacOutline.selectionModel().selectionChanged.connect(
            lambda: self.redacMetadata.selectionChanged(self.treeRedacOutline))
        self.treeRedacOutline.clicked.connect(
            lambda: self.redacMetadata.selectionChanged(self.treeRedacOutline))
        
        #self.treeRedacOutline.selectionModel().currentChanged.connect(self.redacEditor.setCurrentModelIndex)
        self.treeRedacOutline.selectionModel().selectionChanged.connect(self.redacEditor.setView)
        self.treeRedacOutline.selectionModel().currentChanged.connect(self.redacEditor.txtRedacText.setCurrentModelIndex)
        
        self.treeRedacOutline.selectionModel().selectionChanged.connect(self.outlineSelectionChanged)
        self.treeRedacOutline.selectionModel().selectionChanged.connect(self.outlineSelectionChanged)
        self.treePlanOutline.selectionModel().selectionChanged.connect(self.outlineSelectionChanged)
        self.treePlanOutline.selectionModel().selectionChanged.connect(self.outlineSelectionChanged)
        
        self.sldCorkSizeFactor.valueChanged.connect(self.redacEditor.setCorkSizeFactor)
        self.btnRedacFolderCork.toggled.connect(self.sldCorkSizeFactor.setVisible)
        self.btnRedacFolderText.clicked.connect(lambda v: self.redacEditor.setFolderView("text"))
        self.btnRedacFolderCork.clicked.connect(lambda v: self.redacEditor.setFolderView("cork"))
        self.btnRedacFolderOutline.clicked.connect(lambda v: self.redacEditor.setFolderView("outline"))
        
        # Main Menu
        self.actLabels.triggered.connect(self.settingsLabel)
        self.actStatus.triggered.connect(self.settingsStatus)
        self.actQuit.triggered.connect(self.close)
        self.generateViewMenu()
        
        #Debug
        self.mdlFlatData.setVerticalHeaderLabels(["Infos générales", "Summary"])
        self.tblDebugFlatData.setModel(self.mdlFlatData)
        self.tblDebugPersos.setModel(self.mdlPersos)
        self.tblDebugPersosInfos.setModel(self.mdlPersosInfos)
        self.treeDebugOutline.setModel(self.mdlOutline)
        self.lstDebugLabels.setModel(self.mdlLabels)
        self.lstDebugStatus.setModel(self.mdlStatus)
        
        
        # Playing with qStyle
        self.cmbStyle.addItems(list(QStyleFactory.keys()))
        self.cmbStyle.setCurrentIndex([i.lower() for i in list(QStyleFactory.keys())].index(qApp.style().objectName()))
        self.cmbStyle.currentIndexChanged[str].connect(qApp.setStyle)
        
        self.loadProject("test_project")
    
####################################################################################################
#                                             OUTLINE                                              #
####################################################################################################
    
    def outlineSelectionChanged(self):
        if len(self.treeRedacOutline.selectionModel().selection().indexes()) == 0:
            hidden = False
        else:
            idx = self.treeRedacOutline.currentIndex()
            if idx.isValid():
                hidden = not idx.internalPointer().isFolder()
            else:
                hidden = False
            
        self.btnRedacFolderText.setHidden(hidden)
        self.btnRedacFolderCork.setHidden(hidden)
        self.btnRedacFolderOutline.setHidden(hidden)
        self.sldCorkSizeFactor.setHidden(hidden)
        
    def outlineRemoveItems(self):
        for idx in self.treeRedacOutline.selectedIndexes():
            if idx.isValid():
                self.mdlOutline.removeIndex(idx)
    
    
####################################################################################################
#                                             PERSOS                                               #
####################################################################################################

    def createPerso(self):
        "Creates a perso by adding a row in mdlPersos and a column in mdlPersosInfos with same ID"
        p = QStandardItem(self.tr("New character"))
        self.mdlPersos.appendRow(p)
        pid = self.getPersosID()
        self.checkPersosID()  # Attributes a persoID (which is logically pid)
        self.setPersoColor(self.mdlPersos.rowCount()-1, randomColor(QColor(Qt.white)))
        
        # Add column in persos infos
        self.mdlPersosInfos.insertColumn(self.mdlPersosInfos.columnCount(), [QStandardItem(pid)])
        self.mdlPersosInfos.setHorizontalHeaderItem(self.mdlPersosInfos.columnCount()-1, QStandardItem("Valeur"))
            
    def getPersosID(self):
        "Returns an unused perso ID (row 1)"
        vals = []
        for i in range(self.mdlPersos.rowCount()):
            item = self.mdlPersos.item(i, Perso.ID.value)
            if item and item.text():
                vals.append(int(item.text()))
                
        k = 0
        while k in vals: k += 1
        return str(k)
            
    def checkPersosID(self):
        "Checks whether some persos ID (row 1) are empty, if so, assign an ID"
        empty = []
        for i in range(self.mdlPersos.rowCount()):
            item = self.mdlPersos.item(i, Perso.ID.value)
            if not item:
                item = QStandardItem()
                item.setText(self.getPersosID())
                self.mdlPersos.setItem(i, Perso.ID.value, item)
        
    def removePerso(self):
        if self.mdlPersosProxy:
            i = self.mdlPersosProxy.mapToSource(self.lstPersos.currentIndex())
        else:
            i = self.lstPersos.currentIndex()
        self.mdlPersos.takeRow(i.row())
        self.mdlPersosInfos.takeColumn(i.row()+1)
        
    def changeCurrentPerso(self, trash=None):
        if self.mdlPersosProxy:
            idx = self.mdlPersosProxy.mapToSource(self.lstPersos.currentIndex())
        else:
            idx = self.lstPersos.currentIndex()
        
        self.mprPersos.setCurrentModelIndex(idx)
        
        # Button color
        self.updatePersoColor()
        
        # detailed infos
        pid = self.mdlPersos.item(idx.row(), Perso.ID.value).text()
        for c in range(self.mdlPersosInfos.columnCount()):
            pid2 = self.mdlPersosInfos.item(0, c).text()
            self.tblPersoInfos.setColumnHidden(c, c != 0 and pid != pid2)
        
        self.resizePersosInfos()
        
    def updatePersoColor(self):  
        if self.mdlPersosProxy:
            idx = self.mdlPersosProxy.mapToSource(self.lstPersos.currentIndex())
        else:
            idx = self.lstPersos.currentIndex()
            
        px = QPixmap(32, 32)
        icon = self.mdlPersos.item(idx.row()).icon()
        if icon:
            px.fill(iconColor(icon))
        self.btnPersoColor.setIcon(QIcon(px))
    
    def resizePersosInfos(self):
        self.tblPersoInfos.resizeColumnToContents(0)
        w = self.tblPersoInfos.viewport().width()
        w2 = self.tblPersoInfos.columnWidth(0)
        
        if self.mdlPersosProxy:
            current = self.mdlPersosProxy.mapToSource(self.lstPersos.currentIndex()).row() + 1
        else:
            current = self.lstPersos.currentIndex().row() + 1
        
        self.tblPersoInfos.setColumnWidth(current, w - w2)
        
    def chosePersoColor(self):
        if self.mdlPersosProxy:
            idx = self.mdlPersosProxy.mapToSource(self.lstPersos.currentIndex())
        else:
            idx = self.lstPersos.currentIndex()
            
        item = self.mdlPersos.item(idx.row(), Perso.name.value)
        if item:
            color = iconColor(item.icon())
        else:
            color = Qt.white
        self.colorDialog = QColorDialog(color, self)
        color = self.colorDialog.getColor(color)
        self.setPersoColor(idx.row(), color)
        self.updatePersoColor()
    
    def setPersoColor(self, row, color):
        px = QPixmap(32, 32)
        px.fill(color)
        self.mdlPersos.item(row, Perso.name.value).setIcon(QIcon(px))
        
        
####################################################################################################
#                                             GENERAL                                              #
####################################################################################################
        
    def loadProject(self, project):
        self.currentProject = project
        loadStandardItemModelXML(self.mdlFlatData, "{}/flatModel.xml".format(project))
        loadStandardItemModelXML(self.mdlPersos, "{}/perso.xml".format(project))
        loadStandardItemModelXML(self.mdlPersosInfos, "{}/persoInfos.xml".format(project))
        loadStandardItemModelXML(self.mdlLabels, "{}/labels.xml".format(project))
        loadStandardItemModelXML(self.mdlStatus, "{}/status.xml".format(project))
        self.mdlOutline.loadFromXML("{}/outline.xml".format(project))
        settings.load("{}/settings.pickle".format(project))
        
        # Stuff from settings
        self.generateViewMenu()
        self.sldCorkSizeFactor.setValue(settings.corkSizeFactor)
        self.actSpellcheck.setChecked(settings.spellcheck)
        self.updateMenuDict()
        self.setDictionary()
        self.redacEditor.setFolderView(settings.folderView)
        if settings.folderView == "text":
            self.btnRedacFolderText.setChecked(True)
        elif settings.folderView == "cork":
            self.btnRedacFolderCork.setChecked(True)
        elif settings.folderView == "outline":
            self.btnRedacFolderOutline.setChecked(True)
        self.tabMain.setCurrentIndex(settings.lastTab)
        self.treeRedacOutline.setCurrentIndex(self.mdlOutline.indexFromPath(settings.lastIndex))
        
        
        # Stuff
        self.checkPersosID()
        # Adds header labels
        self.mdlPersos.setHorizontalHeaderLabels(
	  [i.name for i in Perso])
                
    def readSettings(self):
        # Load State and geometry
        settings = QSettings(qApp.organizationName(), qApp.applicationName())
        self.restoreGeometry(settings.value("geometry"))
        self.restoreState(settings.value("windowState"))
        
    def closeEvent(self, event):
        # Save State and geometry
        stgs = QSettings(qApp.organizationName(), qApp.applicationName())
        stgs.setValue("geometry", self.saveGeometry())
        stgs.setValue("windowState", self.saveState())
        
        # Specific settings to save before quitting
        settings.lastTab = self.tabMain.currentIndex()
        if len(self.treeRedacOutline.selectedIndexes()) == 0:
            sel = QModelIndex()
        else:
            sel = self.treeRedacOutline.currentIndex()
        settings.lastIndex = self.mdlOutline.pathToIndex(sel)
        
        # Save data from models
        saveStandardItemModelXML(self.mdlFlatData, "{}/flatModel.xml".format(self.currentProject))
        saveStandardItemModelXML(self.mdlPersos, "{}/perso.xml".format(self.currentProject))
        saveStandardItemModelXML(self.mdlPersosInfos, "{}/persoInfos.xml".format(self.currentProject))
        saveStandardItemModelXML(self.mdlLabels, "{}/labels.xml".format(self.currentProject))
        saveStandardItemModelXML(self.mdlStatus, "{}/status.xml".format(self.currentProject))
        self.mdlOutline.saveToXML("{}/outline.xml".format(self.currentProject))
        settings.save("{}/settings.pickle".format(self.currentProject))
        
        # closeEvent
        QMainWindow.closeEvent(self, event)
        
    def clickCycle(self, i):
        if i == 0: # step 2 - paragraph summary
            self.tabMain.setCurrentIndex(1)
            self.tabSummary.setCurrentIndex(1)
        if i == 1: # step 3 - characters summary
            self.tabMain.setCurrentIndex(2)
            self.tabPersos.setCurrentIndex(0)
        if i == 2: # step 4 - page summary
            self.tabMain.setCurrentIndex(1)
            self.tabSummary.setCurrentIndex(2)
        if i == 3: # step 5 - characters description
            self.tabMain.setCurrentIndex(2)
            self.tabPersos.setCurrentIndex(1)
        if i == 4: # step 6 - four page synopsis
            self.tabMain.setCurrentIndex(1)
            self.tabSummary.setCurrentIndex(3)
        if i == 5: # step 7 - full character charts
            self.tabMain.setCurrentIndex(2)
            self.tabPersos.setCurrentIndex(2)
        if i == 6: # step 8 - scene list
            self.tabMain.setCurrentIndex(3)
        
    def wordCount(self, i):
        
        src= {
            0:self.txtSummarySentance,
            1:self.txtSummaryPara,
            2:self.txtSummaryPage,
            3:self.txtSummaryFull
            }[i]
        
        lbl = {
            0:self.lblSummaryWCSentance,
            1:self.lblSummaryWCPara,
            2:self.lblSummaryWCPage,
            3:self.lblSummaryWCFull
            }[i]
        
        wc = wordCount(src.toPlainText())
        if i in [2, 3]: pages = self.tr(" (~{} pages)").format(int(wc / 25) / 10.)
        else: pages = ""
        lbl.setText(self.tr("Words: {}{}").format(wc, pages))
        
        
    def setupMoreUi(self):
        # Splitters
        self.splitterPersos.setStretchFactor(0, 25)
        self.splitterPersos.setStretchFactor(1, 75)
        
        self.splitterPlot.setStretchFactor(0, 20)
        self.splitterPlot.setStretchFactor(1, 60)
        self.splitterPlot.setStretchFactor(2, 30)
        
        self.splitterOutlineH.setStretchFactor(0, 25)
        self.splitterOutlineH.setStretchFactor(1, 75)
        self.splitterOutlineV.setStretchFactor(0, 75)
        self.splitterOutlineV.setStretchFactor(1, 25)
        
        
        self.splitterRedac.setStretchFactor(0, 20)
        self.splitterRedac.setStretchFactor(1, 60)
        self.splitterRedac.setStretchFactor(2, 20)
        
        # Help box
        references = [
            (self.lytTabOverview,
             self.tr("Enter infos about your book, and yourself.")),
            (self.lytTabSummary,
             self.tr("Take time to think about a one sentance (~50 words) summary of your book. Then expand it to a paragraph, then to a page, then to a full summary.")),
            (self.lytTabPersos,
             self.tr("Create your characters.")),
            (self.lytTabPlot,
             self.tr("Develop plots.")),
            (self.lytTabOutline,
             self.tr("Create the outline of your masterpiece.")),
            (self.lytTabRedac,
             self.tr("Write.")),
            (self.lytTabDebug,
             self.tr("Debug infos. Sometimes useful."),)
            ]

        for widget, text in references:
            label = helpLabel(text)
            self.actShowHelp.toggled.connect(label.setVisible)
            widget.layout().insertWidget(0, label)
        
        self.actShowHelp.setChecked(False)
        
        # Spellcheck
        if enchant:
            self.menuDict = QMenu(self.tr("Dictionary"))
            self.menuDictGroup = QActionGroup(self)
            self.updateMenuDict()
            self.menuTools.addMenu(self.menuDict)
            
            self.actSpellcheck.toggled.connect(self.toggleSpellcheck)
            self.dictChanged.connect(self.redacEditor.setDict)
            self.dictChanged.connect(self.redacMetadata.setDict)
            self.dictChanged.connect(self.outlineItemEditor.setDict)
            
        else:
            # No Spell check support
            self.actSpellcheck.setVisible(False)
            a = QAction(self.tr("Install PyEnchant to use spellcheck"), self)
            a.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
            a.triggered.connect(self.openPyEnchantWebPage)
            self.menuTools.addAction(a)
            
        self.btnRedacFullscreen.clicked.connect(self.redacEditor.showFullscreen)
            
    def updateMenuDict(self):
        self.menuDict.clear()
        for i in enchant.list_dicts():
            a = QAction(str(i[0]), self)
            a.setCheckable(True)
            a.triggered.connect(self.setDictionary)
            if settings.dict == None:
                settings.dict = enchant.get_default_language()
            if str(i[0]) == settings.dict:
                a.setChecked(True)
            self.menuDictGroup.addAction(a)
            self.menuDict.addAction(a)
            
    def setDictionary(self):
        for i in self.menuDictGroup.actions():
            if i.isChecked():
                self.dictChanged.emit(i.text().replace("&", ""))
                settings.dict = i.text().replace("&", "")

    def openPyEnchantWebPage(self):
        QDesktopServices.openUrl(QUrl("http://pythonhosted.org/pyenchant/"))
        
    def toggleSpellcheck(self, val):
        settings.spellcheck = val
        self.redacEditor.toggleSpellcheck(val)
        self.redacMetadata.toggleSpellcheck(val)
        self.outlineItemEditor.toggleSpellcheck(val)
        
####################################################################################################
#                                            SETTINGS                                              #
####################################################################################################

    def settingsLabel(self):
        self.settingsWindow(0)
        
    def settingsStatus(self):
        self.settingsWindow(1)
        
    def settingsWindow(self, tab=None):
        self.sw = settingsWindow(self)
        self.sw.hide()
        self.sw.setWindowModality(Qt.ApplicationModal)
        self.sw.setWindowFlags(Qt.Dialog)
        r = self.sw.geometry()
        r2 = self.geometry()
        self.sw.move(r2.center() - r.center())
        if tab:
            self.sw.tabWidget.setCurrentIndex(tab)
        self.sw.show()
        
####################################################################################################
#                                           VIEW MENU                                              #
####################################################################################################
        
    def generateViewMenu(self):    
        
        values = [
                (self.tr("Nothing"), "Nothing"),
                (self.tr("POV"), "POV"),
                (self.tr("Label"), "Label"),
                (self.tr("Progress"), "Progress"),
                (self.tr("Compile"), "Compile"),
                ]
        
        menus = [
            (self.tr("Tree"), "Tree"),
            (self.tr("Index cards"), "Cork"),
            (self.tr("Outline"), "Outline")
            ]
        
        submenus = {
            "Tree": [
                (self.tr("Icon color"), "Icon"),
                (self.tr("Text color"), "Text"),
                (self.tr("Background color"), "Background"),
                ],
            "Cork": [
                (self.tr("Icon"), "Icon"),
                (self.tr("Text"), "Text"),
                (self.tr("Background"), "Background"),
                (self.tr("Border"), "Border"),
                (self.tr("Corner"), "Corner"),
                ],
            "Outline": [
                (self.tr("Icon color"), "Icon"),
                (self.tr("Text color"), "Text"),
                (self.tr("Background color"), "Background"),
                ],
            }
            
        self.menuView.clear()
            
        #print("Generating menus with", settings.viewSettings)
            
        for mnu, mnud in menus:
            m = QMenu(mnu, self.menuView)
            for s, sd in submenus[mnud]:
                m2 = QMenu(s, m)
                agp = QActionGroup(m2)
                for v, vd in values:
                    a = QAction(v, m)
                    a.setCheckable(True)
                    a.setData("{},{},{}".format(mnud, sd, vd))
                    if settings.viewSettings[mnud][sd] == vd:
                        a.setChecked(True)
                    a.triggered.connect(self.setViewElement)
                    agp.addAction(a)
                    m2.addAction(a)
                m.addMenu(m2)
            self.menuView.addMenu(m)
        
    def setViewElement(self):
        action = self.sender()
        item, part, element = action.data().split(",")
        settings.viewSettings[item][part] = element