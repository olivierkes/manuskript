#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from ui.editors.mainEditor_ui import *
from ui.editors.editorWidget import *
from functions import *

class mainEditor(QWidget, Ui_mainEditor):
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        
        self.mw = mainWindow()
        self.tab.tabCloseRequested.connect(self.closeTab)
        self.tab.currentChanged.connect(self.tabChanged)
        
        self.sldCorkSizeFactor.valueChanged.connect(
             self.setCorkSizeFactor, AUC)
        self.btnRedacFolderCork.toggled.connect(
             self.sldCorkSizeFactor.setVisible, AUC)
        self.btnRedacFolderText.clicked.connect(
             lambda v: self.setFolderView("text"), AUC)
        self.btnRedacFolderCork.clicked.connect(
             lambda v: self.setFolderView("cork"), AUC)
        self.btnRedacFolderOutline.clicked.connect(
             lambda v: self.setFolderView("outline"), AUC)
        
        self.btnRedacFullscreen.clicked.connect(
             self.showFullScreen, AUC)
        
        
###############################################################################
# TABS
###############################################################################
      
    def currentEditor(self):
        return self.tab.currentWidget()
    
    def tabChanged(self, index):
        #FIXME: Update UI
        pass
    
    def closeTab(self, index):
        #FIXME: submit data if textedit?
        self.tab.removeTab(index)
      
###############################################################################
# SELECTION AND UPDATES
###############################################################################
        
    def selectionChanged(self):
        if len(self.mw.treeRedacOutline.selectionModel().
                    selection().indexes()) == 0:
            hidden = False
        else:
            idx = self.mw.treeRedacOutline.currentIndex()
            if idx.isValid():
                hidden = not idx.internalPointer().isFolder()
            else:
                hidden = False

        self.btnRedacFolderText.setHidden(hidden)
        self.btnRedacFolderCork.setHidden(hidden)
        self.btnRedacFolderOutline.setHidden(hidden)
        self.sldCorkSizeFactor.setHidden(hidden)
        self.btnRedacFullscreen.setVisible(hidden)
        
        #FIXME
        #self.redacEditor.setView
        
        
    def setCurrentModelIndex(self, index, newTab=False):
        
        if not index.isValid():
            return
        
        item = index.internalPointer()
        
        editor = editorWidget(self)
        editor.setCurrentModelIndex(index)
        self.tab.addTab(editor, item.title())
        self.tab.setCurrentIndex(self.tab.count() - 1)
        
        #FIXME: check if tab is already open
        
        #self.redacEditor.txtRedacText.setCurrentModelIndex
        #FIXME
        
###############################################################################
# UI
###############################################################################
        
        
    def updateStats(self, index=None):  
        if index:
            item = index.internalPointer()
        else:
            item = self._model.rootItem
        
        if not item:
            item = self._model.rootItem
        
        wc = item.data(Outline.wordCount.value)
        goal = item.data(Outline.goal.value)
        progress = item.data(Outline.goalPercentage.value)
        #mw = qApp.activeWindow()
            
        if not wc:
            wc = 0
        if goal:
            self.lblRedacProgress.show()
            rect = self.lblRedacProgress.geometry()
            rect = QRect(QPoint(0, 0), rect.size())
            self.px = QPixmap(rect.size())
            self.px.fill(Qt.transparent)
            p = QPainter(self.px)
            drawProgress(p, rect, progress, 2)
            del p
            self.lblRedacProgress.setPixmap(self.px)
            self.lblRedacWC.setText(self.tr("{} words / {}").format(wc, goal))
        else:
            self.lblRedacProgress.hide()
            self.lblRedacWC.setText(self.tr("{} words").format(wc))
        
###############################################################################
# VIEWS
###############################################################################
        
    def setFolderView(self, view):
        #FIXME
        if self.currentEditor():
            self.currentEditor().setFolderView(view)
        pass
        #self.redacEditor.setFolderView(settings.folderView)
        
    def setCorkSizeFactor(self, val):
        #FIXME
        pass
        #self.redacEditor.setCorkSizeFactor
        
    def updateCorkView(self):
        pass
        #FIXME
        #self.redacEditor.corkView.viewport().update()
        
    def updateCorkBackground(self):
        pass
        #FIXME
        #self.redacEditor.corkView.updateBackground()
    
    def updateTreeView(self):
        pass
        #FIXME
        #self.redacEditor.outlineView.viewport().update()
        
    def showFullScreen(self):
        pass
        #FIXME
        #self.redacEditor.showFullscreen(self.treeRedacOutline.currentIndex()
        
###############################################################################
# DICT AND STUFF LIKE THAT
###############################################################################

    def setDict(self, dict):
        pass
        #FIXME
        
    def toggleSpellcheck(self, val):
        pass
        #FIXME
        #self.redacEditor.toggleSpellcheck(val)
        
    