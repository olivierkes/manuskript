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
        self.mdlPersosProxy = persosProxyModel()
        #self.mdlPersoProxyFilter = QSortFilterProxyModel()
        self.mdlPersosProxy.setSourceModel(self.mdlPersos)
        
        self.mdlPersosInfos = QStandardItemModel(1, 0)
        self.mdlPersosInfos.insertColumn(0, [QStandardItem("ID")])
        self.mdlPersosInfos.setHorizontalHeaderLabels(["Description"])
        #self.lstPersos.setModel(self.mdlPersos)
        self.lstPersos.setModel(self.mdlPersosProxy)
        
        self.tblPersoInfos.setModel(self.mdlPersosInfos)
        self.tblPersoInfos.setRowHidden(0, True)
        
        self.btnAddPerso.clicked.connect(self.createPerso)
        self.btnRmPerso.clicked.connect(self.removePerso)
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
            (Qt.red, self.tr("Scene"))
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
        self.viewRedacProperties.setModels(self.mdlOutline, self.mdlPersos, self.mdlLabels, self.mdlStatus)
        
        self.treePlanOutline.setModel(self.mdlOutline)
        self.cmbPlanPOV.setModels(self.mdlPersos, self.mdlOutline)
        self.redacEditor.setModel(self.mdlOutline)
        
        self.mprPlan = QDataWidgetMapper()
        self.mprPlan.setModel(self.mdlOutline)
        mapping = [
            (self.txtPlanSummarySentance, Outline.summarySentance.value),
            (self.txtPlanSummaryFull, Outline.summaryFull.value),
            (self.txtOutlineGoal, Outline.setGoal.value)
            ]
        for w, i in mapping:
                self.mprPlan.addMapping(w, i)
                
        self.treePlanOutline.selectionModel().currentChanged.connect(lambda idx: self.mprPlan.setRootIndex(idx.parent()))
        self.treePlanOutline.selectionModel().currentChanged.connect(self.mprPlan.setCurrentModelIndex)
        self.treePlanOutline.selectionModel().currentChanged.connect(self.cmbPlanPOV.setCurrentModelIndex)
        self.tabMain.currentChanged.connect(self.mprPlan.submit)
        
        self.treeRedacOutline.setSelectionModel(self.treePlanOutline.selectionModel())
        
        self.btnRedacAddFolder.clicked.connect(self.treeRedacOutline.addFolder)
        self.btnPlanAddFolder.clicked.connect(self.treePlanOutline.addFolder)
        self.btnRedacAddScene.clicked.connect(self.treeRedacOutline.addScene)
        self.btnPlanAddScene.clicked.connect(self.treePlanOutline.addScene)
        self.btnRedacRemoveItem.clicked.connect(self.outlineRemoveItems)
        self.btnPlanRemoveItem.clicked.connect(self.outlineRemoveItems)
        
        self.mprOutline = QDataWidgetMapper()
        self.mprOutline.setModel(self.mdlOutline)
        mapping = [
            (self.txtRedacSummarySentance, Outline.summarySentance.value),
            (self.txtRedacSummaryFull, Outline.summaryFull.value),
            (self.txtRedacNotes, Outline.notes.value)
            ]
        for w, i in mapping:
                self.mprOutline.addMapping(w, i)
        
        self.treeRedacOutline.selectionModel().currentChanged.connect(lambda idx: self.mprOutline.setRootIndex(idx.parent()))
        self.treeRedacOutline.selectionModel().currentChanged.connect(self.mprOutline.setCurrentModelIndex)
        
        self.treeRedacOutline.selectionModel().selectionChanged.connect(
            lambda: self.viewRedacProperties.selectionChanged(self.treeRedacOutline))
        self.treeRedacOutline.clicked.connect(
            lambda: self.viewRedacProperties.selectionChanged(self.treeRedacOutline))
        
        #self.treeRedacOutline.selectionModel().currentChanged.connect(self.redacEditor.setCurrentModelIndex)
        self.treeRedacOutline.selectionModel().selectionChanged.connect(self.redacEditor.setView)
        self.treeRedacOutline.selectionModel().currentChanged.connect(self.redacEditor.txtRedacText.setCurrentModelIndex)
        
        self.tabMain.currentChanged.connect(self.mprOutline.submit)
        
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
        i = self.mdlPersosProxy.mapToSource(self.lstPersos.currentIndex())
        self.mdlPersos.takeRow(i.row())
        self.mdlPersosInfos.takeColumn(i.row()+1)
        
    def changeCurrentPerso(self, trash=None):
        idx = self.mdlPersosProxy.mapToSource(self.lstPersos.currentIndex())
        
        self.mprPersos.setCurrentModelIndex(idx)
        pid = self.mdlPersos.item(idx.row(), Perso.ID.value).text()
        for c in range(self.mdlPersosInfos.columnCount()):
            pid2 = self.mdlPersosInfos.item(0, c).text()
            self.tblPersoInfos.setColumnHidden(c, c != 0 and pid != pid2)
        
        self.resizePersosInfos()
        
    def resizePersosInfos(self):
        self.tblPersoInfos.resizeColumnToContents(0)
        w = self.tblPersoInfos.viewport().width()
        w2 = self.tblPersoInfos.columnWidth(0)
        current = self.mdlPersosProxy.mapToSource(self.lstPersos.currentIndex()).row() + 1
        self.tblPersoInfos.setColumnWidth(current, w - w2)
        
        
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
        settings = QSettings(qApp.organizationName(), qApp.applicationName())
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        
        # Save data from models
        saveStandardItemModelXML(self.mdlFlatData, "{}/flatModel.xml".format(self.currentProject))
        saveStandardItemModelXML(self.mdlPersos, "{}/perso.xml".format(self.currentProject))
        saveStandardItemModelXML(self.mdlPersosInfos, "{}/persoInfos.xml".format(self.currentProject))
        saveStandardItemModelXML(self.mdlLabels, "{}/labels.xml".format(self.currentProject))
        saveStandardItemModelXML(self.mdlStatus, "{}/status.xml".format(self.currentProject))
        self.mdlOutline.saveToXML("{}/outline.xml".format(self.currentProject))
        
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

            for i in enchant.list_dicts():
                a = QAction(str(i[0]), self)
                a.setCheckable(True)
                a.triggered.connect(self.setDictionary)
                if str(i[0]) == enchant.get_default_language(): # "fr_CH"
                    a.setChecked(True)
                self.menuDictGroup.addAction(a)
                self.menuDict.addAction(a)

            self.menuTools.addMenu(self.menuDict)
            
            self.actSpellcheck.toggled.connect(self.redacEditor.toggleSpellcheck)
            self.dictChanged.connect(self.redacEditor.setDict)
            
            
        else:
            # No Spell check support
            self.actSpellcheck.setVisible(False)
            a = QAction(self.tr("Install PyEnchant to use spellcheck"), self)
            a.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
            a.triggered.connect(self.openPyEnchantWebPage)
            self.menuTools.addAction(a)
            
        self.btnRedacFullscreen.clicked.connect(self.redacEditor.showFullscreen)
            
    def setDictionary(self):
        for i in self.menuDictGroup.actions():
            if i.isChecked():
                self.dictChanged.emit(i.text().replace("&", ""))

    def openPyEnchantWebPage(self):
        QDesktopServices.openUrl(QUrl("http://pythonhosted.org/pyenchant/"))
        
        
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
        