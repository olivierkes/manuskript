#!/usr/bin/env python
#--!-- coding: utf8 --!--

from qt import *

from ui.settings import *
from enums import *
from functions import *

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
        
        # Labels
        self.lstLabels.setModel(self.mw.mdlLabels)
        self.lstLabels.setRowHidden(0, True)
        self.lstLabels.clicked.connect(self.updateLabelColor)
        self.btnLabelAdd.clicked.connect(self.addLabel)
        self.btnLabelRemove.clicked.connect(self.removeLabel)
        self.btnLabelColor.clicked.connect(self.setLabelColor)
        
    def updateLabelColor(self, index):
        px = QPixmap(64, 64)
        px.fill(iconColor(self.mw.mdlLabels.item(index.row()).icon()))
        self.btnLabelColor.setIcon(QIcon(px))
        self.btnLabelColor.setEnabled(True)
    
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
        