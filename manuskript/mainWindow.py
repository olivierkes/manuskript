#!/usr/bin/env python
# --!-- coding: utf8 --!--
import importlib
import os
import re

from PyQt5.Qt import qVersion, PYQT_VERSION_STR
from PyQt5.QtCore import (pyqtSignal, QSignalMapper, QTimer, QSettings, Qt, QPoint,
                          QRegExp, QUrl, QSize, QModelIndex)
from PyQt5.QtGui import QStandardItemModel, QIcon, QColor, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QHeaderView, qApp, QMenu, QActionGroup, QAction, QStyle, QListWidgetItem, \
    QLabel, QDockWidget, QWidget, QMessageBox, QLineEdit, QTextEdit, QTreeView, QDialog, QTableView

from manuskript import settings
from manuskript.enums import Character, PlotStep, Plot, World, Outline
from manuskript.functions import wordCount, appPath, findWidgetsOfClass, openURL, showInFolder
import manuskript.functions as F
from manuskript import loadSave
from manuskript.functions.history.History import History
from manuskript.logging import getLogFilePath
from manuskript.models.characterModel import characterModel
from manuskript.models import outlineModel
from manuskript.models.plotModel import plotModel
from manuskript.models.worldModel import worldModel
from manuskript.settingsWindow import settingsWindow
from manuskript.ui import style
from manuskript.ui import characterInfoDialog
from manuskript.ui.about import aboutDialog
from manuskript.ui.collapsibleDockWidgets import collapsibleDockWidgets
from manuskript.ui.importers.importer import importerDialog
from manuskript.ui.exporters.exporter import exporterDialog
from manuskript.ui.helpLabel import helpLabel
from manuskript.ui.mainWindow import Ui_MainWindow
from manuskript.ui.tools.frequencyAnalyzer import frequencyAnalyzer
from manuskript.ui.tools.targets import TargetsDialog
from manuskript.ui.views.outlineDelegates import outlineCharacterDelegate
from manuskript.ui.views.plotDelegate import plotDelegate
from manuskript.ui.views.MDEditView import MDEditView
from manuskript.ui.statusLabel import statusLabel
from manuskript.ui.bulkInfoManager import Ui_BulkInfoManager

# Spellcheck support
from manuskript.ui.views.textEditView import textEditView
from manuskript.functions import Spellchecker

import logging
LOGGER = logging.getLogger(__name__)

class MainWindow(QMainWindow, Ui_MainWindow):
    # dictChanged = pyqtSignal(str)

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
        self.projectDirty = None  # has the user made any unsaved changes ?
        self._lastFocus = None
        self._lastMDEditView = None
        self._defaultCursorFlashTime = 1000 # Overridden at startup with system
                                            # value. In manuskript.main.
        self._autoLoadProject = None  # Used to load a command line project
        self.sessionStartWordCount = 0  # Used to track session targets
        self.history = History()
        self._previousSelectionEmpty = True

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

        self.cmbSummary.setCurrentIndex(0)
        self.cmbSummary.currentIndexChanged.emit(0)

        # Main Menu
        for i in [self.actSave, self.actSaveAs, self.actCloseProject,
                  self.menuEdit, self.menuView, self.menuOrganize,
                  self.menuNavigate, self.menuTools, self.menuHelp, self.actImport,
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
        self.actSearch.triggered.connect(self.doSearch)
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

        # Main menu:: Navigate
        self.actBack.triggered.connect(self.navigateBack)
        self.actForward.triggered.connect(self.navigateForward)

        # Main Menu:: view
        self.generateViewMenu()
        self.actModeGroup = QActionGroup(self)
        self.actModeSimple.setActionGroup(self.actModeGroup)
        self.actModeFiction.setActionGroup(self.actModeGroup)
        self.actModeSimple.triggered.connect(self.setViewModeSimple)
        self.actModeFiction.triggered.connect(self.setViewModeFiction)

        # Main Menu:: Tool
        self.actToolFrequency.triggered.connect(self.frequencyAnalyzer)
        self.actToolTargets.triggered.connect(self.sessionTargets)
        self.actSupport.triggered.connect(self.support)
        self.actLocateLog.triggered.connect(self.locateLogFile)
        self.actAbout.triggered.connect(self.about)

        self.makeUIConnections()

        # Tools non-modal windows
        self.td = None  # Targets Dialog
        self.fw = None  # Frequency Window

        # Bulk Character Info Management
        self.tabsData = self.saveCharacterTabs()  # Used for restoring tabsData with loadCharacterTabs() methods.
        self.BulkManageUi = None
        self.bulkAffectedCharacters = []
        self.isPersoBulkModeEnabled = False

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
        tabIndex = self.tabMain.currentIndex()

        if tabIndex == self.TabPersos:
            selectedCharacters = self.lstCharacters.currentCharacters()
            characterSelectionIsEmpty = not any(selectedCharacters)

            if characterSelectionIsEmpty:
                self.pushHistory(("character", None))
                self._previousSelectionEmpty = True
            else:
                character = selectedCharacters[0]
                self.pushHistory(("character", character.ID()))
                self._previousSelectionEmpty = False
        elif tabIndex == self.TabPlots:
            id = self.lstPlots.currentPlotID()
            self.pushHistory(("plot", id))
            self._previousSelectionEmpty = id is None
        elif tabIndex == self.TabWorld:
            index = self.mdlWorld.selectedIndex()

            if index.isValid():
                id = self.mdlWorld.ID(index)
                self.pushHistory(("world", id))
                self._previousSelectionEmpty = id is not None
            else:
                self.pushHistory(("world", None))
                self._previousSelectionEmpty = True
        elif tabIndex == self.TabOutline:
            index = self.treeOutlineOutline.selectionModel().currentIndex()
            if index.isValid():
                id = self.mdlOutline.ID(index)
                self.pushHistory(("outline", id))
                self._previousSelectionEmpty = id is not None
            else:
                self.pushHistory(("outline", None))
                self._previousSelectionEmpty = False
        elif tabIndex == self.TabRedac:
            index = self.treeRedacOutline.selectionModel().currentIndex()
            if index.isValid():
                id = self.mdlOutline.ID(index)
                self.pushHistory(("redac", id))
                self._previousSelectionEmpty = id is not None
            else:
                self.pushHistory(("redac", None))
                self._previousSelectionEmpty = False
        else:
            self.pushHistory(("main", self.tabMain.currentIndex()))
            self._previousSelectionEmpty = False

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

    def projectName(self):
        """
        Returns a user-friendly name for the loaded project.
        """
        pName = os.path.split(self.currentProject)[1]
        if pName.endswith('.msk'):
            pName=pName[:-4]
        return pName

    ###############################################################################
    # OUTLINE
    ###############################################################################

    def outlineChanged(self, selected, deselected):
        index = self.treeOutlineOutline.selectionModel().currentIndex()
        if not index.isValid():
            self.pushHistory(("outline", None))
            self._previousSelectionEmpty = True
            return
        
        self.pushHistory(("outline", self.mdlOutline.ID(index)))
        self._previousSelectionEmpty = False


    def outlineRemoveItemsRedac(self):
        self.treeRedacOutline.delete()

    def outlineRemoveItemsOutline(self):
        self.treeOutlineOutline.delete()

    ###############################################################################
    # CHARACTERS
    ###############################################################################

    def setPersoBulkMode(self, enabled: bool):
        if enabled and self.BulkManageUi is None: # Delete all tabs and create the manager one
            # Create the widget
            bulkPersoInfoManager = QWidget()
            bulkPersoInfoManagerUi = Ui_BulkInfoManager()
            bulkPersoInfoManagerUi.setupUi(bulkPersoInfoManager)

            self.BulkManageUi = bulkPersoInfoManagerUi  # for global use

            model = QStandardItemModel()

            # Set the column headers
            model.setColumnCount(2)
            model.setHorizontalHeaderLabels([self.tr("Name"), self.tr("Value")])

            # Set the width
            self.updatePersoInfoView(bulkPersoInfoManagerUi.tableView)

            bulkPersoInfoManagerUi.tableView.setModel(model)  # Set the model of tableView

            self.tabPersos.clear()
            self.tabPersos.addTab(bulkPersoInfoManager, self.tr("Bulk Info Manager"))
            self.isPersoBulkModeEnabled = True
            self.refreshBulkAffectedCharacters()

            # Showing the character names on the label
            labelText = self.createCharacterSelectionString()
            bulkPersoInfoManagerUi.lblCharactersDynamic.setText(labelText)

            # Making the connections
            self.makeBulkInfoConnections(bulkPersoInfoManagerUi)

        elif enabled and self.BulkManageUi is not None:  # If yet another character is selected, refresh the label
            labelText = self.createCharacterSelectionString()
            self.BulkManageUi.lblCharactersDynamic.setText(labelText)

        else:  # Delete manager tab and restore the others
            if self.BulkManageUi is not None:
                self.tabPersos.clear()
                self.loadCharacterTabs()
            self.BulkManageUi = None
            self.bulkAffectedCharacters.clear()

    def createCharacterSelectionString(self):
        self.refreshBulkAffectedCharacters()
        labelText = ""
        length = len(self.bulkAffectedCharacters)
        for i in range(length-1):
            labelText += '"' + self.bulkAffectedCharacters[i] + '"' + ", "

        labelText += '"' + self.bulkAffectedCharacters[length-1] + '"'

        return labelText

    def makeBulkInfoConnections(self, bulkUi):
        # A lambda has to be used to pass in the argument
        bulkUi.btnPersoBulkAddInfo.clicked.connect(lambda: self.addBulkInfo(bulkUi))
        bulkUi.btnPersoBulkRmInfo.clicked.connect(lambda: self.removeBulkInfo(bulkUi))
        bulkUi.btnPersoBulkApply.clicked.connect(lambda: self.applyBulkInfo(bulkUi))

    def applyBulkInfo(self, bulkUi):
        selectedItems = self.lstCharacters.currentCharacterIDs()

        # Get the data from the tableview
        model = bulkUi.tableView.model()
        if model.rowCount() == 0:
            QMessageBox.warning(self, self.tr("No Entries!"),
                                self.tr("Please add entries to apply to the selected characters."))
            return

        # Loop through each selected character and add the bulk info to them
        for ID in selectedItems:
            for row in range(model.rowCount()):
                description = model.item(row, 0).text()
                value = model.item(row, 1).text()
                self.lstCharacters._model.addCharacterInfo(ID, description, value)

        QMessageBox.information(self, self.tr("Bulk Info Applied"),
                                self.tr("The bulk info has been applied to the selected characters."))

        # Remove all rows from the table
        model.removeRows(0, model.rowCount())

    def addBulkInfo(self, bulkUi): # Adds an item to the list
        charInfoDialog = QDialog()
        charInfoUi = characterInfoDialog.Ui_characterInfoDialog()
        charInfoUi.setupUi(charInfoDialog)

        if charInfoDialog.exec_() == QDialog.Accepted:
            # User clicked OK, get the input values
            description = charInfoUi.descriptionLineEdit.text()
            value = charInfoUi.valueLineEdit.text()

            # Add a new row to the model with the description and value
            row = [QStandardItem(description), QStandardItem(value)]

            bulkUi.tableView.model().appendRow(row)

            bulkUi.tableView.update()

    def removeBulkInfo(self, bulkUi):
        # Get the selected rows
        selection = bulkUi.tableView.selectionModel().selectedRows()

        # Iterate over the rows and remove them (reversed, so the iteration is not affected)
        for index in reversed(selection):
            bulkUi.tableView.model().removeRow(index.row())

    def saveCharacterTabs(self):
        tabsData = []
        for i in range(self.tabPersos.count()):
            tabData = {}
            widget = self.tabPersos.widget(i)
            tabData['widget'] = widget
            tabData['title'] = self.tabPersos.tabText(i)
            tabsData.append(tabData)
        return tabsData

    def loadCharacterTabs(self):
        for tabData in self.tabsData:
            widget = tabData['widget']
            title = tabData['title']
            self.tabPersos.addTab(widget, title)

    def handleCharacterSelectionChanged(self):
        selectedCharacters = self.lstCharacters.currentCharacters()
        characterSelectionIsEmpty = not any(selectedCharacters)
        if characterSelectionIsEmpty:
            self.pushHistory(("character", None))
            self.tabPersos.setEnabled(False)
            self._previousSelectionEmpty = True
            return

        cList = list(filter(None, self.lstCharacters.currentCharacters())) #cList contains all valid characters
        character = cList[0]
        self.changeCurrentCharacter(character)

        self.pushHistory(("character", character.ID()))
        self._previousSelectionEmpty = False

        if len(selectedCharacters) > 1:
            self.setPersoBulkMode(True)
        else:
            if self.BulkManageUi is not None:
                self.refreshBulkAffectedCharacters()
                self.BulkManageUi.lblCharactersDynamic.setText( self.createCharacterSelectionString() )

                tableview_model = self.BulkManageUi.tableView.model()
                if tableview_model.rowCount() > 0:
                    confirm = QMessageBox.warning(
                        self, self.tr("Un-applied data!"),
                        self.tr("There are un-applied entries in this tab. Discard them?"),
                        QMessageBox.Yes | QMessageBox.No,
                        defaultButton = QMessageBox.No
                    )
                    if confirm != QMessageBox.Yes:
                        return

            self.setPersoBulkMode(False)
        self.tabPersos.setEnabled(True)

    def refreshBulkAffectedCharacters(self): # Characters affected by a potential bulk-info modification
        self.bulkAffectedCharacters = []
        for character in self.lstCharacters.currentCharacters():
            self.bulkAffectedCharacters.append(character.name())

    def changeCurrentCharacter(self, character):
        if character is None:
            return

        index = character.index()

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
        self.updateCharacterColor(character.ID())

        # Slider importance
        self.updateCharacterImportance(character.ID())

        # POV state
        self.updateCharacterPOVState(character.ID())

        # Character Infos
        self.tblPersoInfos.setRootIndex(index)

        if self.mdlCharacter.rowCount(index):
            self.updatePersoInfoView(self.tblPersoInfos)

    def updatePersoInfoView(self, infoView):
        infoView.horizontalHeader().setStretchLastSection(True)
        infoView.horizontalHeader().setMinimumSectionSize(20)
        infoView.horizontalHeader().setMaximumSectionSize(500)
        infoView.verticalHeader().hide()

    def updateCharacterColor(self, ID):
        c = self.mdlCharacter.getCharacterByID(ID)
        color = c.color().name()
        self.btnPersoColor.setStyleSheet("background:{};".format(color))

    def updateCharacterImportance(self, ID):
        c = self.mdlCharacter.getCharacterByID(ID)
        self.sldPersoImportance.setValue(int(c.importance()))

    def updateCharacterPOVState(self, ID):
        c = self.mdlCharacter.getCharacterByID(ID)
        self.disconnectAll(self.chkPersoPOV.stateChanged, self.lstCharacters.changeCharacterPOVState)

        if c.pov():
            self.chkPersoPOV.setCheckState(Qt.Checked)
        else:
            self.chkPersoPOV.setCheckState(Qt.Unchecked)

        try:
            self.chkPersoPOV.stateChanged.connect(self.lstCharacters.changeCharacterPOVState, F.AUC)
            self.chkPersoPOV.setEnabled(len(self.mdlOutline.findItemsByPOV(ID)) == 0)
        except TypeError:
            #don't know what's up with this
            pass

    def deleteCharacter(self):
        ID = self.lstCharacters.removeCharacters()
        if ID is None:
            return
        for itemID in self.mdlOutline.findItemsByPOV(ID):
            item = self.mdlOutline.getItemByID(itemID)
            if item:
                item.resetPOV()

    ###############################################################################
    # PLOTS
    ###############################################################################

    def changeCurrentPlot(self):
        index = self.lstPlots.currentPlotIndex()
        id = self.lstPlots.currentPlotID()

        if not index.isValid():
            self.tabPlot.setEnabled(False)
            self.pushHistory(("plot", None))
            self._previousSelectionEmpty = True
            return

        self.pushHistory(("plot", id))
        self._previousSelectionEmpty = False

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
            self.pushHistory(("world", None))
            self._previousSelectionEmpty = True
            return

        self.pushHistory(("world", self.mdlWorld.ID(index)))
        self._previousSelectionEmpty = False

        self.tabWorld.setEnabled(True)
        self.txtWorldName.setCurrentModelIndex(index)
        self.txtWorldDescription.setCurrentModelIndex(index)
        self.txtWorldPassion.setCurrentModelIndex(index)
        self.txtWorldConflict.setCurrentModelIndex(index)

    ###############################################################################
    # EDITOR
    ###############################################################################

    def redacOutlineChanged(self):
        index = self.treeRedacOutline.selectionModel().currentIndex()
        if not index.isValid():
            self.pushHistory(("redac", None))
            self._previousSelectionEmpty = True
            return
        
        self.pushHistory(("redac", self.mdlOutline.ID(index)))
        self._previousSelectionEmpty = False

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
    def doSearch(self):
        "Do a global search."
        self.dckSearch.show()
        self.dckSearch.activateWindow()
        searchTextInput = self.dckSearch.findChild(QLineEdit, 'searchTextInput')
        searchTextInput.setFocus()
        searchTextInput.selectAll()
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

    # Navigate
    
    def navigateBack(self):
        self.history.back()

    def navigateForward(self):
        self.history.forward()

    def pushHistory(self, entry):
        if self._previousSelectionEmpty:
            self.history.replace(entry)
        else:
            self.history.next(entry)

    def navigated(self, event):
        if event.entry:
            first_entry = event.entry[0]

            if first_entry == "character":
                if self.tabMain.currentIndex() != self.TabPersos:
                    self.tabMain.setCurrentIndex(self.TabPersos)

                if event.entry[1] is None:
                    self.lstCharacters.setCurrentItem(None)
                    self.lstCharacters.clearSelection()
                else:
                    if self.lstCharacters.currentCharacterID() != event.entry[1]:
                        char = self.lstCharacters.getItemByID(event.entry[1])
                        if char != None:
                            self.lstCharacters.clearSelection()
                            self.lstCharacters.setCurrentItem(char)
            elif first_entry == "plot":
                if self.tabMain.currentIndex() != self.TabPlots:
                    self.tabMain.setCurrentIndex(self.TabPlots)

                if event.entry[1] is None:
                    self.lstPlots.setCurrentItem(None)
                else:
                    index = self.lstPlots.currentPlotIndex()
                    if index and index.row() != event.entry[1]:
                        plot = self.lstPlots.getItemByID(event.entry[1])
                        if plot != None:
                            self.lstPlots.setCurrentItem(plot)
            elif first_entry == "world":
                if self.tabMain.currentIndex() != self.TabWorld:
                    self.tabMain.setCurrentIndex(self.TabWorld)

                if event.entry[1] is None:
                    self.treeWorld.selectionModel().clear()
                else:
                    index = self.mdlWorld.selectedIndex()
                    if index and self.mdlWorld.ID(index) != event.entry[1]:
                        world = self.mdlWorld.indexByID(event.entry[1])
                        if world != None:
                            self.treeWorld.setCurrentIndex(world)
            elif first_entry == "outline":
                if self.tabMain.currentIndex() != self.TabOutline:
                    self.tabMain.setCurrentIndex(self.TabOutline)

                if event.entry[1] is None:
                    self.treeOutlineOutline.selectionModel().clear()
                else:
                    index = self.treeOutlineOutline.selectionModel().currentIndex()
                    if index and self.mdlOutline.ID(index) != event.entry[1]:
                        outline = self.mdlOutline.getIndexByID(event.entry[1])
                        if outline is not None:
                            self.treeOutlineOutline.setCurrentIndex(outline)
            elif first_entry == "redac":
                if self.tabMain.currentIndex() != self.TabRedac:
                    self.tabMain.setCurrentIndex(self.TabRedac)

                if event.entry[1] is None:
                    self.treeRedacOutline.selectionModel().clear()
                else:
                    index = self.treeRedacOutline.selectionModel().currentIndex()
                    if index and self.mdlOutline.ID(index) != event.entry[1]:
                        outline = self.mdlOutline.getIndexByID(event.entry[1])
                        if outline is not None:
                            self.treeRedacOutline.setCurrentIndex(outline)
            elif first_entry == "main":
                if self.tabMain.currentIndex() != event.entry[1]:
                    self.lstTabs.setCurrentRow(event.entry[1])

        self.actBack.setEnabled(event.position > 0)
        self.actForward.setEnabled(event.position < event.count - 1)

    ###############################################################################
    # LOAD AND SAVE
    ###############################################################################

    def loadProject(self, project, loadFromFile=True):
        """Loads the project ``project``.

        If ``loadFromFile`` is False, then it does not load datas from file.
        It assumes that the datas have been populated in a different way."""

        # Convert project path to OS norm
        project = os.path.normpath(project)

        if loadFromFile and not os.path.exists(project):
            LOGGER.warning("The file {} does not exist. Has it been moved or deleted?".format(project))
            F.statusMessage(
                    self.tr("The file {} does not exist. Has it been moved or deleted?").format(project), importance=3)
            return

        if loadFromFile:
            # Load empty settings
            importlib.reload(settings)
            settings.initDefaultValues()

            # Load data
            self.loadEmptyDatas()
            
            if not self.loadDatas(project):
                self.closeProject()
                return

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
        self.mdlStatus.dataChanged.connect(self.startTimerNoChanges)
        self.mdlLabels.dataChanged.connect(self.startTimerNoChanges)

        self.saveTimerNoChanges.timeout.connect(self.saveDatas)
        self.saveTimerNoChanges.stop()

        # UI
        for i in [self.actOpen, self.menuRecents]:
            i.setEnabled(False)
        for i in [self.actSave, self.actSaveAs, self.actCloseProject,
                  self.menuEdit, self.menuView, self.menuOrganize,
                  self.menuNavigate,
                  self.menuTools, self.menuHelp, self.actImport,
                  self.actCompile, self.actSettings]:
            i.setEnabled(True)
        # We force to emit even if it opens on the current tab
        self.tabMain.currentChanged.emit(settings.lastTab)

        # Make sure we can update the window title later.
        self.currentProject = project
        self.projectDirty = False
        QSettings().setValue("lastProject", project)

        item = self.mdlOutline.rootItem
        wc = item.data(Outline.wordCount)
        self.sessionStartWordCount = int(wc) if wc != "" else 0
        # Add project name to Window's name
        self.setWindowTitle(self.projectName() + " - " + self.tr("Manuskript"))

        # Reset history
        self.history.reset()

        # Show main Window
        self.switchToProject()

    def handleUnsavedChanges(self):
        """
        There may be some currently unsaved changes, but the action the user triggered
        will result in the project or application being closed. To save, or not to save?

        Or just bail out entirely?

        Sometimes it is best to just ask.
        """

        if not self.projectDirty:
            return True  # no unsaved changes, all is good

        msg = QMessageBox(QMessageBox.Question,
            self.tr("Save project?"),
            "<p><b>" +
                self.tr("Save changes to project \"{}\" before closing?").format(self.projectName()) +
            "</b></p>" +
            "<p>" +
                self.tr("Your changes will be lost if you don't save them.") +
            "</p>",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

        ret = msg.exec()

        if ret == QMessageBox.Cancel:
            return False  # the situation has not been handled, cancel action

        if ret == QMessageBox.Save:
            self.saveDatas()

        return True  # the situation has been handled


    def closeProject(self):

        if not self.currentProject:
            return

        # Make sure data is saved.
        if (self.projectDirty and settings.saveOnQuit == True):
             self.saveDatas()
        elif not self.handleUnsavedChanges():
             return  # user cancelled action

        # Close open tabs in editor
        self.mainEditor.closeAllTabs()

        self.currentProject = None
        self.projectDirty = None
        QSettings().setValue("lastProject", "")

        # Clear datas
        self.loadEmptyDatas()
        self.saveTimer.stop()
        self.saveTimerNoChanges.stop()
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
        # Specific settings to save before quitting
        settings.lastTab = self.tabMain.currentIndex()

        if self.currentProject:
            # Remembering the current items (stores outlineItem's ID)
            settings.openIndexes = self.mainEditor.tabSplitter.openIndexes()

            # Call close on the main window to clean children widgets
            if self.mainEditor:
                self.mainEditor.close()

            # Save data from models
            if settings.saveOnQuit:
                self.saveDatas()
            elif not self.handleUnsavedChanges():
                event.ignore() # user opted to cancel the close action

            # closeEvent
            # QMainWindow.closeEvent(self, event)  # Causing segfaults?

        # Close non-modal windows if they are open.
        if self.td:
            self.td.close()
        if self.fw:
            self.fw.close()

        # User may have canceled close event, so make sure we indeed want to close.
        # This is necessary because self.updateDockVisibility() hides UI elements.
        if event.isAccepted():
            # Save State and geometry and other things
            appSettings = QSettings(qApp.organizationName(), qApp.applicationName())
            appSettings.setValue("geometry", self.saveGeometry())
            appSettings.setValue("windowState", self.saveState())
            appSettings.setValue("metadataState", self.redacMetadata.saveState())
            appSettings.setValue("revisionsState", self.redacMetadata.revisions.saveState())
            appSettings.setValue("splitterRedacH", self.splitterRedacH.saveState())
            appSettings.setValue("splitterRedacV", self.splitterRedacV.saveState())
            appSettings.setValue("toolbar", self.toolbar.saveState())

            # If we are not in the welcome window, we update the visibility
            # of the docks widgets
            if self.stack.currentIndex() == 1:
                self.updateDockVisibility()

            # Storing the visibility of docks to restore it on restart
            appSettings.setValue("docks", self._dckVisibility)

    def startTimerNoChanges(self):
        """
        Something changed in the project that requires auto-saving.
        """
        self.projectDirty = True

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

        # Stop the timer before saving: if auto-saving fails (bugs out?) we don't want it
        # to keep trying and continuously hitting the failure condition. Nor do we want to
        # risk a scenario where the timer somehow triggers a new save while saving.
        self.saveTimerNoChanges.stop()

        if self.currentProject is None:
            # No UI feedback here as this code path indicates a race condition that happens
            # after the user has already closed the project through some way. But in that
            # scenario, this code should not be reachable to begin with.
            LOGGER.error("There is no current project to save.")
            return

        r = loadSave.saveProject()  # version=0

        projectName = os.path.basename(self.currentProject)
        if r:
            self.projectDirty = False  # successful save, clear dirty flag

            feedback = self.tr("Project {} saved.").format(projectName)
            F.statusMessage(feedback, importance=0)
            LOGGER.info("Project {} saved.".format(projectName))
        else:
            feedback = self.tr("WARNING: Project {} not saved.").format(projectName)
            F.statusMessage(feedback, importance=3)
            LOGGER.warning("Project {} not saved.".format(projectName))

    def loadEmptyDatas(self):
        self.mdlFlatData = QStandardItemModel(self)
        self.mdlCharacter = characterModel(self)
        self.mdlLabels = QStandardItemModel(self)
        self.mdlStatus = QStandardItemModel(self)
        self.mdlPlots = plotModel(self)
        self.mdlOutline = outlineModel(self)
        self.mdlWorld = worldModel(self)

    def loadDatas(self, project):
        errors = loadSave.loadProject(project)

        # Giving some feedback
        if not errors:
            LOGGER.info("Project {} loaded.".format(project))
            F.statusMessage(
                    self.tr("Project {} loaded.").format(project), 2000)
        else:
            LOGGER.error("Project {} loaded with some errors:".format(project))
            for e in errors:
                LOGGER.error(" * {} wasn't found in project file.".format(e))
            F.statusMessage(
                    self.tr("Project {} loaded with some errors.").format(project), 5000, importance = 3)
        
        if project in errors:
            LOGGER.error("Loading project {} failed.".format(project))
            F.statusMessage(
                    self.tr("Loading project {} failed.").format(project), 5000, importance = 3)

            return False
        
        return True

    ###############################################################################
    # MAIN CONNECTIONS
    ###############################################################################

    def makeUIConnections(self):
        "Connections that have to be made once only, even when a new project is loaded."
        # Characters
        self.txtPersosFilter.textChanged.connect(self.lstCharacters.setFilter, F.AUC)
        self.lstCharacters.itemSelectionChanged.connect(self.handleCharacterSelectionChanged, F.AUC)

        # Plots
        self.txtPlotFilter.textChanged.connect(self.lstPlots.setFilter, F.AUC)
        self.lstPlots.currentItemChanged.connect(self.changeCurrentPlot, F.AUC)
        self.lstSubPlots.clicked.connect(self.changeCurrentSubPlot, F.AUC)

        # Outline
        self.btnRedacAddFolder.clicked.connect(self.treeRedacOutline.addFolder, F.AUC)
        self.btnOutlineAddFolder.clicked.connect(self.treeOutlineOutline.addFolder, F.AUC)
        self.btnRedacAddText.clicked.connect(self.treeRedacOutline.addText, F.AUC)
        self.btnOutlineAddText.clicked.connect(self.treeOutlineOutline.addText, F.AUC)
        self.btnRedacRemoveItem.clicked.connect(self.outlineRemoveItemsRedac, F.AUC)
        self.btnOutlineRemoveItem.clicked.connect(self.outlineRemoveItemsOutline, F.AUC)

        self.tabMain.currentChanged.connect(self.toolbar.setCurrentGroup)
        self.tabMain.currentChanged.connect(self.tabMainChanged)

        self.history.navigated.connect(self.navigated)

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
        self.updatePersoInfoView(self.tblPersoInfos)
        self.lstCharacters.setCharactersModel(self.mdlCharacter)
        self.tblPersoInfos.setModel(self.mdlCharacter)
        try:
            self.btnAddPerso.clicked.connect(self.lstCharacters.addCharacter, F.AUC)
            self.btnRmPerso.clicked.connect(self.deleteCharacter, F.AUC)

            self.btnPersoColor.clicked.connect(self.lstCharacters.choseCharacterColor, F.AUC)
            self.chkPersoPOV.stateChanged.connect(self.lstCharacters.changeCharacterPOVState, F.AUC)

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

        self.treeOutlineOutline.selectionModel().selectionChanged.connect(self.outlineChanged, F.AUC)
        self.treeOutlineOutline.selectionModel().selectionChanged.connect(self.outlineItemEditor.selectionChanged, F.AUC)
        self.treeOutlineOutline.clicked.connect(self.outlineItemEditor.selectionChanged, F.AUC)

        # Sync selection
        self.treeRedacOutline.selectionModel().selectionChanged.connect(self.redacOutlineChanged, F.AUC)
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
                if oldHandler != None:
                    signal.disconnect(oldHandler)
                else:
                    signal.disconnect()
            except TypeError:
                break

    def breakConnections(self):
        # Break connections for UI elements that were connected in makeConnections()

        # Characters
        self.disconnectAll(self.btnAddPerso.clicked, self.lstCharacters.addCharacter)
        self.disconnectAll(self.btnRmPerso.clicked, self.deleteCharacter)

        self.disconnectAll(self.btnPersoColor.clicked, self.lstCharacters.choseCharacterColor)
        self.disconnectAll(self.chkPersoPOV.stateChanged, self.lstCharacters.changeCharacterPOVState)

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
        
        self.disconnectAll(self.history.navigated)

    ###############################################################################
    # HELP
    ###############################################################################

    def centerChildWindow(self, win):
        r = win.geometry()
        r2 = self.geometry()
        win.move(r2.center() - QPoint(int(r.width()/2), int(r.height()/2)))

    def support(self):
        openURL("https://github.com/olivierkes/manuskript/wiki/Technical-Support")

    def locateLogFile(self):
        logfile = getLogFilePath()

        # Make sure we are even logging to a file.
        if not logfile:
            QMessageBox(QMessageBox.Information,
                self.tr("Sorry!"),
                "<p><b>" +
                    self.tr("This session is not being logged.") +
                "</b></p>",
                QMessageBox.Ok).exec()
            return

        # Remind user that log files are at their best once they are complete.
        msg = QMessageBox(QMessageBox.Information,
            self.tr("A log file is a Work in Progress!"),
            "<p><b>" +
                self.tr("The log file \"{}\" will continue to be written to until Manuskript is closed.").format(os.path.basename(logfile)) +
            "</b></p>" +
            "<p>" +
                self.tr("It will now be displayed in your file manager, but is of limited use until you close Manuskript.") +
            "</p>",
            QMessageBox.Ok)

        ret = msg.exec()

        # Open the filemanager.
        if ret == QMessageBox.Ok:
            if not showInFolder(logfile):
                # If everything convenient fails, at least make sure the user can browse to its location manually.
                QMessageBox(QMessageBox.Critical,
                    self.tr("Error!"),
                    "<p><b>" +
                        self.tr("An error was encountered while trying to show the log file below in your file manager.") +
                    "</b></p>" +
                    "<p>" +
                        logfile +
                    "</p>",
                    QMessageBox.Ok).exec()


    def about(self):
        self.dialog = aboutDialog(mw=self)
        self.dialog.setFixedSize(self.dialog.size())
        self.dialog.show()
        # Center about dialog
        self.centerChildWindow(self.dialog)

    ###############################################################################
    # GENERAL AKA UNSORTED
    ###############################################################################

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
                                   "")  # Start with no text, will be set by set_sidebar_labels_visible
            item.setToolTip(self.tabMain.tabText(i))
            item.setTextAlignment(Qt.AlignCenter)
            self.lstTabs.addItem(item)
        self.tabMain.tabBar().hide()
        self.lstTabs.currentRowChanged.connect(self.tabMain.setCurrentIndex)
        self.lstTabs.item(self.TabDebug).setHidden(not self.SHOW_DEBUG_TAB)
        self.tabMain.setTabEnabled(self.TabDebug, self.SHOW_DEBUG_TAB)
        self.tabMain.currentChanged.connect(self.lstTabs.setCurrentRow)

        # Apply sidebar labels visibility setting
        self.set_sidebar_labels_visible(settings.show_sidebar_labels)

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
        if Spellchecker.isInstalled():
            self.menuDict = QMenu(self.tr("Dictionary"))
            self.menuDictGroup = QActionGroup(self)
            self.updateMenuDict()
            self.menuTools.addMenu(self.menuDict)

            self.actSpellcheck.toggled.connect(self.toggleSpellcheck, F.AUC)
            # self.dictChanged.connect(self.mainEditor.setDict, F.AUC)
            # self.dictChanged.connect(self.redacMetadata.setDict, F.AUC)
            # self.dictChanged.connect(self.outlineItemEditor.setDict, F.AUC)

        else:
            # No Spell check support
            self.actSpellcheck.setVisible(False)
            for lib, requirement in Spellchecker.supportedLibraries().items():
                a = QAction(self.tr("Install {}{} to use spellcheck").format(lib, requirement or ""), self)
                a.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                # Need to bound the lib argument otherwise the lambda uses the same lib value across all calls
                def gen_slot_cb(l):
                    return lambda: self.openSpellcheckWebPage(l)
                a.triggered.connect(gen_slot_cb(lib), F.AUC)
                self.menuTools.addAction(a)


    ###############################################################################
    # SPELLCHECK
    ###############################################################################

    def updateMenuDict(self):

        if not Spellchecker.isInstalled():
            return

        self.menuDict.clear()
        dictionaries = Spellchecker.availableDictionaries()

        # Set first run dictionary
        if settings.dict is None:
            settings.dict = Spellchecker.getDefaultDictionary()

        # Check if project dict is unavailable on this machine
        dict_available = False
        for lib, dicts in dictionaries.items():
            if dict_available:
                break
            for i in dicts:
                if Spellchecker.normalizeDictName(lib, i) == settings.dict:
                    dict_available = True
                    break
        # Reset dict to default one if it's unavailable
        if not dict_available:
            settings.dict = Spellchecker.getDefaultDictionary()

        for lib, dicts in dictionaries.items():
            if len(dicts) > 0:
                a = QAction(lib, self)
            else:
                a = QAction(self.tr("{} has no installed dictionaries").format(lib), self)
            a.setEnabled(False)
            self.menuDict.addAction(a)
            for i in dicts:
                a = QAction(i, self)
                a.data = lib
                a.setCheckable(True)
                if Spellchecker.normalizeDictName(lib, i) == settings.dict:
                    a.setChecked(True)
                a.triggered.connect(self.setDictionary, F.AUC)
                self.menuDictGroup.addAction(a)
                self.menuDict.addAction(a)
            self.menuDict.addSeparator()

        # If a new dictionary was chosen, apply the change and re-enable spellcheck if it was enabled.
        if not dict_available:
            self.setDictionary()
            self.toggleSpellcheck(settings.spellcheck)

        for lib, requirement in Spellchecker.supportedLibraries().items():
            if lib not in dictionaries:
                a = QAction(self.tr("{}{} is not installed").format(lib, requirement or ""), self)
                a.setEnabled(False)
                self.menuDict.addAction(a)
                self.menuDict.addSeparator()

    def setDictionary(self):
        if not Spellchecker.isInstalled():
            return

        for i in self.menuDictGroup.actions():
            if i.isChecked():
                # self.dictChanged.emit(i.text().replace("&", ""))
                settings.dict = Spellchecker.normalizeDictName(i.data, i.text().replace("&", ""))

                # Find all textEditView from self, and toggle spellcheck
                for w in self.findChildren(textEditView, QRegExp(".*"),
                                           Qt.FindChildrenRecursively):
                    w.setDict(settings.dict)

    def openSpellcheckWebPage(self, lib):
        F.openURL(Spellchecker.getLibraryURL(lib))

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
        self.centerChildWindow(self.sw)
        if tab:
            self.sw.setTab(tab)
        self.sw.show()

    ###############################################################################
    # TOOLS
    ###############################################################################

    def frequencyAnalyzer(self):
        self.fw = frequencyAnalyzer(self)
        self.fw.show()
        self.centerChildWindow(self.fw)

    def sessionTargets(self):
        self.td = TargetsDialog(self)
        self.td.show()
        self.centerChildWindow(self.td)

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

        # LOGGER.debug("Generating menus with %s.", settings.viewSettings)

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
        # Warn about buggy Qt versions and import crash
        #
        # (Py)Qt 5.11 and 5.12 have a bug that can cause crashes when simply
        # setting up various UI elements.
        # This has been reported and verified to happen with File -> Import.
        # See PR #611.
        if re.match("^5\\.1[12](\\.?|$)", qVersion()):
            warning1 = self.tr("PyQt / Qt versions 5.11 and 5.12 are known to cause a crash which might result in a loss of data.")
            warning2 = self.tr("PyQt {} and Qt {} are in use.").format(qVersion(), PYQT_VERSION_STR)

            # Don't translate for debug log.
            LOGGER.warning(warning1)
            LOGGER.warning(warning2)

            msg = QMessageBox(QMessageBox.Warning,
                self.tr("Proceed with import at your own risk"),
                "<p><b>" +
                    warning1 +
                "</b></p>" +
                "<p>" +
                    warning2 +
                "</p>",
                QMessageBox.Abort | QMessageBox.Ignore)
            msg.setDefaultButton(QMessageBox.Abort)

            # Return because user heeds warning
            if msg.exec() == QMessageBox.Abort:
                return

        # Proceed with Import
        self.dialog = importerDialog(mw=self)
        self.dialog.show()
        self.centerChildWindow(self.dialog)


    def doCompile(self):
        self.dialog = exporterDialog(mw=self)
        self.dialog.show()
        self.centerChildWindow(self.dialog)

    ###############################################################################
    # SIDEBAR
    ###############################################################################
    def set_sidebar_labels_visible(self, visible):
        """Show or hide text labels in the sidebar navigation."""
        # Icon size is 48x48
        iconOnlyWidth = 48
        withLabelsWidth = 120

        LOGGER.debug(f"Setting sidebar labels visible: {visible}")
        LOGGER.debug(f"lstTabs width before change: {self.lstTabs.width()}px")
        LOGGER.debug(f"dckNavigation width before change: {self.dckNavigation.width()}px")

        if visible:
            # Show icon with text below
            self.lstTabs.setSpacing(0)
            self.lstTabs.setMinimumWidth(withLabelsWidth)
            self.lstTabs.setMaximumWidth(withLabelsWidth)
            # Make dock widget follow lstTabs size
            self.dckNavigation.setMinimumWidth(withLabelsWidth)
            self.dckNavigation.setMaximumWidth(withLabelsWidth)
            for i in range(self.lstTabs.count()):
                item = self.lstTabs.item(i)
                item.setText(self.tabMain.tabText(i))
                item.setSizeHint(QSize(withLabelsWidth, 64))
            LOGGER.debug(f"lstTabs width after showing labels: {self.lstTabs.width()}px (target: {withLabelsWidth}px)")
            LOGGER.debug(f"dckNavigation width after showing labels: {self.dckNavigation.width()}px")
        else:
            # Show icon only - compact width, no text gap
            self.lstTabs.setSpacing(0)
            self.lstTabs.setMinimumWidth(iconOnlyWidth)
            self.lstTabs.setMaximumWidth(iconOnlyWidth)
            # Make dock widget follow lstTabs size
            self.dckNavigation.setMinimumWidth(iconOnlyWidth)
            self.dckNavigation.setMaximumWidth(iconOnlyWidth)
            for i in range(self.lstTabs.count()):
                item = self.lstTabs.item(i)
                item.setText("")
                # Set height to exact icon size to eliminate text label gap
                item.setSizeHint(QSize(iconOnlyWidth, iconOnlyWidth))
            LOGGER.debug(f"lstTabs width after hiding labels: {self.lstTabs.width()}px (target: {iconOnlyWidth}px)")
            LOGGER.debug(f"dckNavigation width after hiding labels: {self.dckNavigation.width()}px")
