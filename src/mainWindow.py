#!/usr/bin/env python
#--!-- coding: utf8 --!--

from qt import *

from ui.mainWindow import *
from ui.helpLabel import helpLabel
from ui.compileDialog import compileDialog
from loadSave import *
from enums import *
from models.outlineModel import *
from models.persosModel import *
from models.plotModel import *
from ui.views.outlineDelegates import outlinePersoDelegate
from ui.views.plotDelegate import plotDelegate
#from models.persosProxyModel import *
from functions import *
from settingsWindow import *
import settings
import imp

# Spellcheck support
try:
    import enchant
except ImportError:
    enchant = None


class MainWindow(QMainWindow, Ui_MainWindow):

    dictChanged = pyqtSignal(str)

    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.currentProject = None

        self.readSettings()

        # UI
        self.setupMoreUi()

        # Welcome
        self.welcome.updateValues()
        #self.welcome.btnCreate.clicked.connect
        self.stack.setCurrentIndex(0)

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
        self.cmbSummary.currentIndexChanged.connect(self.summaryPageChanged)
        self.cmbSummary.setCurrentIndex(0)
        self.cmbSummary.currentIndexChanged.emit(0)

        # Main Menu
        for i in [self.actSave, self.actSaveAs, self.actCloseProject,
                  self.menuEdit, self.menuMode, self.menuView, self.menuTools,
                  self.menuHelp]:
            i.setEnabled(False)

        self.actOpen.triggered.connect(self.welcome.openFile)
        self.actSave.triggered.connect(self.saveDatas)
        self.actSaveAs.triggered.connect(self.welcome.saveAsFile)
        self.actCompile.triggered.connect(self.doCompile)
        self.actLabels.triggered.connect(self.settingsLabel)
        self.actStatus.triggered.connect(self.settingsStatus)
        self.actSettings.triggered.connect(self.settingsWindow)
        self.actCloseProject.triggered.connect(self.closeProject)
        self.actQuit.triggered.connect(self.close)
        self.generateViewMenu()

        self.makeUIConnections()

        #self.loadProject(os.path.join(appPath(), "test_project.zip"))

###############################################################################
# SUMMARY
###############################################################################

    def summaryPageChanged(self, index):
        fractalButtons = [
            self.btnStepTwo,
            self.btnStepThree,
            self.btnStepFive,
            self.btnStepSeven,
            ]
        for b in fractalButtons:
            b.setVisible(fractalButtons.index(b) == index)

###############################################################################
# OUTLINE
###############################################################################

    def outlineRemoveItemsRedac(self):
        self.treeRedacOutline.delete()
                
    def outlineRemoveItemsOutline(self):
        self.treeOutlineOutline.delete()
                
###############################################################################
# PERSOS
###############################################################################

    #def createPerso(self):
        #"""Creates a perso by adding a row in mdlPersos
        #and a column in mdlPersosInfos with same ID"""
        #p = QStandardItem(self.tr("New character"))
        #pid = self.getPersosID()
        ##self.checkPersosID()  # Attributes a persoID (which is logically pid)
        #self.mdlPersos.appendRow([p, QStandardItem(pid), QStandardItem("0")])

        #self.setPersoColor(self.mdlPersos.rowCount() - 1,
                           #randomColor(QColor(Qt.white)))

        ## Add column in persos infos
        #self.mdlPersosInfos.insertColumn(self.mdlPersosInfos.columnCount(),
                                         #[QStandardItem(pid)])
        #self.mdlPersosInfos.setHorizontalHeaderItem(
            #self.mdlPersosInfos.columnCount() - 1,
            #QStandardItem("Valeur"))

    #def getPersosID(self):
        #"""Returns an unused perso ID (row 1)."""
        #vals = []
        #for i in range(self.mdlPersos.rowCount()):
            #item = self.mdlPersos.item(i, Perso.ID.value)
            #if item and item.text():
                #vals.append(int(item.text()))

        #k = 0
        #while k in vals:
            #k += 1
        #return str(k)

    #def checkPersosID(self):
        #"""Checks whether some persos ID (row 1) are empty.
        #If so, assign an ID"""
        #for i in range(self.mdlPersos.rowCount()):
            #item = self.mdlPersos.item(i, Perso.ID.value)
            #if not item:
                #item = QStandardItem()
                #item.setText(self.getPersosID())
                #self.mdlPersos.setItem(i, Perso.ID.value, item)

    #def removePerso(self):
        #if self.mdlPersosProxy:
            #i = self.mdlPersosProxy.mapToSource(self.lstPersos.currentIndex())
        #else:
            #i = self.lstPersos.currentIndex()
        #self.mdlPersos.takeRow(i.row())
        #self.mdlPersosInfos.takeColumn(i.row() + 1)

    def changeCurrentPerso(self, trash=None):

        index = self.lstPersos.currentPersoIndex()

        if not index.isValid():
            self.tabPlot.setEnabled(False)
            return

        self.tabPersos.setEnabled(True)

        for w in [
            self.txtPersoName,
            self.sldPersoImportance,
            self.txtPersoMotivation,
            self.txtPersoGoal,
            self.txtPersoConflict,
            self.txtPersoEpiphany,
            self.txtPersoSummarySentance,
            self.txtPersoSummaryPara,
            self.txtPersoSummaryFull,
            self.txtPersoNotes,
            ]:
            w.setCurrentModelIndex(index)

        # Button color
        self.mdlPersos.updatePersoColor(index)

        # Perso Infos
        self.tblPersoInfos.setRootIndex(index)

        if self.mdlPersos.rowCount(index):
            self.updatePersoInfoView()

        #if self.mdlPersosProxy:
            #idx = self.mdlPersosProxy.mapToSource(self.lstPersos.currentIndex())
        #else:
            #idx = self.lstPersos.currentIndex()

        #self.mprPersos.setCurrentModelIndex(idx)


        ## detailed infos
        #pid = self.mdlPersos.item(idx.row(), Perso.ID.value).text()
        #for c in range(self.mdlPersosInfos.columnCount()):
            #pid2 = self.mdlPersosInfos.item(0, c).text()
            #self.tblPersoInfos.setColumnHidden(c, c != 0 and pid != pid2)

        #self.resizePersosInfos()

    def updatePersoInfoView(self):
        # Hide columns
        for i in range(self.mdlPersos.columnCount()):
            self.tblPersoInfos.hideColumn(i)
        self.tblPersoInfos.showColumn(Perso.infoName.value)
        self.tblPersoInfos.showColumn(Perso.infoData.value)

        self.tblPersoInfos.horizontalHeader().setSectionResizeMode(
            Perso.infoName.value, QHeaderView.ResizeToContents)
        self.tblPersoInfos.horizontalHeader().setSectionResizeMode(
            Perso.infoData.value, QHeaderView.Stretch)
        self.tblPersoInfos.verticalHeader().hide()

    #def updatePersoColor(self):
        #if self.mdlPersosProxy:
            #idx = self.mdlPersosProxy.mapToSource(self.lstPersos.currentIndex())
        #else:
            #idx = self.lstPersos.currentIndex()

        #icon = self.mdlPersos.item(idx.row()).icon()
        #color = iconColor(icon).name() if icon else ""
        #self.btnPersoColor.setStyleSheet("background:{};".format(color))

    #def resizePersosInfos(self):
        #self.tblPersoInfos.resizeColumnToContents(0)
        #w = self.tblPersoInfos.viewport().width()
        #w2 = self.tblPersoInfos.columnWidth(0)

        #if self.mdlPersosProxy:
            #current = self.mdlPersosProxy.mapToSource(
                           #self.lstPersos.currentIndex()).row() + 1
        #else:
            #current = self.lstPersos.currentIndex().row() + 1

        #self.tblPersoInfos.setColumnWidth(current, w - w2)

    #def chosePersoColor(self):
        #if self.mdlPersosProxy:
            #idx = self.mdlPersosProxy.mapToSource(self.lstPersos.currentIndex())
        #else:
            #idx = self.lstPersos.currentIndex()

        #item = self.mdlPersos.item(idx.row(), Perso.name.value)
        #if item:
            #color = iconColor(item.icon())
        #else:
            #color = Qt.white
        #self.colorDialog = QColorDialog(color, self)
        #color = self.colorDialog.getColor(color)
        #if color.isValid():
            #self.setPersoColor(idx.row(), color)
            #self.updatePersoColor()

    #def setPersoColor(self, row, color):
        #px = QPixmap(32, 32)
        #px.fill(color)
        #self.mdlPersos.item(row, Perso.name.value).setIcon(QIcon(px))

###############################################################################
# PLOTS
###############################################################################

    def changeCurrentPlot(self):
        index = self.lstPlots.currentPlotIndex()

        if not index.isValid():
            self.tabPlot.setEnabled(False)
            return

        self.tabPlot.setEnabled(True)
        self.txtPlotName.setCurrentModelIndex(index)
        self.txtPlotDescription.setCurrentModelIndex(index)
        self.txtPlotResult.setCurrentModelIndex(index)
        self.sldPlotImportance.setCurrentModelIndex(index)
        self.lstPlotPerso.setRootIndex(index.sibling(index.row(),
                                                     Plot.persos.value))
        subplotindex = index.sibling(index.row(), Plot.subplots.value)
        self.lstSubPlots.setRootIndex(subplotindex)
        if self.mdlPlots.rowCount(subplotindex):
            self.updateSubPlotView()

        #self.txtSubPlotSummary.setCurrentModelIndex(QModelIndex())
        self.txtSubPlotSummary.setEnabled(False)
        self._updatingSubPlot = True
        self.txtSubPlotSummary.setPlainText("")
        self._updatingSubPlot = False
        self.lstPlotPerso.selectionModel().clear()

    def updateSubPlotView(self):
        # Hide columns
        for i in range(self.mdlPlots.columnCount()):
            self.lstSubPlots.hideColumn(i)
        self.lstSubPlots.showColumn(Subplot.name.value)
        self.lstSubPlots.showColumn(Subplot.meta.value)

        self.lstSubPlots.horizontalHeader().setSectionResizeMode(
            Subplot.name.value, QHeaderView.Stretch)
        self.lstSubPlots.horizontalHeader().setSectionResizeMode(
            Subplot.meta.value, QHeaderView.ResizeToContents)
        self.lstSubPlots.verticalHeader().hide()
        
    def changeCurrentSubPlot(self, index):
        # Got segfaults when using textEditView model system, so ad hoc stuff.
        index = index.sibling(index.row(), Subplot.summary.value)
        item = self.mdlPlots.itemFromIndex(index)
        if not item:
            self.txtSubPlotSummary.setEnabled(False)
            return
        self.txtSubPlotSummary.setEnabled(True)
        txt = item.text()
        self._updatingSubPlot = True
        self.txtSubPlotSummary.setPlainText(txt)
        self._updatingSubPlot = False

    def updateSubPlotSummary(self):
        if self._updatingSubPlot:
            return

        index = self.lstSubPlots.currentIndex()
        if not index.isValid():
            return
        index = index.sibling(index.row(), Subplot.summary.value)
        item = self.mdlPlots.itemFromIndex(index)

        self._updatingSubPlot = True
        item.setText(self.txtSubPlotSummary.toPlainText())
        self._updatingSubPlot = False
        
    def plotPersoSelectionChanged(self):
        "Enables or disables remove plot perso button."
        self.btnRmPlotPerso.setEnabled(
            len(self.lstPlotPerso.selectedIndexes()) != 0)

###############################################################################
# LOAD AND SAVE
###############################################################################

    def loadProject(self, project, loadFromFile=True):
        """Loads the project ``project``.

        If ``loadFromFile`` is False, then it does not load datas from file.
        It assumes that the datas have been populated in a different way."""
        if loadFromFile and not os.path.exists(project):
            print(self.tr("The file {} does not exist. Try again.").format(project))
            self.statusBar().showMessage(
                self.tr("The file {} does not exist. Try again.").format(project),
                5000)
            return


        if loadFromFile:
            # Load empty settings
            imp.reload(settings)

            # Load data
            self.loadEmptyDatas()
            self.loadDatas(project)

        self.makeConnections()

        # Load settings
        for i in settings.openIndexes:
            idx = self.mdlOutline.indexFromPath(i)
            self.mainEditor.setCurrentModelIndex(idx, newTab = True)
        self.generateViewMenu()
        self.mainEditor.sldCorkSizeFactor.setValue(settings.corkSizeFactor)
        self.actSpellcheck.setChecked(settings.spellcheck)
        self.toggleSpellcheck(settings.spellcheck)
        self.updateMenuDict()
        self.setDictionary()

        self.mainEditor.setFolderView(settings.folderView)
        self.mainEditor.updateFolderViewButtons(settings.folderView)
        self.tabMain.setCurrentIndex(settings.lastTab)
        self.mainEditor.updateCorkBackground()

        # Set autosave
        self.saveTimer = QTimer()
        self.saveTimer.setInterval(settings.autoSaveDelay * 60 * 1000)
        self.saveTimer.setSingleShot(False)
        self.saveTimer.timeout.connect(self.saveDatas)
        if settings.autoSave:
            self.saveTimer.start()

        # Set autosave if no changes
        self.saveTimerNoChanges = QTimer()
        self.saveTimerNoChanges.setInterval(settings.autoSaveNoChangesDelay
                                                                        * 1000)
        self.saveTimerNoChanges.setSingleShot(True)
        self.mdlFlatData.dataChanged.connect(self.startTimerNoChanges)
        self.mdlOutline.dataChanged.connect(self.startTimerNoChanges)
        self.mdlPersos.dataChanged.connect(self.startTimerNoChanges)
        self.mdlPlots.dataChanged.connect(self.startTimerNoChanges)
        #self.mdlPersosInfos.dataChanged.connect(self.startTimerNoChanges)
        self.mdlStatus.dataChanged.connect(self.startTimerNoChanges)
        self.mdlLabels.dataChanged.connect(self.startTimerNoChanges)

        self.saveTimerNoChanges.timeout.connect(self.saveDatas)
        self.saveTimerNoChanges.stop()

        # UI
        for i in [self.actSave, self.actSaveAs, self.actCloseProject,
                  self.menuEdit, self.menuMode, self.menuView, self.menuTools,
                  self.menuHelp]:
            i.setEnabled(True)
        #FIXME: set Window's name: project name

        # Stuff
        #self.checkPersosID()  # Should'n be necessary any longer

        self.currentProject = project
        QSettings().setValue("lastProject", project)

        # Show main Window
        self.stack.setCurrentIndex(1)

    def closeProject(self):
        # Save datas
        self.saveDatas()

        self.currentProject = None
        QSettings().setValue("lastProject", "")

        # Clear datas
        self.loadEmptyDatas()

        self.saveTimer.stop()

        # UI
        for i in [self.actSave, self.actSaveAs, self.actCloseProject,
                  self.menuEdit, self.menuMode, self.menuView, self.menuTools,
                  self.menuHelp]:
            i.setEnabled(False)

        # Reload recent files
        self.welcome.updateValues()

        # Show welcome dialog
        self.stack.setCurrentIndex(0)

    def readSettings(self):
        # Load State and geometry
        sttgns = QSettings(qApp.organizationName(), qApp.applicationName())
        if sttgns.contains("geometry"):
            self.restoreGeometry(sttgns.value("geometry"))
        if sttgns.contains("windowState"):
            self.restoreState(sttgns.value("windowState"))
        if sttgns.contains("metadataState"):
            state = [False if v == "false" else True for v in sttgns.value("metadataState")]
            self.redacMetadata.restoreState(state)
        if sttgns.contains("redacInfosState"):
            self.tabRedacInfos.setCurrentIndex(int(sttgns.value("redacInfosState")))
        if sttgns.contains("cheatSheetState"):
            state = False if sttgns.value("cheatSheetState") == "false" else True
            self.grpCheatSheet.restoreState(state)
        if sttgns.contains("searchState"):
            state = False if sttgns.value("searchState") == "false" else True
            self.grpSearch.restoreState(state)
        if sttgns.contains("revisionsState"):
            state = [False if v == "false" else True for v in sttgns.value("revisionsState")]
            self.redacMetadata.revisions.restoreState(state)
        
        
    def closeEvent(self, event):
        # Save State and geometry and other things
        sttgns = QSettings(qApp.organizationName(), qApp.applicationName())
        sttgns.setValue("geometry", self.saveGeometry())
        sttgns.setValue("windowState", self.saveState())
        sttgns.setValue("metadataState", self.redacMetadata.saveState())
        sttgns.setValue("metadataState", self.redacMetadata.saveState())
        sttgns.setValue("redacInfosState", self.tabRedacInfos.currentIndex())
        sttgns.setValue("cheatSheetState", self.grpCheatSheet.saveState())
        sttgns.setValue("searchState", self.grpSearch.saveState())
        sttgns.setValue("revisionsState", self.redacMetadata.revisions.saveState())
        
        # Specific settings to save before quitting
        settings.lastTab = self.tabMain.currentIndex()

        if self.currentProject:
            # Remembering the current items
            sel = []
            for i in range(self.mainEditor.tab.count()):
                sel.append(self.mdlOutline.pathToIndex(self.mainEditor.tab.widget(i).currentIndex))
            settings.openIndexes = sel

        # Save data from models
        if self.currentProject and settings.saveOnQuit:
            self.saveDatas()

        # closeEvent
        #QMainWindow.closeEvent(self, event)  # Causin segfaults?

    def startTimerNoChanges(self):
        if settings.autoSaveNoChanges:
            self.saveTimerNoChanges.start()

    def saveDatas(self, projectName=None):
        """Saves the current project (in self.currentProject).

        If ``projectName`` is given, currentProject becomes projectName.
        In other words, it "saves as...".
        """

        if projectName:
            self.currentProject = projectName
            QSettings().setValue("lastProject", projectName)

        # Saving
        files = []

        files.append((saveStandardItemModelXML(self.mdlFlatData),
                      "flatModel.xml"))
        files.append((saveStandardItemModelXML(self.mdlPersos),
                      "perso.xml"))
        #files.append((saveStandardItemModelXML(self.mdlPersosInfos),
                      #"persoInfos.xml"))
        files.append((saveStandardItemModelXML(self.mdlLabels),
                      "labels.xml"))
        files.append((saveStandardItemModelXML(self.mdlStatus),
                      "status.xml"))
        files.append((saveStandardItemModelXML(self.mdlPlots),
                      "plots.xml"))
        files.append((self.mdlOutline.saveToXML(),
                      "outline.xml"))
        files.append((settings.save(),
                      "settings.pickle"))

        saveFilesToZip(files, self.currentProject)

        # Giving some feedback
        print(self.tr("Project {} saved.").format(self.currentProject))
        self.statusBar().showMessage(
             self.tr("Project {} saved.").format(self.currentProject), 5000)


    def loadEmptyDatas(self):
        self.mdlFlatData = QStandardItemModel(self)
        self.mdlPersos = persosModel(self)
        #self.mdlPersosProxy = persosProxyModel(self)
        #self.mdlPersosInfos = QStandardItemModel(self)
        self.mdlLabels = QStandardItemModel(self)
        self.mdlStatus = QStandardItemModel(self)
        self.mdlPlots = plotModel(self)
        self.mdlOutline = outlineModel(self)

    def loadDatas(self, project):
        # Loading
        files = loadFilesFromZip(project)

        errors = []

        if "flatModel.xml" in files:
            loadStandardItemModelXML(self.mdlFlatData,
                                     files["flatModel.xml"], fromString=True)
        else:
            errors.append("flatModel.xml")

        if "perso.xml" in files:
            loadStandardItemModelXML(self.mdlPersos,
                                     files["perso.xml"], fromString=True)
        else:
            errors.append("perso.xml")


        #if "persoInfos.xml" in files:
            #loadStandardItemModelXML(self.mdlPersosInfos,
                                     #files["persoInfos.xml"], fromString=True)
        #else:
            #errors.append("perso.xml")

        if "labels.xml" in files:
            loadStandardItemModelXML(self.mdlLabels,
                                     files["labels.xml"], fromString=True)
        else:
            errors.append("perso.xml")

        if "status.xml" in files:
            loadStandardItemModelXML(self.mdlStatus,
                                     files["status.xml"], fromString=True)
        else:
            errors.append("perso.xml")

        if "plots.xml" in files:
            loadStandardItemModelXML(self.mdlPlots,
                                     files["plots.xml"], fromString=True)
        else:
            errors.append("perso.xml")

        if "outline.xml" in files:
            self.mdlOutline.loadFromXML(files["outline.xml"], fromString=True)
        else:
            errors.append("perso.xml")

        if "settings.pickle" in files:
            settings.load(files["settings.pickle"], fromString=True)
        else:
            errors.append("perso.xml")


        # Giving some feedback
        if not errors:
            print(self.tr("Project {} loaded.").format(project))
            self.statusBar().showMessage(
                self.tr("Project {} loaded.").format(project), 5000)
        else:
            print(self.tr("Project {} loaded with some errors:").format(project))
            for e in errors:
                print(self.tr(" * {} wasn't found in project file.").format(e))
            self.statusBar().showMessage(
                self.tr("Project {} loaded with some errors.").format(project), 5000)

###############################################################################
# MAIN CONNECTIONS
###############################################################################

    def makeUIConnections(self):
        "Connections that have to be made once only, event when new project is loaded."
        self.lstPersos.currentItemChanged.connect(self.changeCurrentPerso, AUC)

        self.txtPlotFilter.textChanged.connect(self.lstPlots.setFilter, AUC)
        self.lstPlots.currentItemChanged.connect(self.changeCurrentPlot, AUC)
        self.txtSubPlotSummary.document().contentsChanged.connect(
                                                     self.updateSubPlotSummary, AUC)
        self.lstSubPlots.activated.connect(self.changeCurrentSubPlot, AUC)

        self.btnRedacAddFolder.clicked.connect(self.treeRedacOutline.addFolder, AUC)
        self.btnOutlineAddFolder.clicked.connect(self.treeOutlineOutline.addFolder, AUC)
        self.btnRedacAddText.clicked.connect(self.treeRedacOutline.addText, AUC)
        self.btnOutlineAddText.clicked.connect(self.treeOutlineOutline.addText, AUC)
        self.btnRedacRemoveItem.clicked.connect(self.outlineRemoveItemsRedac, AUC)
        self.btnOutlineRemoveItem.clicked.connect(self.outlineRemoveItemsOutline, AUC)

        self.mainEditor.btnRedacShowOutline.toggled.connect(self.treeRedacWidget.setVisible)
        self.mainEditor.btnRedacShowOutline.setChecked(True)
        self.mainEditor.btnRedacShowInfos.toggled.connect(self.tabRedacInfos.setVisible)
        self.mainEditor.btnRedacShowInfos.setChecked(True)

    def makeConnections(self):

        # Flat datas (Summary and general infos)
        for widget, col in [
            (self.txtSummarySituation, 0),
            (self.txtSummarySentance, 1),
            (self.txtSummarySentance_2, 1),
            (self.txtSummaryPara, 2),
            (self.txtSummaryPara_2, 2),
            (self.txtPlotSummaryPara, 2),
            (self.txtSummaryPage, 3),
            (self.txtSummaryPage_2, 3),
            (self.txtPlotSummaryPage, 3),
            (self.txtSummaryFull, 4),
            (self.txtPlotSummaryFull, 4),
            ]:

            widget.setModel(self.mdlFlatData)
            widget.setColumn(col)
            widget.setCurrentModelIndex(self.mdlFlatData.index(1, col))

        for widget, col in [
            (self.txtGeneralTitle, 0),
            (self.txtGeneralSubtitle, 1),
            (self.txtGeneralSerie, 2),
            (self.txtGeneralVolume, 3),
            (self.txtGeneralGenre, 4),
            (self.txtGeneralLicense, 5),
            (self.txtGeneralAuthor, 6),
            (self.txtGeneralEmail, 7),
            ]:

            widget.setModel(self.mdlFlatData)
            widget.setColumn(col)
            widget.setCurrentModelIndex(self.mdlFlatData.index(0, col))

        # Persos
        self.lstPersos.setPersosModel(self.mdlPersos)
        self.tblPersoInfos.setModel(self.mdlPersos)

        self.btnAddPerso.clicked.connect(self.mdlPersos.addPerso, AUC)
        self.btnRmPerso.clicked.connect(self.mdlPersos.removePerso, AUC)
        self.btnPersoColor.clicked.connect(self.mdlPersos.chosePersoColor, AUC)
        #if self.mdlPersosProxy:
            #self.mdlPersosProxy.setSourceModel(self.mdlPersos)
            #self.lstPersos.setModel(self.mdlPersosProxy)
        #else:
            #self.lstPersos.setModel(self.mdlPersos)

        #self.tblPersoInfos.setModel(self.mdlPersosInfos)
        #self.tblPersoInfos.setRowHidden(0, True)

        self.btnPersoAddInfo.clicked.connect(self.mdlPersos.addPersoInfo, AUC)
        self.btnPersoRmInfo.clicked.connect(self.mdlPersos.removePersoInfo, AUC)

        #self.mprPersos = QDataWidgetMapper()
        #self.mprPersos.setModel(self.mdlPersos)

        #mapping = [
            #(self.txtPersoName, Perso.name.value),
            #(self.txtPersoMotivation, Perso.motivation.value),
            #(self.txtPersoGoal, Perso.goal.value),
            #(self.txtPersoConflict, Perso.conflict.value),
            #(self.txtPersoEpiphany, Perso.epiphany.value),
            #(self.txtPersoSummarySentance, Perso.summarySentance.value),
            #(self.txtPersoSummaryPara, Perso.summaryPara.value),
            #(self.txtPersoSummaryFull, Perso.summaryFull.value),
            #(self.txtPersoNotes, Perso.notes.value)
            #]
        #for w, i in mapping:
                #self.mprPersos.addMapping(w, i)
        #self.mprPersos.addMapping(self.sldPersoImportance,
                                  #Perso.importance.value, "importance")
        #self.sldPersoImportance.importanceChanged.connect(self.mprPersos.submit, AUC)
        #self.tabMain.currentChanged.connect(self.mprPersos.submit, AUC)
        #self.mprPersos.setCurrentIndex(0)

        for w, c in [
            (self.txtPersoName, Perso.name.value),
            (self.sldPersoImportance, Perso.importance.value),
            (self.txtPersoMotivation, Perso.motivation.value),
            (self.txtPersoGoal, Perso.goal.value),
            (self.txtPersoConflict, Perso.conflict.value),
            (self.txtPersoEpiphany, Perso.epiphany.value),
            (self.txtPersoSummarySentance, Perso.summarySentance.value),
            (self.txtPersoSummaryPara, Perso.summaryPara.value),
            (self.txtPersoSummaryFull, Perso.summaryFull.value),
            (self.txtPersoNotes, Perso.notes.value)
            ]:
            w.setModel(self.mdlPersos)
            w.setColumn(c)
        self.tabPersos.setEnabled(False)

        #self.lstPersos.selectionModel().currentChanged.connect(
                                        #self.mdlPersos.updatePersoColor, AUC)
        #self.tabPersos.currentChanged.connect(self.resizePersosInfos)

        # Plots
        self.lstPlots.setPlotModel(self.mdlPlots)
        self.lstPlotPerso.setModel(self.mdlPlots)
        self.lstSubPlots.setModel(self.mdlPlots)
        self._updatingSubPlot = False
        self.btnAddPlot.clicked.connect(self.mdlPlots.addPlot, AUC)
        self.btnRmPlot.clicked.connect(lambda:
                    self.mdlPlots.removePlot(self.lstPlots.currentPlotIndex()), AUC)
        self.btnAddSubPlot.clicked.connect(self.mdlPlots.addSubPlot, AUC)
        self.btnRmSubPlot.clicked.connect(self.mdlPlots.removeSubPlot, AUC)
        self.lstPlotPerso.selectionModel().selectionChanged.connect(self.plotPersoSelectionChanged)
        self.btnRmPlotPerso.clicked.connect(self.mdlPlots.removePlotPerso, AUC)

        for w, c in [
            (self.txtPlotName, Plot.name.value),
            (self.txtPlotDescription, Plot.description.value),
            (self.txtPlotResult, Plot.result.value),
            (self.sldPlotImportance, Plot.importance.value),
            ]:
            w.setModel(self.mdlPlots)
            w.setColumn(c)

        self.tabPlot.setEnabled(False)
        self.mdlPlots.updatePlotPersoButton()
        self.mdlPersos.dataChanged.connect(self.mdlPlots.updatePlotPersoButton)
        self.lstOutlinePlots.setPlotModel(self.mdlPlots)
        self.lstOutlinePlots.setShowSubPlot(True)
        self.plotPersoDelegate = outlinePersoDelegate(self.mdlPersos, self)
        self.lstPlotPerso.setItemDelegate(self.plotPersoDelegate)
        self.plotDelegate = plotDelegate(self)
        self.lstSubPlots.setItemDelegateForColumn(Subplot.meta.value, self.plotDelegate)

        # Outline
        self.treeRedacOutline.setModel(self.mdlOutline)
        self.treeOutlineOutline.setModelPersos(self.mdlPersos)
        self.treeOutlineOutline.setModelLabels(self.mdlLabels)
        self.treeOutlineOutline.setModelStatus(self.mdlStatus)

        self.redacMetadata.setModels(self.mdlOutline, self.mdlPersos,
                                     self.mdlLabels, self.mdlStatus)
        self.outlineItemEditor.setModels(self.mdlOutline, self.mdlPersos,
                                         self.mdlLabels, self.mdlStatus)

        self.treeOutlineOutline.setModel(self.mdlOutline)
        #self.redacEditor.setModel(self.mdlOutline)

        self.treeOutlineOutline.selectionModel().selectionChanged.connect(lambda:
                 self.outlineItemEditor.selectionChanged(self.treeOutlineOutline), AUC)
        self.treeOutlineOutline.clicked.connect(lambda:
                 self.outlineItemEditor.selectionChanged(self.treeOutlineOutline), AUC)

        # Sync selection
        #self.treeRedacOutline.setSelectionModel(self.treeOutlineOutline
                                                    #.selectionModel())

        self.treeRedacOutline.selectionModel().selectionChanged.connect(
            lambda: self.redacMetadata.selectionChanged(self.treeRedacOutline), AUC)
        self.treeRedacOutline.clicked.connect(
            lambda: self.redacMetadata.selectionChanged(self.treeRedacOutline), AUC)

        #self.treeRedacOutline.selectionModel().currentChanged.connect(self.redacEditor.setCurrentModelIndex)
        self.treeRedacOutline.selectionModel().selectionChanged.connect(self.mainEditor.selectionChanged, AUC)
        #self.treeRedacOutline.doubleClicked.connect(self.mainEditor.setCurrentModelIndex, AUC)
        #self.treeRedacOutline.selectionModel().currentChanged.connect(self.mainEditor.setCurrentModelIndex, AUC)

        #self.treeRedacOutline.selectionModel().selectionChanged.connect(self.outlineSelectionChanged, AUC)
        #self.treeRedacOutline.selectionModel().selectionChanged.connect(self.outlineSelectionChanged, AUC)
        #self.treeOutlineOutline.selectionModel().selectionChanged.connect(self.outlineSelectionChanged, AUC)
        #self.treeOutlineOutline.selectionModel().selectionChanged.connect(self.outlineSelectionChanged, AUC)

        # Cheat Sheet
        self.cheatSheet.setModels()

        #Debug
        self.mdlFlatData.setVerticalHeaderLabels(["Infos générales", "Summary"])
        self.tblDebugFlatData.setModel(self.mdlFlatData)
        self.tblDebugPersos.setModel(self.mdlPersos)
        self.tblDebugPersosInfos.setModel(self.mdlPersos)
        self.tblDebugPersos.selectionModel().currentChanged.connect(
            lambda: self.tblDebugPersosInfos.setRootIndex(self.mdlPersos.index(
                self.tblDebugPersos.selectionModel().currentIndex().row(),
                Perso.name.value)), AUC)

        self.tblDebugPlots.setModel(self.mdlPlots)
        self.tblDebugPlotsPersos.setModel(self.mdlPlots)
        self.tblDebugSubPlots.setModel(self.mdlPlots)
        self.tblDebugPlots.selectionModel().currentChanged.connect(
            lambda: self.tblDebugPlotsPersos.setRootIndex(self.mdlPlots.index(
                self.tblDebugPlots.selectionModel().currentIndex().row(),
                Plot.persos.value)), AUC)
        self.tblDebugPlots.selectionModel().currentChanged.connect(
            lambda: self.tblDebugSubPlots.setRootIndex(self.mdlPlots.index(
                self.tblDebugPlots.selectionModel().currentIndex().row(),
                Plot.subplots.value)), AUC)
        self.treeDebugOutline.setModel(self.mdlOutline)
        self.lstDebugLabels.setModel(self.mdlLabels)
        self.lstDebugStatus.setModel(self.mdlStatus)
        #self.mdlPersos.setHorizontalHeaderLabels([i.name for i in Perso])


###############################################################################
# GENERAL AKA UNSORTED
###############################################################################

    def clickCycle(self, i):
        if i == 0:  # step 2 - paragraph summary
            self.tabMain.setCurrentIndex(1)
            self.tabSummary.setCurrentIndex(1)
        if i == 1:  # step 3 - characters summary
            self.tabMain.setCurrentIndex(2)
            self.tabPersos.setCurrentIndex(0)
        if i == 2:  # step 4 - page summary
            self.tabMain.setCurrentIndex(1)
            self.tabSummary.setCurrentIndex(2)
        if i == 3:  # step 5 - characters description
            self.tabMain.setCurrentIndex(2)
            self.tabPersos.setCurrentIndex(1)
        if i == 4:  # step 6 - four page synopsis
            self.tabMain.setCurrentIndex(1)
            self.tabSummary.setCurrentIndex(3)
        if i == 5:  # step 7 - full character charts
            self.tabMain.setCurrentIndex(2)
            self.tabPersos.setCurrentIndex(2)
        if i == 6:  # step 8 - scene list
            self.tabMain.setCurrentIndex(3)

    def wordCount(self, i):

        src = {
            0: self.txtSummarySentance,
            1: self.txtSummaryPara,
            2: self.txtSummaryPage,
            3: self.txtSummaryFull
            }[i]

        lbl = {
            0: self.lblSummaryWCSentance,
            1: self.lblSummaryWCPara,
            2: self.lblSummaryWCPage,
            3: self.lblSummaryWCFull
            }[i]

        wc = wordCount(src.toPlainText())
        if i in [2, 3]:
            pages = self.tr(" (~{} pages)").format(int(wc / 25) / 10.)
        else:
            pages = ""
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

        self.splitterRedac.setStretchFactor(0, 30)
        self.splitterRedac.setStretchFactor(1, 40)
        self.splitterRedac.setStretchFactor(2, 30)
        
        # Help box
        references = [
            (self.lytTabOverview,
             self.tr("Enter infos about your book, and yourself."),
             0),
            (self.lytSituation,
             self.tr("The basic situation, in the form of a 'What if...?' question. Ex: 'What if the most dangerous evil wizard could wasn't abled to kill a baby?' (Harry Potter)"),
             1),
            (self.lytSummary,
             self.tr("Take time to think about a one sentance (~50 words) summary of your book. Then expand it to a paragraph, then to a page, then to a full summary."),
             1),
            (self.lytTabPersos,
             self.tr("Create your characters."),
             0),
            (self.lytTabPlot,
             self.tr("Develop plots."),
             0),
            (self.lytTabOutline,
             self.tr("Create the outline of your masterpiece."),
             0),
            (self.lytTabRedac,
             self.tr("Write."),
             0),
            (self.lytTabDebug,
             self.tr("Debug infos. Sometimes useful."),
             0)
            ]

        for widget, text, pos in references:
            label = helpLabel(text, self)
            self.actShowHelp.toggled.connect(label.setVisible, AUC)
            widget.layout().insertWidget(pos, label)

        self.actShowHelp.setChecked(False)

        # Spellcheck
        if enchant:
            self.menuDict = QMenu(self.tr("Dictionary"))
            self.menuDictGroup = QActionGroup(self)
            self.updateMenuDict()
            self.menuTools.addMenu(self.menuDict)

            self.actSpellcheck.toggled.connect(self.toggleSpellcheck, AUC)
            self.dictChanged.connect(self.mainEditor.setDict, AUC)
            self.dictChanged.connect(self.redacMetadata.setDict, AUC)
            self.dictChanged.connect(self.outlineItemEditor.setDict, AUC)

        else:
            # No Spell check support
            self.actSpellcheck.setVisible(False)
            a = QAction(self.tr("Install PyEnchant to use spellcheck"), self)
            a.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
            a.triggered.connect(self.openPyEnchantWebPage, AUC)
            self.menuTools.addAction(a)

###############################################################################
# SPELLCHECK
###############################################################################

    def updateMenuDict(self):

        if not enchant:
            return

        self.menuDict.clear()
        for i in enchant.list_dicts():
            a = QAction(str(i[0]), self)
            a.setCheckable(True)
            if settings.dict is None:
                settings.dict = enchant.get_default_language()
            if str(i[0]) == settings.dict:
                a.setChecked(True)
            a.triggered.connect(self.setDictionary, AUC)
            self.menuDictGroup.addAction(a)
            self.menuDict.addAction(a)

    def setDictionary(self):
        if not enchant:
            return

        for i in self.menuDictGroup.actions():
            if i.isChecked():
                #self.dictChanged.emit(i.text().replace("&", ""))
                settings.dict = i.text().replace("&", "")

                # Find all textEditView from self, and toggle spellcheck
                for w in self.findChildren(textEditView, QRegExp(".*"),
                                           Qt.FindChildrenRecursively):
                    w.setDict(settings.dict)

    def openPyEnchantWebPage(self):
        QDesktopServices.openUrl(QUrl("http://pythonhosted.org/pyenchant/"))

    def toggleSpellcheck(self, val):
        settings.spellcheck = val
        #self.mainEditor.toggleSpellcheck(val)
        #self.redacMetadata.toggleSpellcheck(val)
        #self.outlineItemEditor.toggleSpellcheck(val)

        # Find all textEditView from self, and toggle spellcheck
        for w in self.findChildren(textEditView, QRegExp(".*"),
                                   Qt.FindChildrenRecursively):
            w.toggleSpellcheck(val)

###############################################################################
# SETTINGS
###############################################################################

    def settingsLabel(self):
        self.settingsWindow(3)

    def settingsStatus(self):
        self.settingsWindow(4)

    def settingsWindow(self, tab=None):
        self.sw = settingsWindow(self)
        self.sw.hide()
        self.sw.setWindowModality(Qt.ApplicationModal)
        self.sw.setWindowFlags(Qt.Dialog)
        r = self.sw.geometry()
        r2 = self.geometry()
        self.sw.move(r2.center() - r.center())
        if tab:
            self.sw.setTab(tab)
        self.sw.show()

###############################################################################
# VIEW MENU
###############################################################################

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
                    a.triggered.connect(self.setViewSettingsAction, AUC)
                    agp.addAction(a)
                    m2.addAction(a)
                m.addMenu(m2)
            self.menuView.addMenu(m)

    def setViewSettingsAction(self):
        action = self.sender()
        item, part, element = action.data().split(",")
        self.setViewSettings(item, part, element)

    def setViewSettings(self, item, part, element):
        settings.viewSettings[item][part] = element
        if item == "Cork":
            self.mainEditor.updateCorkView()
        if item == "Outline":
            self.mainEditor.updateTreeView()
            self.treeOutlineOutline.viewport().update()
        if item == "Tree":
            self.treeRedacOutline.viewport().update()


###############################################################################
# COMPILE
###############################################################################

    def doCompile(self):
        self.compileDialog = compileDialog()
        self.compileDialog.show()