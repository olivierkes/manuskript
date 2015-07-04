#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from ui.views.metadataView_ui import *

class metadataView(QWidget, Ui_metadataView):
    
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.setupUi(self)
        self._lastIndexes = None
        self.txtSummarySentance.setColumn(Outline.summarySentance.value)
        self.txtSummaryFull.setColumn(Outline.summaryFull.value)
        self.txtNotes.setColumn(Outline.notes.value)
        self.revisions.setEnabled(False)
        
    def setModels(self, mdlOutline, mdlPersos, mdlLabels, mdlStatus):
        self.properties.setModels(mdlOutline, mdlPersos, mdlLabels, mdlStatus)
        self.txtSummarySentance.setModel(mdlOutline)
        self.txtSummaryFull.setModel(mdlOutline)
        self.txtNotes.setModel(mdlOutline)
        self.revisions.setModel(mdlOutline)
        
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
        
        if self._lastIndexes == indexes:
            return
        
        if len(indexes) == 0:
            self.setEnabled(False)
            self.revisions.setEnabled(False)
        
        elif len(indexes) == 1:
            self.setEnabled(True)
            idx = indexes[0]
            self.txtSummarySentance.setCurrentModelIndex(idx)
            self.txtSummaryFull.setCurrentModelIndex(idx)
            self.txtNotes.setCurrentModelIndex(idx)
            self.revisions.setEnabled(True)
            self.revisions.setCurrentModelIndex(idx)
            
        else:
            self.setEnabled(True)
            self.txtSummarySentance.setCurrentModelIndexes(indexes)
            self.txtSummaryFull.setCurrentModelIndexes(indexes)
            self.txtNotes.setCurrentModelIndexes(indexes)
            self.revisions.setEnabled(False)
            
        self.properties.selectionChanged(sourceView)
        self._lastIndexes = indexes
        
    def setDict(self, d):
        self.txtNotes.setDict(d)
        self.txtSummaryFull.setDict(d)
        
    def toggleSpellcheck(self, v):
        self.txtNotes.toggleSpellcheck(v)
        self.txtSummaryFull.toggleSpellcheck(v)
        
    def saveState(self):
        return [
            self.grpProperties.saveState(),
            self.grpSummary.saveState(),
            self.grpNotes.saveState(),
            self.grpRevisions.saveState(),
            ]
    
    def restoreState(self, state):
        self.grpProperties.restoreState(state[0]),
        self.grpSummary.restoreState(state[1]),
        self.grpNotes.restoreState(state[2]),
        self.grpRevisions.restoreState(state[3]),
        