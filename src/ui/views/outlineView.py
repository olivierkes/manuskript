#!/usr/bin/env python
#--!-- coding: utf8 --!--
 



from qt import *
from enums import *
from functions import *
from ui.views.treeOutlineDelegates import *
from ui.views.dndView import *

class outlineView(QTreeView, dndView):
    
    def __init__(self, parent=None, modelPersos=None):
        QTreeView.__init__(self, parent)
        dndView.__init__(self, parent)
        self.modelPersos = modelPersos
        self.header().setStretchLastSection(False)
        
    def setModelPersos(self, model):
        # This is used by treeOutlinePersoDelegate to select character
        self.modelPersos = model
        
    def setModel(self, model):
        QTreeView.setModel(self, model)
        
        # Setting delegates
        self.treePlanOutlinePersoDelegate = treeOutlinePersoDelegate(self.modelPersos)
        self.setItemDelegateForColumn(Outline.POV.value, self.treePlanOutlinePersoDelegate)
        self.treePlanOutlineCompileDelegate = treeOutlineCompileDelegate()
        self.setItemDelegateForColumn(Outline.compile.value, self.treePlanOutlineCompileDelegate)
        self.treePlanOutlineStatusDelegate = treeOutlineStatusDelegate()
        self.setItemDelegateForColumn(Outline.status.value, self.treePlanOutlineStatusDelegate)
        self.treePlanOutlineGoalPercentageDelegate = treeOutlineGoalPercentageDelegate()
        self.setItemDelegateForColumn(Outline.goalPercentage.value, self.treePlanOutlineGoalPercentageDelegate)
        
        # Hiding columns
        for c in range(1, self.model().columnCount()):
            self.hideColumn(c)
        for c in [Outline.POV.value, Outline.status.value, Outline.compile.value, 
                  Outline.wordCount.value, Outline.goal.value, Outline.goalPercentage.value]:
            self.showColumn(c)
        
        self.header().setSectionResizeMode(Outline.title.value, QHeaderView.Stretch)
        self.header().setSectionResizeMode(Outline.POV.value, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(Outline.status.value, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(Outline.compile.value, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(Outline.wordCount.value, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(Outline.goal.value, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(Outline.goalPercentage.value, QHeaderView.ResizeToContents)
        
    def setRootIndex(self, index):
        QTreeView.setRootIndex(self, index)
        self.treePlanOutlineGoalPercentageDelegate = treeOutlineGoalPercentageDelegate(index)
        self.setItemDelegateForColumn(Outline.goalPercentage.value, self.treePlanOutlineGoalPercentageDelegate)
        
    def dragMoveEvent(self, event):
        dndView.dragMoveEvent(self, event)
        QTreeView.dragMoveEvent(self, event)
        