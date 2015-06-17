#!/usr/bin/env python
#--!-- coding: utf8 --!--

from qt import *

from ui.settings import *
from enums import *
from functions import *
import settings
# Spell checker support
try:
    import enchant
except ImportError:
    enchant = None

class settingsWindow(QWidget, Ui_Settings):
    
    def __init__(self, mainWindow):
        QWidget.__init__(self)
        self.setupUi(self)
        
        self.mw = mainWindow
        
        # General
        self.cmbStyle.addItems(list(QStyleFactory.keys()))
        self.cmbStyle.setCurrentIndex([i.lower() for i in list(QStyleFactory.keys())].index(qApp.style().objectName()))
        self.cmbStyle.currentIndexChanged[str].connect(self.setStyle)
        
        self.txtAutoSave.setValidator(QIntValidator(0, 999, self))
        self.txtAutoSaveNoChanges.setValidator(QIntValidator(0, 999, self))
        self.chkAutoSave.setChecked(settings.autoSave)
        self.chkAutoSaveNoChanges.setChecked(settings.autoSaveNoChanges)
        self.txtAutoSave.setText(str(settings.autoSaveDelay))
        self.txtAutoSaveNoChanges.setText(str(settings.autoSaveNoChangesDelay))
        self.chkSaveOnQuit.setChecked(settings.saveOnQuit)
        self.chkAutoSave.stateChanged.connect(self.saveSettingsChanged)
        self.chkAutoSaveNoChanges.stateChanged.connect(self.saveSettingsChanged)
        self.chkSaveOnQuit.stateChanged.connect(self.saveSettingsChanged)
        self.txtAutoSave.textEdited.connect(self.saveSettingsChanged)
        self.txtAutoSaveNoChanges.textEdited.connect(self.saveSettingsChanged)
        
        # Views
        lst = ["Nothing", "POV", "Label", "Progress", "Compile"]
        for cmb in self.viewSettingsDatas():
            item, part = self.viewSettingsDatas()[cmb]
            cmb.setCurrentIndex(lst.index(settings.viewSettings[item][part]))
            cmb.currentIndexChanged.connect(self.viewSettingsChanged)
        
        for chk in self.outlineColumnsData():
            col = self.outlineColumnsData()[chk]
            chk.setChecked(col in settings.outlineViewColumns)
            chk.stateChanged.connect(self.outlineColumnsChanged)
        
        # Labels
        self.lstLabels.setModel(self.mw.mdlLabels)
        self.lstLabels.setRowHidden(0, True)
        self.lstLabels.clicked.connect(self.updateLabelColor)
        self.btnLabelAdd.clicked.connect(self.addLabel)
        self.btnLabelRemove.clicked.connect(self.removeLabel)
        self.btnLabelColor.clicked.connect(self.setLabelColor)
        
        # Statuses
        self.lstStatus.setModel(self.mw.mdlStatus)
        self.lstStatus.setRowHidden(0, True)
        self.btnStatusAdd.clicked.connect(self.addStatus)
        self.btnStatusRemove.clicked.connect(self.removeStatus)
        
####################################################################################################
#                                           GENERAL                                                #
####################################################################################################
        
    def setStyle(self, style):
        #Save style to Qt Settings
        settings = QSettings(qApp.organizationName(), qApp.applicationName())
        settings.setValue("applicationStyle", style)
        qApp.setStyle(style)
        
    def saveSettingsChanged(self):
        if self.txtAutoSave.text() in ["", "0"]:
            self.txtAutoSave.setText("1")
        if self.txtAutoSaveNoChanges.text() in ["", "0"]:
            self.txtAutoSaveNoChanges.setText("1")
        
        settings.autoSave = True if self.chkAutoSave.checkState() else False
        settings.autoSaveNoChanges = True if self.chkAutoSaveNoChanges.checkState() else False
        settings.saveOnQuit = True if self.chkSaveOnQuit.checkState() else False
        settings.autoSaveDelay = int(self.txtAutoSave.text())
        settings.autoSaveNoChangesDelay = int(self.txtAutoSaveNoChanges.text())
        self.mw.saveTimer.setInterval(settings.autoSaveDelay * 60 * 1000)
        self.mw.saveTimerNoChanges.setInterval(settings.autoSaveNoChangesDelay * 1000)

####################################################################################################
#                                           VIEWS                                                  #
####################################################################################################

    def viewSettingsDatas(self):
        return {
            self.cmbTreeIcon: ("Tree", "Icon"),
            self.cmbTreeText: ("Tree", "Text"),
            self.cmbTreeBackground: ("Tree", "Background"),
            self.cmbOutlineIcon: ("Outline", "Icon"),
            self.cmbOutlineText: ("Outline", "Text"),
            self.cmbOutlineBackground: ("Outline", "Background"),
            self.cmbCorkIcon: ("Cork", "Icon"),
            self.cmbCorkText: ("Cork", "Text"),
            self.cmbCorkBackground: ("Cork", "Background"),
            self.cmbCorkBorder: ("Cork", "Border"),
            self.cmbCorkCorner: ("Cork", "Corner")
            }
        
    def viewSettingsChanged(self):
        cmb = self.sender()
        lst = ["Nothing", "POV", "Label", "Progress", "Compile"]
        item, part = self.viewSettingsDatas()[cmb]
        element = lst[cmb.currentIndex()]
        self.mw.setViewSettings(item, part, element)
        
    def outlineColumnsData(self):
        return {
            self.chkOutlineTitle: Outline.title.value,
            self.chkOutlinePOV: Outline.POV.value,
            self.chkOutlineLabel: Outline.label.value,
            self.chkOutlineStatus: Outline.status.value,
            self.chkOutlineCompile: Outline.compile.value,
            self.chkOutlineWordCount: Outline.wordCount.value,
            self.chkOutlineGoal: Outline.goal.value,
            self.chkOutlinePercentage: Outline.goalPercentage.value,
            }
        
    def outlineColumnsChanged(self):
        chk = self.sender()
        val = True if chk.checkState() else False
        col = self.outlineColumnsData()[chk]
        if val and not col in settings.outlineViewColumns:
            settings.outlineViewColumns.append(col)
        elif not val and col in settings.outlineViewColumns:
            settings.outlineViewColumns.remove(col)
        
        # Update views
        self.mw.redacEditor.outlineView.hideColumns()
        self.mw.treePlanOutline.hideColumns()
        

####################################################################################################
#                                           STATUS                                                 #
####################################################################################################

    def addStatus(self):
        self.mw.mdlStatus.appendRow(QStandardItem(self.tr("New status")))
        
    def removeStatus(self):
        for i in self.lstStatus.selectedIndexes():
            self.mw.mdlStatus.removeRows(i.row(), 1)
        
    def updateLabelColor(self, index):
        px = QPixmap(64, 64)
        px.fill(iconColor(self.mw.mdlLabels.item(index.row()).icon()))
        self.btnLabelColor.setIcon(QIcon(px))
        self.btnLabelColor.setEnabled(True)
    
####################################################################################################
#                                           LABELS                                                 #
####################################################################################################
    
    def addLabel(self):
        px = QPixmap(32, 32)
        px.fill(Qt.transparent)
        self.mw.mdlLabels.appendRow(QStandardItem(QIcon(px), self.tr("New label")))
    
    def removeLabel(self):
        for i in self.lstLabels.selectedIndexes():
            self.mw.mdlLabels.removeRows(i.row(), 1)
            
    def setLabelColor(self):
        index = self.lstLabels.currentIndex()
        color = iconColor(self.mw.mdlLabels.item(index.row()).icon())
        self.colorDialog = QColorDialog(color, self)
        color = self.colorDialog.getColor(color)
        px = QPixmap(32, 32)
        px.fill(color)
        self.mw.mdlLabels.item(index.row()).setIcon(QIcon(px))
        