#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from ui.views.propertiesView_ui import *

class propertiesView(QWidget, Ui_propertiesView):
    
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.setupUi(self)
        self.txtGoal.setColumn(Outline.setGoal.value)
        
    def setModels(self, mdlOutline, mdlPersos, mdlLabels, mdlStatus):
        self.cmbPOV.setModels(mdlPersos, mdlOutline)
        self.cmbLabel.setModels(mdlLabels, mdlOutline)
        self.cmbStatus.setModels(mdlStatus, mdlOutline)
        self.chkCompile.setModel(mdlOutline)
        self.txtTitle.setModel(mdlOutline)
        self.txtGoal.setModel(mdlOutline)
        
    def getIndexes(self, sourceView):
        "Returns a list of indexes from list of QItemSelectionRange"
        indexes = []
        
        for i in sourceView.selectionModel().selection().indexes():
            if i.column() != 0: 
                continue
            
            if i not in indexes:
                indexes.append(i)
                
        return indexes
        
    def selectionChanged(self, sourceView):
        
        indexes = self.getIndexes(sourceView)
        #print(indexes)
        if len(indexes) == 0:
            self.setEnabled(False)
        
        elif len(indexes) == 1:
            self.setEnabled(True)
            idx = indexes[0]
            self.cmbPOV.setCurrentModelIndex(idx)
            self.cmbLabel.setCurrentModelIndex(idx)
            self.cmbStatus.setCurrentModelIndex(idx)
            self.chkCompile.setCurrentModelIndex(idx)
            self.txtTitle.setCurrentModelIndex(idx)
            self.txtGoal.setCurrentModelIndex(idx)
            
        else:
            print("Multiple selection, Work in progress")
            self.txtTitle.setCurrentModelIndexes(indexes)
            self.txtGoal.setCurrentModelIndexes(indexes)
            self.chkCompile.setCurrentModelIndexes(indexes)
            #FIXME: do the other views
            