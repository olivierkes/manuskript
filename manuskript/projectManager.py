import importlib
import os

from PyQt5.QtCore import QSettings, QTimer, QSize
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QMessageBox

from manuskript import settings, loadSave
import manuskript.functions as F
from manuskript.logging import getLogFilePath
from manuskript.models.characterModel import characterModel
from manuskript.models import outlineModel
from manuskript.models.plotModel import plotModel
from manuskript.models.worldModel import worldModel
from manuskript.enums import Outline

import logging
LOGGER = logging.getLogger(__name__)


class ProjectManager:
    def __init__(self, window):
        self.window = window
        self.saveTimer = QTimer()
        self.saveTimerNoChanges = QTimer()

    def loadProject(self, project, loadFromFile=True):
        """Loads the project ``project``.

        If ``loadFromFile`` is False, then it does not load datas from file.
        It assumes that the datas have been populated in a different way."""

        # Convert project path to OS norm
        project = os.path.normpath(project)

        if loadFromFile and not os.path.exists(project):
            LOGGER.warning("The file {} does not exist. Has it been moved or deleted?".format(project))
            F.statusMessage(
                    self.window.tr("The file {} does not exist. Has it been moved or deleted?").format(project), importance=3)
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

        self.window.makeConnections()

        # Load settings
        if settings.openIndexes and settings.openIndexes != [""]:
            self.window.mainEditor.tabSplitter.restoreOpenIndexes(settings.openIndexes)
        self.window.generateViewMenu()
        self.window.mainEditor.sldCorkSizeFactor.setValue(settings.corkSizeFactor)
        self.window.actSpellcheck.setChecked(settings.spellcheck)
        self.window.toggleSpellcheck(settings.spellcheck)
        self.window.updateMenuDict()
        self.window.setDictionary()

        iconSize = settings.viewSettings["Tree"]["iconSize"]
        self.window.treeRedacOutline.setIconSize(QSize(iconSize, iconSize))
        self.window.mainEditor.setFolderView(settings.folderView)
        self.window.mainEditor.updateFolderViewButtons(settings.folderView)
        self.window.mainEditor.tabSplitter.updateStyleSheet()
        self.window.tabMain.setCurrentIndex(settings.lastTab)
        self.window.mainEditor.updateCorkBackground()
        if settings.viewMode == "simple":
            self.window.setViewModeSimple()
        else:
            self.window.setViewModeFiction()

        # Set autosave
        self.saveTimer.setInterval(settings.autoSaveDelay * 60 * 1000)
        self.saveTimer.setSingleShot(False)
        self.saveTimer.timeout.connect(self.saveDatas)
        if settings.autoSave:
            self.saveTimer.start()

        # Set autosave if no changes
        self.saveTimerNoChanges.setInterval(settings.autoSaveNoChangesDelay * 1000)
        self.saveTimerNoChanges.setSingleShot(True)
        self.window.mdlFlatData.dataChanged.connect(self.startTimerNoChanges)
        self.window.mdlOutline.dataChanged.connect(self.startTimerNoChanges)
        self.window.mdlCharacter.dataChanged.connect(self.startTimerNoChanges)
        self.window.mdlPlots.dataChanged.connect(self.startTimerNoChanges)
        self.window.mdlWorld.dataChanged.connect(self.startTimerNoChanges)
        self.window.mdlStatus.dataChanged.connect(self.startTimerNoChanges)
        self.window.mdlLabels.dataChanged.connect(self.startTimerNoChanges)

        self.saveTimerNoChanges.timeout.connect(self.saveDatas)
        self.saveTimerNoChanges.stop()

        # UI
        for i in [self.window.actOpen, self.window.menuRecents]:
            i.setEnabled(False)
        for i in [self.window.actSave, self.window.actSaveAs, self.window.actCloseProject,
                  self.window.menuEdit, self.window.menuView, self.window.menuOrganize,
                  self.window.menuNavigate,
                  self.window.menuTools, self.window.menuHelp, self.window.actImport,
                  self.window.actCompile, self.window.actSettings]:
            i.setEnabled(True)
        # We force to emit even if it opens on the current tab
        self.window.tabMain.currentChanged.emit(settings.lastTab)

        # Make sure we can update the window title later.
        self.window.currentProject = project
        self.window.projectDirty = False
        QSettings().setValue("lastProject", project)

        item = self.window.mdlOutline.rootItem
        wc = item.data(Outline.wordCount)
        self.window.sessionStartWordCount = int(wc) if wc != "" else 0
        # Add project name to Window's name
        self.window.setWindowTitle(self.window.projectName() + " - " + self.window.tr("Manuskript"))

        # Reset history
        self.window.history.reset()

        # Show main Window
        self.window.switchToProject()

    def handleUnsavedChanges(self):
        """
        There may be some currently unsaved changes, but the action the user triggered
        will result in the project or application being closed. To save, or not to save?

        Or just bail out entirely?

        Sometimes it is best to just ask.
        """

        if not self.window.projectDirty:
            return True  # no unsaved changes, all is good

        msg = QMessageBox(QMessageBox.Question,
            self.window.tr("Save project?"),
            "<p><b>" +
                self.window.tr("Save changes to project \"{}\" before closing?").format(self.window.projectName()) +
            "</b></p>" +
            "<p>" +
                self.window.tr("Your changes will be lost if you don't save them.") +
            "</p>",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

        ret = msg.exec()

        if ret == QMessageBox.Cancel:
            return False  # the situation has not been handled, cancel action

        if ret == QMessageBox.Save:
            self.saveDatas()

        return True  # the situation has been handled


    def closeProject(self):

        if not self.window.currentProject:
            return

        # Make sure data is saved.
        if (self.window.projectDirty and settings.saveOnQuit == True):
             self.saveDatas()
        elif not self.handleUnsavedChanges():
             return  # user cancelled action

        # Close open tabs in editor
        self.window.mainEditor.closeAllTabs()

        self.window.currentProject = None
        self.window.projectDirty = None
        QSettings().setValue("lastProject", "")

        # Clear datas
        self.loadEmptyDatas()
        self.saveTimer.stop()
        self.saveTimerNoChanges.stop()
        loadSave.clearSaveCache()

        self.window.breakConnections()

        # UI
        for i in [self.window.actOpen, self.window.menuRecents]:
            i.setEnabled(True)
        for i in [self.window.actSave, self.window.actSaveAs, self.window.actCloseProject,
                  self.window.menuEdit, self.window.menuView, self.window.menuOrganize,
                  self.window.menuTools, self.window.menuHelp, self.window.actImport,
                  self.window.actCompile, self.window.actSettings]:
            i.setEnabled(False)

        # Set Window's name - no project loaded
        self.window.setWindowTitle(self.window.tr("Manuskript"))

        # Reload recent files
        self.window.welcome.updateValues()

        # Show welcome dialog
        self.window.switchToWelcome()

    def startTimerNoChanges(self):
        """
        Something changed in the project that requires auto-saving.
        """
        self.window.projectDirty = True

        if settings.autoSaveNoChanges:
            self.saveTimerNoChanges.start()

    def saveDatas(self, projectName=None):
        """Saves the current project (in self.currentProject).

        If ``projectName`` is given, currentProject becomes projectName.
        In other words, it "saves as...".
        """

        if projectName:
            self.window.currentProject = projectName
            QSettings().setValue("lastProject", projectName)

        # Stop the timer before saving: if auto-saving fails (bugs out?) we don't want it
        # to keep trying and continuously hitting the failure condition. Nor do we want to
        # risk a scenario where the timer somehow triggers a new save while saving.
        self.saveTimerNoChanges.stop()

        if self.window.currentProject is None:
            # No UI feedback here as this code path indicates a race condition that happens
            # after the user has already closed the project through some way. But in that
            # scenario, this code should not be reachable to begin with.
            LOGGER.error("There is no current project to save.")
            return

        r = loadSave.saveProject()  # version=0

        projectName = os.path.basename(self.window.currentProject)
        if r:
            self.window.projectDirty = False  # successful save, clear dirty flag

            feedback = self.window.tr("Project {} saved.").format(projectName)
            F.statusMessage(feedback, importance=0)
            LOGGER.info("Project {} saved.".format(projectName))
        else:
            feedback = self.window.tr("WARNING: Project {} not saved.").format(projectName)
            F.statusMessage(feedback, importance=3)
            LOGGER.warning("Project {} not saved.".format(projectName))

    def loadEmptyDatas(self):
        self.window.mdlFlatData = QStandardItemModel(self.window)
        self.window.mdlCharacter = characterModel(self.window)
        self.window.mdlLabels = QStandardItemModel(self.window)
        self.window.mdlStatus = QStandardItemModel(self.window)
        self.window.mdlPlots = plotModel(self.window)
        self.window.mdlOutline = outlineModel(self.window)
        self.window.mdlWorld = worldModel(self.window)

    def loadDatas(self, project):
        errors = loadSave.loadProject(project)

        # Giving some feedback
        if not errors:
            LOGGER.info("Project {} loaded.".format(project))
            F.statusMessage(
                    self.window.tr("Project {} loaded.").format(project), 2000)
        else:
            LOGGER.error("Project {} loaded with some errors:".format(project))
            for e in errors:
                LOGGER.error(" * {} wasn't found in project file.".format(e))
            F.statusMessage(
                    self.window.tr("Project {} loaded with some errors.").format(project), 5000, importance = 3)
        
        if project in errors:
            LOGGER.error("Loading project {} failed.".format(project))
            F.statusMessage(
                    self.window.tr("Loading project {} failed.").format(project), 5000, importance = 3)

            return False
        
        return True