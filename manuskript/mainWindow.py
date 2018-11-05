#!/usr/bin/env python
# --!-- coding: utf8 --!--
import imp
import os

from PyQt5.QtCore import (pyqtSignal, QSignalMapper, QTimer, QSettings, Qt,
                          QRegExp, QUrl, QSize, QModelIndex)
from PyQt5.QtGui import QStandardItemModel, QIcon, QColor
from PyQt5.QtWidgets import QMainWindow, QHeaderView, qApp, QMenu, QActionGroup, QAction, QStyle, QListWidgetItem, \
    QLabel, QDockWidget, QWidget

from manuskript import settings
from manuskript.enums import Character, PlotStep, Plot, World, Outline
from manuskript.functions import wordCount, appPath, findWidgetsOfClass
import manuskript.functions as F
from manuskript import loadSave
from manuskript.models.characterModel import characterModel
from manuskript.models import outlineModel
from manuskript.models.plotModel import plotModel
from manuskript.models.worldModel import worldModel
from manuskript.settingsWindow import settingsWindow
from manuskript.ui import style
from manuskript.ui.about import aboutDialog
from manuskript.ui.collapsibleDockWidgets import collapsibleDockWidgets
from manuskript.ui.importers.importer import importerDialog
from manuskript.ui.exporters.exporter import exporterDialog
from manuskript.ui.helpLabel import helpLabel
from manuskript.ui.mainWindow import Ui_MainWindow
from manuskript.ui.tools.frequencyAnalyzer import frequencyAnalyzer
from manuskript.ui.views.outlineDelegates import outlineCharacterDelegate
from manuskript.ui.views.plotDelegate import plotDelegate
from manuskript.ui.views.MDEditView import MDEditView
from manuskript.ui.statusLabel import statusLabel

# Spellcheck support
from manuskript.ui.views.textEditView import textEditView

try:
    import enchant
except ImportError:
    enchant = None


class MainWindow(QMainWindow, Ui_MainWindow):
    dictChanged = pyqtSignal(str)

    # Tab indexes
    TabInfos = 0
    TabSummary = 1
    TabPersos = 2
    TabPlots = 3
    TabWorld = 4
    TabOutline = 5
    TabRedac = 6
    TabDebug = 7

    SHOW_DEBUG_TAB = False

    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

        # Var
        self.currentProject = None
        self._lastFocus = None
        self._lastMDEditView = None
        self._defaultCursorFlashTime = 1000 # Overriden at startup with system
                                            # value. In manuskript.main.
        self._autoLoadProject = None  # Used to load a command line project

        self.readSettings()

        # UI
        self.setupMoreUi()
        self.statusLabel = statusLabel(parent=self)
        self.statusLabel.setAutoFillBackground(True)
        self.statusLabel.hide()

        # Welcome
        self.welcome.updateValues()
        self.switchToWelcome()

        # Word count
        self.mprWordCount = QSignalMapper(self)
        for t, i in [
            (self.txtSummarySentence, 0),
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
            (self.btnStepTwo, 0),
            (self.btnStepThree, 1),
            (self.btnStepFour, 2),
            (self.btnStepFive, 3),
            (self.btnStepSix, 4),
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
                  self.menuEdit, self.menuView, self.menuOrganize,
                  self.menuTools, self.menuHelp, self.actImport,
                  self.actCompile, self.actSettings]:
            i.setEnabled(False)

        # Main Menu:: File
        self.actOpen.triggered.connect(self.welcome.openFile)
        self.actSave.triggered.connect(self.saveDatas)
        self.actSaveAs.triggered.connect(self.welcome.saveAsFile)
        self.actImport.triggered.connect(self.doImport)
        self.actCompile.triggered.connect(self.doCompile)
        self.actCloseProject.triggered.connect(self.closeProject)
        self.actQuit.triggered.connect(self.close)

        # Main menu:: Edit
        self.actCopy.triggered.connect(self.documentsCopy)
        self.actCut.triggered.connect(self.documentsCut)
        self.actPaste.triggered.connect(self.documentsPaste)
        self.actRename.triggered.connect(self.documentsRename)
        self.actDuplicate.triggered.connect(self.documentsDuplicate)
        self.actDelete.triggered.connect(self.documentsDelete)
        self.actLabels.triggered.connect(self.settingsLabel)
        self.actStatus.triggered.connect(self.settingsStatus)
        self.actSettings.triggered.connect(self.settingsWindow)

        # Main menu:: Edit:: Format
        self.actHeaderSetextL1.triggered.connect(self.formatSetext1)
        self.actHeaderSetextL2.triggered.connect(self.formatSetext2)
        self.actHeaderAtxL1.triggered.connect(self.formatAtx1)
        self.actHeaderAtxL2.triggered.connect(self.formatAtx2)
        self.actHeaderAtxL3.triggered.connect(self.formatAtx3)
        self.actHeaderAtxL4.triggered.connect(self.formatAtx4)
        self.actHeaderAtxL5.triggered.connect(self.formatAtx5)
        self.actHeaderAtxL6.triggered.connect(self.formatAtx6)
        self.actFormatBold.triggered.connect(self.formatBold)
        self.actFormatItalic.triggered.connect(self.formatItalic)
        self.actFormatStrike.triggered.connect(self.formatStrike)
        self.actFormatVerbatim.triggered.connect(self.formatVerbatim)
        self.actFormatSuperscript.triggered.connect(self.formatSuperscript)
        self.actFormatSubscript.triggered.connect(self.formatSubscript)
        self.actFormatCommentLines.triggered.connect(self.formatCommentLines)
        self.actFormatList.triggered.connect(self.formatList)
        self.actFormatOrderedList.triggered.connect(self.formatOrderedList)
        self.actFormatBlockquote.triggered.connect(self.formatBlockquote)
        self.actFormatCommentBlock.triggered.connect(self.formatCommentBlock)
        self.actFormatClear.triggered.connect(self.formatClear)

        # Main menu:: Organize
        self.actMoveUp.triggered.connect(self.documentsMoveUp)
        self.actMoveDown.triggered.connect(self.documentsMoveDown)
        self.actSplitDialog.triggered.connect(self.documentsSplitDialog)
        self.actSplitCursor.triggered.connect(self.documentsSplitCursor)
        self.actMerge.triggered.connect(self.documentsMerge)

        # Main Menu:: view
        self.generateViewMenu()
        self.actModeGroup = QActionGroup(self)
        self.actModeSimple.setActionGroup(self.actModeGroup)
        self.actModeFiction.setActionGroup(self.actModeGroup)
        self.actModeSnowflake.setActionGroup(self.actModeGroup)
        self.actModeSimple.triggered.connect(self.setViewModeSimple)
        self.actModeFiction.triggered.connect(self.setViewModeFiction)
        self.actModeSnowflake.setEnabled(False)

        # Main Menu:: Tool
        self.actToolFrequency.triggered.connect(self.frequencyAnalyzer)
        self.actAbout.triggered.connect(self.about)

        self.makeUIConnections()

        # self.loadProject(os.path.join(appPath(), "test_project.zip"))

    def updateDockVisibility(self, restore=False):
        """
        Saves the state of the docks visibility. Or if `restore` is True,
        restores from `self._dckVisibility`. This allows to hide the docks
        while showing the welcome screen, and then restore them as they
        were.

        If `self._dckVisibility` contains "LOCK", then we don't override values
        with current visibility state. This is used the first time we load.
        "LOCK" is then removed.
        """
        docks = [
            self.dckCheatSheet,
            self.dckNavigation,
            self.dckSearch,
        ]

        for d in docks:
            if not restore:
                # We store the values, but only if "LOCK" is not present
                if not "LOCK" in self._dckVisibility:
                    self._dckVisibility[d.objectName()] = d.isVisible()
                # Hide the dock
                d.setVisible(False)
            else:
                # Restore the dock's visibility based on stored value
                d.setVisible(self._dckVisibility[d.objectName()])

        # Lock is used only once, at start up. We can remove it
        if "LOCK" in self._dckVisibility:
            self._dckVisibility.pop("LOCK")

    def switchToWelcome(self):
        """
        While switching to welcome screen, we have to hide all the docks.
        Otherwise one could use the search dock, and manuskript would crash.
        Plus it's unnecessary distraction.
        But we also want to restore them to their visibility prior to switching,
        so we store states.
        """
        # Stores the state of docks
        self.updateDockVisibility()
        # Hides the toolbar
        self.toolbar.setVisible(False)
        # Switch to welcome screen
        self.stack.setCurrentIndex(0)

    def switchToProject(self):
        """Restores docks and toolbar visibility, and switch to project."""
        # Restores the docks visibility
        self.updateDockVisibility(restore=True)
        # Show the toolbar
        self.toolbar.setVisible(True)
        self.stack.setCurrentIndex(1)

    ###############################################################################
    # GENERAL / UI STUFF
    ###############################################################################

    def tabMainChanged(self):
        "Called when main tab changes."
        tabIsEditor = self.tabMain.currentIndex() == self.TabRedac
        self.menuOrganize.menuAction().setEnabled(tabIsEditor)
        for i in [self.actCut,
                  self.actCopy,
                  self.actPaste,
                  self.actDelete,
                  self.actRename]:
            i.setEnabled(tabIsEditor)

    def focusChanged(self, old, new):
        """
        We get notified by qApp when focus changes, from old to new widget.
        """

        # If new is a MDEditView, we keep it in memory
        if issubclass(type(new), MDEditView):
            self._lastMDEditView = new
        else:
            self._lastMDEditView = None

        # Determine which view had focus last, to send the keyboard shortcuts
        # to the right place

        targets = [
            self.treeRedacOutline,
            self.mainEditor
            ]

        while new is not None:
            if new in targets:
                self._lastFocus = new
                break
            new = new.parent()

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
    # CHARACTERS
    ###############################################################################

    def changeCurrentCharacter(self, trash=None):
        """

        @return:
        """
        c = self.lstCharacters.currentCharacter()
        if not c:
            self.tabPersos.setEnabled(False)
            return

        self.tabPersos.setEnabled(True)
        index = c.index()

        for w in [
            self.txtPersoName,
            self.sldPersoImportance,
            self.txtPersoMotivation,
            self.txtPersoGoal,
            self.txtPersoConflict,
            self.txtPersoEpiphany,
            self.txtPersoSummarySentence,
            self.txtPersoSummaryPara,
            self.txtPersoSummaryFull,
            self.txtPersoNotes,
        ]:
            w.setCurrentModelIndex(index)

        # Button color
        self.updateCharacterColor(c.ID())

        # Slider importance
        self.updateCharacterImportance(c.ID())

        # Character Infos
        self.tblPersoInfos.setRootIndex(index)

        if self.mdlCharacter.rowCount(index):
            self.updatePersoInfoView()

    def updatePersoInfoView(self):
        self.tblPersoInfos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tblPersoInfos.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tblPersoInfos.verticalHeader().hide()

    def updateCharacterColor(self, ID):
        c = self.mdlCharacter.getCharacterByID(ID)
        color = c.color().name()
        self.btnPersoColor.setStyleSheet("background:{};".format(color))

    def updateCharacterImportance(self, ID):
        c = self.mdlCharacter.getCharacterByID(ID)
        self.sldPersoImportance.setValue(int(c.importance()))

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
                                                     Plot.characters))

        # Slider importance
        self.updatePlotImportance(index.row())

        subplotindex = index.sibling(index.row(), Plot.steps)
        self.lstSubPlots.setRootIndex(subplotindex)
        if self.mdlPlots.rowCount(subplotindex):
            self.updateSubPlotView()

        self.txtSubPlotSummary.setCurrentModelIndex(QModelIndex())
        self.lstPlotPerso.selectionModel().clear()

    def updateSubPlotView(self):
        # Hide columns
        # FIXME: when columns are hidden, and drag and drop InternalMove is enabled
        #        as well as selectionBehavior=SelectRows, then when moving a row
        #        hidden cells (here: summary and ID) are deleted...
        #        So instead we set their width to 0.
        #for i in range(self.mdlPlots.columnCount()):
            #self.lstSubPlots.hideColumn(i)
        #self.lstSubPlots.showColumn(PlotStep.name)
        #self.lstSubPlots.showColumn(PlotStep.meta)

        self.lstSubPlots.horizontalHeader().setSectionResizeMode(
                PlotStep.ID, QHeaderView.Fixed)
        self.lstSubPlots.horizontalHeader().setSectionResizeMode(
                PlotStep.summary, QHeaderView.Fixed)
        self.lstSubPlots.horizontalHeader().resizeSection(
                PlotStep.ID, 0)
        self.lstSubPlots.horizontalHeader().resizeSection(
                PlotStep.summary, 0)

        self.lstSubPlots.horizontalHeader().setSectionResizeMode(
                PlotStep.name, QHeaderView.Stretch)
        self.lstSubPlots.horizontalHeader().setSectionResizeMode(
                PlotStep.meta, QHeaderView.ResizeToContents)
        self.lstSubPlots.verticalHeader().hide()

    def updatePlotImportance(self, row):
        imp = self.mdlPlots.getPlotImportanceByRow(row)
        self.sldPlotImportance.setValue(int(imp))

    def changeCurrentSubPlot(self, index):
        index = index.sibling(index.row(), PlotStep.summary)
        self.txtSubPlotSummary.setColumn(PlotStep.summary)
        self.txtSubPlotSummary.setCurrentModelIndex(index)

    def plotPersoSelectionChanged(self):
        "Enables or disables remove plot perso button."
        self.btnRmPlotPerso.setEnabled(
                len(self.lstPlotPerso.selectedIndexes()) != 0)

    ###############################################################################
    # WORLD
    ###############################################################################

    def changeCurrentWorld(self):
        index = self.mdlWorld.selectedIndex()

        if not index.isValid():
            self.tabWorld.setEnabled(False)
            return

        self.tabWorld.setEnabled(True)
        self.txtWorldName.setCurrentModelIndex(index)
        self.txtWorldDescription.setCurrentModelIndex(index)
        self.txtWorldPassion.setCurrentModelIndex(index)
        self.txtWorldConflict.setCurrentModelIndex(index)

    ###############################################################################
    # EDITOR
    ###############################################################################

    def openIndex(self, index):
        self.treeRedacOutline.setCurrentIndex(index)

    def openIndexes(self, indexes, newTab=True):
        self.mainEditor.openIndexes(indexes, newTab=True)

    # Menu #############################################################

    # Functions called by the menus
    # self._lastFocus is the last editor that had focus (either treeView or
    # mainEditor). So we just pass along the signal.

    # Edit

    def documentsCopy(self):
        "Copy selected item(s)."
        if self._lastFocus: self._lastFocus.copy()
    def documentsCut(self):
        "Cut selected item(s)."
        if self._lastFocus: self._lastFocus.cut()
    def documentsPaste(self):
        "Paste clipboard item(s) into selected item."
        if self._lastFocus: self._lastFocus.paste()
    def documentsRename(self):
        "Rename selected item."
        if self._lastFocus: self._lastFocus.rename()
    def documentsDuplicate(self):
        "Duplicate selected item(s)."
        if self._lastFocus: self._lastFocus.duplicate()
    def documentsDelete(self):
        "Delete selected item(s)."
        if self._lastFocus: self._lastFocus.delete()

    # Formats
    def callLastMDEditView(self, functionName, param=[]):
        """
        If last focused widget was MDEditView, call the given function.
        """
        if self._lastMDEditView:
            function = getattr(self._lastMDEditView, functionName)
            function(*param)
    def formatSetext1(self): self.callLastMDEditView("titleSetext", [1])
    def formatSetext2(self): self.callLastMDEditView("titleSetext", [2])
    def formatAtx1(self): self.callLastMDEditView("titleATX", [1])
    def formatAtx2(self): self.callLastMDEditView("titleATX", [2])
    def formatAtx3(self): self.callLastMDEditView("titleATX", [3])
    def formatAtx4(self): self.callLastMDEditView("titleATX", [4])
    def formatAtx5(self): self.callLastMDEditView("titleATX", [5])
    def formatAtx6(self): self.callLastMDEditView("titleATX", [6])
    def formatBold(self): self.callLastMDEditView("bold")
    def formatItalic(self): self.callLastMDEditView("italic")
    def formatStrike(self): self.callLastMDEditView("strike")
    def formatVerbatim(self): self.callLastMDEditView("verbatim")
    def formatSuperscript(self): self.callLastMDEditView("superscript")
    def formatSubscript(self): self.callLastMDEditView("subscript")
    def formatCommentLines(self): self.callLastMDEditView("commentLine")
    def formatList(self): self.callLastMDEditView("unorderedList")
    def formatOrderedList(self): self.callLastMDEditView("orderedList")
    def formatBlockquote(self): self.callLastMDEditView("blockquote")
    def formatCommentBlock(self): self.callLastMDEditView("comment")
    def formatClear(self): self.callLastMDEditView("clearFormat")

    # Organize

    def documentsMoveUp(self):
        "Move up selected item(s)."
        if self._lastFocus: self._lastFocus.moveUp()
    def documentsMoveDown(self):
        "Move Down selected item(s)."
        if self._lastFocus: self._lastFocus.moveDown()

    def documentsSplitDialog(self):
        "Opens a dialog to split selected items."
        if self._lastFocus: self._lastFocus.splitDialog()
        # current items or selected items?
        pass
        # use outlineBasics, to do that on all selected items.
        # use editorWidget to do that on selected text.

    def documentsSplitCursor(self):
        """
        Split current item (open in text editor) at cursor position. If there is
        a text selection, that selection becomes the title of the new scene.
        """
        if self._lastFocus and self._lastFocus == self.mainEditor:
            self.mainEditor.splitCursor()
    def documentsMerge(self):
        "Merges selected item(s)."
        if self._lastFocus: self._lastFocus.merge()

    ###############################################################################
    # LOAD AND SAVE
    ###############################################################################

    def loadProject(self, project, loadFromFile=True):
        """Loads the project ``project``.

        If ``loadFromFile`` is False, then it does not load datas from file.
        It assumes that the datas have been populated in a different way."""
        if loadFromFile and not os.path.exists(project):
            print(self.tr("The file {} does not exist. Has it been moved or deleted?").format(project))
            F.statusMessage(
                    self.tr("The file {} does not exist. Has it been moved or deleted?").format(project), importance=3)
            return

        if loadFromFile:
            # Load empty settings
            imp.reload(settings)
            settings.initDefaultValues()

            # Load data
            self.loadEmptyDatas()
            self.loadDatas(project)

        self.makeConnections()

        # Load settings
        if settings.openIndexes and settings.openIndexes != [""]:
            self.mainEditor.tabSplitter.restoreOpenIndexes(settings.openIndexes)
        self.generateViewMenu()
        self.mainEditor.sldCorkSizeFactor.setValue(settings.corkSizeFactor)
        self.actSpellcheck.setChecked(settings.spellcheck)
        self.toggleSpellcheck(settings.spellcheck)
        self.updateMenuDict()
        self.setDictionary()

        iconSize = settings.viewSettings["Tree"]["iconSize"]
        self.treeRedacOutline.setIconSize(QSize(iconSize, iconSize))
        self.mainEditor.setFolderView(settings.folderView)
        self.mainEditor.updateFolderViewButtons(settings.folderView)
        self.mainEditor.tabSplitter.updateStyleSheet()
        self.tabMain.setCurrentIndex(settings.lastTab)
        self.mainEditor.updateCorkBackground()
        if settings.viewMode == "simple":
            self.setViewModeSimple()
        else:
            self.setViewModeFiction()

        # Set autosave
        self.saveTimer = QTimer()
        self.saveTimer.setInterval(settings.autoSaveDelay * 60 * 1000)
        self.saveTimer.setSingleShot(False)
        self.saveTimer.timeout.connect(self.saveDatas)
        if settings.autoSave:
            self.saveTimer.start()

        # Set autosave if no changes
        self.saveTimerNoChanges = QTimer()
        self.saveTimerNoChanges.setInterval(settings.autoSaveNoChangesDelay * 1000)
        self.saveTimerNoChanges.setSingleShot(True)
        self.mdlFlatData.dataChanged.connect(self.startTimerNoChanges)
        self.mdlOutline.dataChanged.connect(self.startTimerNoChanges)
        self.mdlCharacter.dataChanged.connect(self.startTimerNoChanges)
        self.mdlPlots.dataChanged.connect(self.startTimerNoChanges)
        self.mdlWorld.dataChanged.connect(self.startTimerNoChanges)
        # self.mdlPersosInfos.dataChanged.connect(self.startTimerNoChanges)
        self.mdlStatus.dataChanged.connect(self.startTimerNoChanges)
        self.mdlLabels.dataChanged.connect(self.startTimerNoChanges)

        self.saveTimerNoChanges.timeout.connect(self.saveDatas)
        self.saveTimerNoChanges.stop()

        # UI
        for i in [self.actOpen, self.menuRecents]:
            i.setEnabled(False)
        for i in [self.actSave, self.actSaveAs, self.actCloseProject,
                  self.menuEdit, self.menuView, self.menuOrganize,
                  self.menuTools, self.menuHelp, self.actImport,
                  self.actCompile, self.actSettings]:
            i.setEnabled(True)
        # We force to emit even if it opens on the current tab
        self.tabMain.currentChanged.emit(settings.lastTab)

        # Add project name to Window's name
        pName = os.path.split(project)[1]
        if pName.endswith('.msk'):
            pName=pName[:-4]
        self.setWindowTitle(pName + " - " + self.tr("Manuskript"))

        # Stuff
        # self.checkPersosID()  # Shouldn't be necessary any longer

        self.currentProject = project
        QSettings().setValue("lastProject", project)

        # Show main Window
        self.switchToProject()

    def closeProject(self):

        if not self.currentProject:
            return

        # Close open tabs in editor
        self.mainEditor.closeAllTabs()

        # Save datas
        self.saveDatas()

        self.currentProject = None
        QSettings().setValue("lastProject", "")

        # Clear datas
        self.loadEmptyDatas()
        self.saveTimer.stop()
        loadSave.clearSaveCache()

        self.breakConnections()

        # UI
        for i in [self.actOpen, self.menuRecents]:
            i.setEnabled(True)
        for i in [self.actSave, self.actSaveAs, self.actCloseProject,
                  self.menuEdit, self.menuView, self.menuOrganize,
                  self.menuTools, self.menuHelp, self.actImport,
                  self.actCompile, self.actSettings]:
            i.setEnabled(False)

        # Set Window's name - no project loaded
        self.setWindowTitle(self.tr("Manuskript"))

        # Reload recent files
        self.welcome.updateValues()

        # Show welcome dialog
        self.switchToWelcome()

    def readSettings(self):
        # Load State and geometry
        sttgns = QSettings(qApp.organizationName(), qApp.applicationName())
        if sttgns.contains("geometry"):
            self.restoreGeometry(sttgns.value("geometry"))
        if sttgns.contains("windowState"):
            self.restoreState(sttgns.value("windowState"))

        if sttgns.contains("docks"):
            self._dckVisibility = {}
            vals = sttgns.value("docks")
            for name in vals:
                self._dckVisibility[name] = vals[name]
        else:
            # Create default settings
            self._dckVisibility = {
                self.dckNavigation.objectName() : True,
                self.dckCheatSheet.objectName() : False,
                self.dckSearch.objectName() : False,
            }
        self._dckVisibility["LOCK"] = True  # prevent overriding loaded values

        if sttgns.contains("metadataState"):
            state = [False if v == "false" else True for v in sttgns.value("metadataState")]
            self.redacMetadata.restoreState(state)
        if sttgns.contains("revisionsState"):
            state = [False if v == "false" else True for v in sttgns.value("revisionsState")]
            self.redacMetadata.revisions.restoreState(state)
        if sttgns.contains("splitterRedacH"):
            self.splitterRedacH.restoreState(sttgns.value("splitterRedacH"))
        if sttgns.contains("splitterRedacV"):
            self.splitterRedacV.restoreState(sttgns.value("splitterRedacV"))
        if sttgns.contains("toolbar"):
            # self.toolbar is not initialized yet, so we just store value
            self._toolbarState = sttgns.value("toolbar")
        else:
            self._toolbarState = ""

    def closeEvent(self, event):
        # Save State and geometry and other things
        sttgns = QSettings(qApp.organizationName(), qApp.applicationName())
        sttgns.setValue("geometry", self.saveGeometry())
        sttgns.setValue("windowState", self.saveState())
        sttgns.setValue("metadataState", self.redacMetadata.saveState())
        sttgns.setValue("revisionsState", self.redacMetadata.revisions.saveState())
        sttgns.setValue("splitterRedacH", self.splitterRedacH.saveState())
        sttgns.setValue("splitterRedacV", self.splitterRedacV.saveState())
        sttgns.setValue("toolbar", self.toolbar.saveState())

        # If we are not in the welcome window, we update the visibility
        # of the docks widgets
        if self.stack.currentIndex() == 1:
            self.updateDockVisibility()
        # Storing the visibility of docks to restore it on restart
        sttgns.setValue("docks", self._dckVisibility)

        # Specific settings to save before quitting
        settings.lastTab = self.tabMain.currentIndex()

        if self.currentProject:
            # Remembering the current items (stores outlineItem's ID)
            settings.openIndexes = self.mainEditor.tabSplitter.openIndexes()

        # Save data from models
        if self.currentProject and settings.saveOnQuit:
            self.saveDatas()

            # closeEvent
            # QMainWindow.closeEvent(self, event)  # Causing segfaults?

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

        r = loadSave.saveProject()  # version=0
        self.saveTimerNoChanges.stop()

        projectName = os.path.basename(self.currentProject)
        if r:
            feedback = self.tr("Project {} saved.").format(projectName)
            F.statusMessage(feedback, importance=0)
        else:
            feedback = self.tr("WARNING: Project {} not saved.").format(projectName)
            F.statusMessage(feedback, importance=3)

        # Giving some feedback in console
        print(feedback)

    def loadEmptyDatas(self):
        self.mdlFlatData = QStandardItemModel(self)
        self.mdlCharacter = characterModel(self)
        # self.mdlPersosProxy = persosProxyModel(self)
        # self.mdlPersosInfos = QStandardItemModel(self)
        self.mdlLabels = QStandardItemModel(self)
        self.mdlStatus = QStandardItemModel(self)
        self.mdlPlots = plotModel(self)
        self.mdlOutline = outlineModel(self)
        self.mdlWorld = worldModel(self)

    def loadDatas(self, project):

        errors = loadSave.loadProject(project)

        # Giving some feedback
        if not errors:
            print(self.tr("Project {} loaded.").format(project))
            F.statusMessage(
                    self.tr("Project {} loaded.").format(project), 2000)
        else:
            print(self.tr("Project {} loaded with some errors:").format(project))
            for e in errors:
                print(self.tr(" * {} wasn't found in project file.").format(e))
            F.statusMessage(
                    self.tr("Project {} loaded with some errors.").format(project), 5000, importance = 3)

    ###############################################################################
    # MAIN CONNECTIONS
    ###############################################################################

    def makeUIConnections(self):
        "Connections that have to be made once only, even when a new project is loaded."
        self.lstCharacters.currentItemChanged.connect(self.changeCurrentCharacter, F.AUC)

        self.txtPlotFilter.textChanged.connect(self.lstPlots.setFilter, F.AUC)
        self.lstPlots.currentItemChanged.connect(self.changeCurrentPlot, F.AUC)
        self.lstSubPlots.clicked.connect(self.changeCurrentSubPlot, F.AUC)

        self.btnRedacAddFolder.clicked.connect(self.treeRedacOutline.addFolder, F.AUC)
        self.btnOutlineAddFolder.clicked.connect(self.treeOutlineOutline.addFolder, F.AUC)
        self.btnRedacAddText.clicked.connect(self.treeRedacOutline.addText, F.AUC)
        self.btnOutlineAddText.clicked.connect(self.treeOutlineOutline.addText, F.AUC)
        self.btnRedacRemoveItem.clicked.connect(self.outlineRemoveItemsRedac, F.AUC)
        self.btnOutlineRemoveItem.clicked.connect(self.outlineRemoveItemsOutline, F.AUC)

        self.tabMain.currentChanged.connect(self.toolbar.setCurrentGroup)
        self.tabMain.currentChanged.connect(self.tabMainChanged)

        qApp.focusChanged.connect(self.focusChanged)

    def makeConnections(self):

        # Flat datas (Summary and general infos)
        for widget, col in [
            (self.txtSummarySituation, 0),
            (self.txtSummarySentence, 1),
            (self.txtSummarySentence_2, 1),
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

        # Characters
        self.lstCharacters.setCharactersModel(self.mdlCharacter)
        self.tblPersoInfos.setModel(self.mdlCharacter)

        self.btnAddPerso.clicked.connect(self.mdlCharacter.addCharacter, F.AUC)
        try:
            self.btnRmPerso.clicked.connect(self.lstCharacters.removeCharacter, F.AUC)
            self.btnPersoColor.clicked.connect(self.lstCharacters.choseCharacterColor, F.AUC)
            self.btnPersoAddInfo.clicked.connect(self.lstCharacters.addCharacterInfo, F.AUC)
            self.btnPersoRmInfo.clicked.connect(self.lstCharacters.removeCharacterInfo, F.AUC)
        except TypeError:
            # Connection has already been made
            pass

        for w, c in [
            (self.txtPersoName, Character.name),
            (self.sldPersoImportance, Character.importance),
            (self.txtPersoMotivation, Character.motivation),
            (self.txtPersoGoal, Character.goal),
            (self.txtPersoConflict, Character.conflict),
            (self.txtPersoEpiphany, Character.epiphany),
            (self.txtPersoSummarySentence, Character.summarySentence),
            (self.txtPersoSummaryPara, Character.summaryPara),
            (self.txtPersoSummaryFull, Character.summaryFull),
            (self.txtPersoNotes, Character.notes)
        ]:
            w.setModel(self.mdlCharacter)
            w.setColumn(c)
        self.tabPersos.setEnabled(False)

        # Plots
        self.lstSubPlots.setModel(self.mdlPlots)
        self.lstPlotPerso.setModel(self.mdlPlots)
        self.lstPlots.setPlotModel(self.mdlPlots)
        self._updatingSubPlot = False
        self.btnAddPlot.clicked.connect(self.mdlPlots.addPlot, F.AUC)
        self.btnRmPlot.clicked.connect(lambda:
                                       self.mdlPlots.removePlot(self.lstPlots.currentPlotIndex()), F.AUC)
        self.btnAddSubPlot.clicked.connect(self.mdlPlots.addSubPlot, F.AUC)
        self.btnAddSubPlot.clicked.connect(self.updateSubPlotView, F.AUC)
        self.btnRmSubPlot.clicked.connect(self.mdlPlots.removeSubPlot, F.AUC)
        self.lstPlotPerso.selectionModel().selectionChanged.connect(self.plotPersoSelectionChanged)
        self.btnRmPlotPerso.clicked.connect(self.mdlPlots.removePlotPerso, F.AUC)
        self.lstSubPlots.selectionModel().currentRowChanged.connect(self.changeCurrentSubPlot, F.AUC)

        for w, c in [
            (self.txtPlotName, Plot.name),
            (self.txtPlotDescription, Plot.description),
            (self.txtPlotResult, Plot.result),
            (self.sldPlotImportance, Plot.importance),
        ]:
            w.setModel(self.mdlPlots)
            w.setColumn(c)

        self.tabPlot.setEnabled(False)
        self.mdlPlots.updatePlotPersoButton()
        self.mdlCharacter.dataChanged.connect(self.mdlPlots.updatePlotPersoButton)
        self.lstOutlinePlots.setPlotModel(self.mdlPlots)
        self.lstOutlinePlots.setShowSubPlot(True)
        self.plotCharacterDelegate = outlineCharacterDelegate(self.mdlCharacter, self)
        self.lstPlotPerso.setItemDelegate(self.plotCharacterDelegate)
        self.plotDelegate = plotDelegate(self)
        self.lstSubPlots.setItemDelegateForColumn(PlotStep.meta, self.plotDelegate)

        # World
        self.treeWorld.setModel(self.mdlWorld)
        for i in range(self.mdlWorld.columnCount()):
            self.treeWorld.hideColumn(i)
        self.treeWorld.showColumn(0)
        self.btnWorldEmptyData.setMenu(self.mdlWorld.emptyDataMenu())
        self.treeWorld.selectionModel().selectionChanged.connect(self.changeCurrentWorld, F.AUC)
        self.btnAddWorld.clicked.connect(self.mdlWorld.addItem, F.AUC)
        self.btnRmWorld.clicked.connect(self.mdlWorld.removeItem, F.AUC)
        for w, c in [
            (self.txtWorldName, World.name),
            (self.txtWorldDescription, World.description),
            (self.txtWorldPassion, World.passion),
            (self.txtWorldConflict, World.conflict),
        ]:
            w.setModel(self.mdlWorld)
            w.setColumn(c)
        self.tabWorld.setEnabled(False)
        self.treeWorld.expandAll()

        # Outline
        self.treeRedacOutline.setModel(self.mdlOutline)
        self.treeOutlineOutline.setModelCharacters(self.mdlCharacter)
        self.treeOutlineOutline.setModelLabels(self.mdlLabels)
        self.treeOutlineOutline.setModelStatus(self.mdlStatus)

        self.redacMetadata.setModels(self.mdlOutline, self.mdlCharacter,
                                     self.mdlLabels, self.mdlStatus)
        self.outlineItemEditor.setModels(self.mdlOutline, self.mdlCharacter,
                                         self.mdlLabels, self.mdlStatus)

        self.treeOutlineOutline.setModel(self.mdlOutline)
        # self.redacEditor.setModel(self.mdlOutline)
        self.storylineView.setModels(self.mdlOutline, self.mdlCharacter, self.mdlPlots)

        self.treeOutlineOutline.selectionModel().selectionChanged.connect(self.outlineItemEditor.selectionChanged, F.AUC)
        self.treeOutlineOutline.clicked.connect(self.outlineItemEditor.selectionChanged, F.AUC)

        # Sync selection
        self.treeRedacOutline.selectionModel().selectionChanged.connect(self.redacMetadata.selectionChanged, F.AUC)
        self.treeRedacOutline.clicked.connect(self.redacMetadata.selectionChanged, F.AUC)

        self.treeRedacOutline.selectionModel().selectionChanged.connect(self.mainEditor.selectionChanged, F.AUC)

        # Cheat Sheet
        self.cheatSheet.setModels()

        # Debug
        self.mdlFlatData.setVerticalHeaderLabels(["General info", "Summary"])
        self.tblDebugFlatData.setModel(self.mdlFlatData)
        self.tblDebugPersos.setModel(self.mdlCharacter)
        self.tblDebugPersosInfos.setModel(self.mdlCharacter)
        self.tblDebugPersos.selectionModel().currentChanged.connect(
                lambda: self.tblDebugPersosInfos.setRootIndex(self.mdlCharacter.index(
                        self.tblDebugPersos.selectionModel().currentIndex().row(),
                        Character.name)), F.AUC)

        self.tblDebugPlots.setModel(self.mdlPlots)
        self.tblDebugPlotsPersos.setModel(self.mdlPlots)
        self.tblDebugSubPlots.setModel(self.mdlPlots)
        self.tblDebugPlots.selectionModel().currentChanged.connect(
                lambda: self.tblDebugPlotsPersos.setRootIndex(self.mdlPlots.index(
                        self.tblDebugPlots.selectionModel().currentIndex().row(),
                        Plot.characters)), F.AUC)
        self.tblDebugPlots.selectionModel().currentChanged.connect(
                lambda: self.tblDebugSubPlots.setRootIndex(self.mdlPlots.index(
                        self.tblDebugPlots.selectionModel().currentIndex().row(),
                        Plot.steps)), F.AUC)
        self.treeDebugWorld.setModel(self.mdlWorld)
        self.treeDebugOutline.setModel(self.mdlOutline)
        self.lstDebugLabels.setModel(self.mdlLabels)
        self.lstDebugStatus.setModel(self.mdlStatus)

    def disconnectAll(self, signal, oldHandler=None):
        # Disconnect all "oldHandler" slot connections for a signal
        #
        # Ref: PyQt Widget connect() and disconnect()
        #      https://stackoverflow.com/questions/21586643/pyqt-widget-connect-and-disconnect
        #
        # The loop is needed for safely disconnecting a specific handler,
        # because it may have been connected multiple times, and
        # disconnect only removes one connection at a time.
        while True:
            try:
                if oldHandler is not None:
                    signal.disconnect(oldHandler)
                else:
                    signal.disconnect()
            except TypeError:
                break

    def breakConnections(self):
        # Break connections for UI elements that were connected in makeConnections()

        # Characters
        self.disconnectAll(self.btnAddPerso.clicked, self.mdlCharacter.addCharacter)
        self.disconnectAll(self.btnRmPerso.clicked, self.lstCharacters.removeCharacter)
        self.disconnectAll(self.btnPersoColor.clicked, self.lstCharacters.choseCharacterColor)
        self.disconnectAll(self.btnPersoAddInfo.clicked, self.lstCharacters.addCharacterInfo)
        self.disconnectAll(self.btnPersoRmInfo.clicked, self.lstCharacters.removeCharacterInfo)

        # Plots
        self._updatingSubPlot = False
        self.disconnectAll(self.btnAddPlot.clicked, self.mdlPlots.addPlot)
        self.disconnectAll(self.btnRmPlot.clicked, lambda:
                                                   self.mdlPlots.removePlot(self.lstPlots.currentPlotIndex()))
        self.disconnectAll(self.btnAddSubPlot.clicked, self.mdlPlots.addSubPlot)
        self.disconnectAll(self.btnAddSubPlot.clicked, self.updateSubPlotView)
        self.disconnectAll(self.btnRmSubPlot.clicked, self.mdlPlots.removeSubPlot)
        self.disconnectAll(self.lstPlotPerso.selectionModel().selectionChanged, self.plotPersoSelectionChanged)
        self.disconnectAll(self.lstSubPlots.selectionModel().currentRowChanged, self.changeCurrentSubPlot)
        self.disconnectAll(self.btnRmPlotPerso.clicked, self.mdlPlots.removePlotPerso)

        self.disconnectAll(self.mdlCharacter.dataChanged, self.mdlPlots.updatePlotPersoButton)

        # World
        self.disconnectAll(self.treeWorld.selectionModel().selectionChanged, self.changeCurrentWorld)
        self.disconnectAll(self.btnAddWorld.clicked, self.mdlWorld.addItem)
        self.disconnectAll(self.btnRmWorld.clicked, self.mdlWorld.removeItem)

        # Outline
        self.disconnectAll(self.treeOutlineOutline.selectionModel().selectionChanged, self.outlineItemEditor.selectionChanged)
        self.disconnectAll(self.treeOutlineOutline.clicked, self.outlineItemEditor.selectionChanged)

        # Sync selection
        self.disconnectAll(self.treeRedacOutline.selectionModel().selectionChanged, self.redacMetadata.selectionChanged)
        self.disconnectAll(self.treeRedacOutline.clicked, self.redacMetadata.selectionChanged)

        self.disconnectAll(self.treeRedacOutline.selectionModel().selectionChanged, self.mainEditor.selectionChanged)

        # Debug
        self.disconnectAll(self.tblDebugPersos.selectionModel().currentChanged,
                lambda: self.tblDebugPersosInfos.setRootIndex(self.mdlCharacter.index(
                        self.tblDebugPersos.selectionModel().currentIndex().row(),
                        Character.name)))
        self.disconnectAll(self.tblDebugPlots.selectionModel().currentChanged,
                lambda: self.tblDebugPlotsPersos.setRootIndex(self.mdlPlots.index(
                        self.tblDebugPlots.selectionModel().currentIndex().row(),
                        Plot.characters)))
        self.disconnectAll(self.tblDebugPlots.selectionModel().currentChanged,
                lambda: self.tblDebugSubPlots.setRootIndex(self.mdlPlots.index(
                        self.tblDebugPlots.selectionModel().currentIndex().row(),
                        Plot.steps)))

    ###############################################################################
    # HELP
    ###############################################################################

    def about(self):
        self.dialog = aboutDialog(mw=self)
        self.dialog.setFixedSize(self.dialog.size())
        self.dialog.show()
        # Center about dialog
        r = self.dialog.geometry()
        r2 = self.geometry()
        self.dialog.move(r2.center() - r.center())

    ###############################################################################
    # GENERAL AKA UNSORTED
    ###############################################################################

    def clickCycle(self, i):
        if i == 0:  # step 2 - paragraph summary
            self.tabMain.setCurrentIndex(self.TabSummary)
            self.tabSummary.setCurrentIndex(1)
        if i == 1:  # step 3 - characters summary
            self.tabMain.setCurrentIndex(self.TabPersos)
            self.tabPersos.setCurrentIndex(0)
        if i == 2:  # step 4 - page summary
            self.tabMain.setCurrentIndex(self.TabSummary)
            self.tabSummary.setCurrentIndex(2)
        if i == 3:  # step 5 - characters description
            self.tabMain.setCurrentIndex(self.TabPersos)
            self.tabPersos.setCurrentIndex(1)
        if i == 4:  # step 6 - four page synopsis
            self.tabMain.setCurrentIndex(self.TabSummary)
            self.tabSummary.setCurrentIndex(3)
        if i == 5:  # step 7 - full character charts
            self.tabMain.setCurrentIndex(self.TabPersos)
            self.tabPersos.setCurrentIndex(2)
        if i == 6:  # step 8 - scene list
            self.tabMain.setCurrentIndex(self.TabPlots)

    def wordCount(self, i):

        src = {
            0: self.txtSummarySentence,
            1: self.txtSummaryPara,
            2: self.txtSummaryPage,
            3: self.txtSummaryFull
        }[i]

        lbl = {
            0: self.lblSummaryWCSentence,
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

        style.styleMainWindow(self)

        # Tool bar on the right
        self.toolbar = collapsibleDockWidgets(Qt.RightDockWidgetArea, self)
        self.toolbar.addCustomWidget(self.tr("Book summary"), self.grpPlotSummary, self.TabPlots, False)
        self.toolbar.addCustomWidget(self.tr("Project tree"), self.treeRedacWidget, self.TabRedac, True)
        self.toolbar.addCustomWidget(self.tr("Metadata"), self.redacMetadata, self.TabRedac, False)
        self.toolbar.addCustomWidget(self.tr("Story line"), self.storylineView, self.TabRedac, False)
        if self._toolbarState:
            self.toolbar.restoreState(self._toolbarState)

        # Hides navigation dock title bar
        self.dckNavigation.setTitleBarWidget(QWidget(None))

        # Custom "tab" bar on the left
        self.lstTabs.setIconSize(QSize(48, 48))
        for i in range(self.tabMain.count()):

            icons = [QIcon.fromTheme("stock_view-details"), #info
                     QIcon.fromTheme("application-text-template"), #applications-publishing
                     F.themeIcon("characters"),
                     F.themeIcon("plots"),
                     F.themeIcon("world"),
                     F.themeIcon("outline"),
                     QIcon.fromTheme("gtk-edit"),
                     QIcon.fromTheme("applications-debugging")
            ]
            self.tabMain.setTabIcon(i, icons[i])

            item = QListWidgetItem(self.tabMain.tabIcon(i),
                                   self.tabMain.tabText(i))
            item.setSizeHint(QSize(item.sizeHint().width(), 64))
            item.setToolTip(self.tabMain.tabText(i))
            item.setTextAlignment(Qt.AlignCenter)
            self.lstTabs.addItem(item)
        self.tabMain.tabBar().hide()
        self.lstTabs.currentRowChanged.connect(self.tabMain.setCurrentIndex)
        self.lstTabs.item(self.TabDebug).setHidden(not self.SHOW_DEBUG_TAB)
        self.tabMain.setTabEnabled(self.TabDebug, self.SHOW_DEBUG_TAB)
        self.tabMain.currentChanged.connect(self.lstTabs.setCurrentRow)

        # Splitters
        self.splitterPersos.setStretchFactor(0, 25)
        self.splitterPersos.setStretchFactor(1, 75)

        self.splitterPlot.setStretchFactor(0, 20)
        self.splitterPlot.setStretchFactor(1, 60)
        self.splitterPlot.setStretchFactor(2, 30)

        self.splitterWorld.setStretchFactor(0, 25)
        self.splitterWorld.setStretchFactor(1, 75)

        self.splitterOutlineH.setStretchFactor(0, 25)
        self.splitterOutlineH.setStretchFactor(1, 75)
        self.splitterOutlineV.setStretchFactor(0, 75)
        self.splitterOutlineV.setStretchFactor(1, 25)

        self.splitterRedacV.setStretchFactor(0, 75)
        self.splitterRedacV.setStretchFactor(1, 25)

        self.splitterRedacH.setStretchFactor(0, 30)
        self.splitterRedacH.setStretchFactor(1, 40)
        self.splitterRedacH.setStretchFactor(2, 30)

        # QFormLayout stretch
        for w in [self.txtWorldDescription, self.txtWorldPassion, self.txtWorldConflict]:
            s = w.sizePolicy()
            s.setVerticalStretch(1)
            w.setSizePolicy(s)

        # Help box
        references = [
            (self.lytTabOverview,
             self.tr("Enter information about your book, and yourself."),
             0),
            (self.lytSituation,
             self.tr(
                     """The basic situation, in the form of a 'What if...?' question. Ex: 'What if the most dangerous
                     evil wizard wasn't able to kill a baby?' (Harry Potter)"""),
             1),
            (self.lytSummary,
             self.tr(
                     """Take time to think about a one sentence (~50 words) summary of your book. Then expand it to
                     a paragraph, then to a page, then to a full summary."""),
             1),
            (self.lytTabPersos,
             self.tr("Create your characters."),
             0),
            (self.lytTabPlot,
             self.tr("Develop plots."),
             0),
            (self.lytTabContext,
             self.tr("Build worlds.  Create hierarchy of broad categories down to specific details."),
             0),
            (self.lytTabOutline,
             self.tr("Create the outline of your masterpiece."),
             0),
            (self.lytTabRedac,
             self.tr("Write."),
             0),
            (self.lytTabDebug,
             self.tr("Debug info. Sometimes useful."),
             0)
        ]

        for widget, text, pos in references:
            label = helpLabel(text, self)
            self.actShowHelp.toggled.connect(label.setVisible, F.AUC)
            widget.layout().insertWidget(pos, label)

        self.actShowHelp.setChecked(False)

        # Spellcheck
        if enchant:
            self.menuDict = QMenu(self.tr("Dictionary"))
            self.menuDictGroup = QActionGroup(self)
            self.updateMenuDict()
            self.menuTools.addMenu(self.menuDict)

            self.actSpellcheck.toggled.connect(self.toggleSpellcheck, F.AUC)
            self.dictChanged.connect(self.mainEditor.setDict, F.AUC)
            self.dictChanged.connect(self.redacMetadata.setDict, F.AUC)
            self.dictChanged.connect(self.outlineItemEditor.setDict, F.AUC)

        else:
            # No Spell check support
            self.actSpellcheck.setVisible(False)
            a = QAction(self.tr("Install PyEnchant to use spellcheck"), self)
            a.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
            a.triggered.connect(self.openPyEnchantWebPage, F.AUC)
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
            a.triggered.connect(self.setDictionary, F.AUC)
            self.menuDictGroup.addAction(a)
            self.menuDict.addAction(a)

    def setDictionary(self):
        if not enchant:
            return

        for i in self.menuDictGroup.actions():
            if i.isChecked():
                # self.dictChanged.emit(i.text().replace("&", ""))
                settings.dict = i.text().replace("&", "")

                # Find all textEditView from self, and toggle spellcheck
                for w in self.findChildren(textEditView, QRegExp(".*"),
                                           Qt.FindChildrenRecursively):
                    w.setDict(settings.dict)

    def openPyEnchantWebPage(self):
        F.openURL("http://pythonhosted.org/pyenchant/")

    def toggleSpellcheck(self, val):
        settings.spellcheck = val

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
    # TOOLS
    ###############################################################################

    def frequencyAnalyzer(self):
        self.fw = frequencyAnalyzer(self)
        self.fw.show()

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
            (self.tr("Tree"), "Tree", "view-list-tree"),
            (self.tr("Index cards"), "Cork", "view-cards"),
            (self.tr("Outline"), "Outline", "view-outline")
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
        self.menuView.addMenu(self.menuMode)
        self.menuView.addSeparator()

        # print("Generating menus with", settings.viewSettings)

        for mnu, mnud, icon in menus:
            m = QMenu(mnu, self.menuView)
            if icon:
                m.setIcon(QIcon.fromTheme(icon))
            for s, sd in submenus[mnud]:
                m2 = QMenu(s, m)
                agp = QActionGroup(m2)
                for v, vd in values:
                    a = QAction(v, m)
                    a.setCheckable(True)
                    a.setData("{},{},{}".format(mnud, sd, vd))
                    if settings.viewSettings[mnud][sd] == vd:
                        a.setChecked(True)
                    a.triggered.connect(self.setViewSettingsAction, F.AUC)
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
    # VIEW MODES
    ###############################################################################

    def setViewModeSimple(self):
        settings.viewMode = "simple"
        self.tabMain.setCurrentIndex(self.TabRedac)
        self.viewModeFictionVisibilitySwitch(False)
        self.actModeSimple.setChecked(True)

    def setViewModeFiction(self):
        settings.viewMode = "fiction"
        self.viewModeFictionVisibilitySwitch(True)
        self.actModeFiction.setChecked(True)

    def viewModeFictionVisibilitySwitch(self, val):
        """
        Switches the visibility of some UI components useful for fiction only
        @param val: sets visibility to val
        """

        # Menu navigation & button in toolbar
        self.toolbar.setDockVisibility(self.dckNavigation, val)

        # POV in metadata
        from manuskript.ui.views.propertiesView import propertiesView
        for w in findWidgetsOfClass(propertiesView):
            w.lblPOV.setVisible(val)
            w.cmbPOV.setVisible(val)

        # POV in outline view
        if val is None and Outline.POV in settings.outlineViewColumns:
            settings.outlineViewColumns.remove(Outline.POV)

        from manuskript.ui.views.outlineView import outlineView
        for w in findWidgetsOfClass(outlineView):
            w.hideColumns()

        # TODO: clean up all other fiction things in non-fiction view mode
        # Character in search widget
        # POV in settings / views

    ###############################################################################
    # IMPORT / EXPORT
    ###############################################################################

    def doImport(self):
        self.dialog = importerDialog(mw=self)
        self.dialog.show()

        r = self.dialog.geometry()
        r2 = self.geometry()
        self.dialog.move(r2.center() - r.center())

    def doCompile(self):
        self.dialog = exporterDialog(mw=self)
        self.dialog.show()

        r = self.dialog.geometry()
        r2 = self.geometry()
        self.dialog.move(r2.center() - r.center())
