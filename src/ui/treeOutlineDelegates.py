#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from __future__ import print_function
from __future__ import unicode_literals

from qt import *
from enums import *

class treeOutlinePersoDelegate(QStyledItemDelegate):
    
    def __init__(self, mdlPersos, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.mdlPersos = mdlPersos
        
    def sizeHint(self, option, index):
        s = QStyledItemDelegate.sizeHint(self, option, index)
        return s + QSize(18, 0)
    
    def createEditor(self, parent, option, index):
        item = index.internalPointer()
        if item.isFolder():
            return
        
        editor = QComboBox(parent)
        editor.setAutoFillBackground(True)
        editor.setFrame(False)
        return editor
    
    def setEditorData(self, editor, index):
        for i in range(self.mdlPersos.rowCount()):
            editor.addItem(self.mdlPersos.item(i, Perso.name.value).text(), self.mdlPersos.item(i, Perso.ID.value).text())
        editor.setCurrentIndex(editor.findData(index.data()))
    
    def setModelData(self, editor, model, index):
        val = editor.currentData()
        model.setData(index, val)
    
    def displayText(self, value, locale):
        
        for i in range(self.mdlPersos.rowCount()):
            if self.mdlPersos.item(i, Perso.ID.value).text() == value:
                return self.mdlPersos.item(i, Perso.name.value).text()
        return ""
    
class treeOutlineCompileDelegate(QStyledItemDelegate):
    
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        
    #def displayText(self, value, locale):
        #return ""
    
class treeOutlineStatusDelegate(QStyledItemDelegate):
    
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        
    def sizeHint(self, option, index):
        s = QStyledItemDelegate.sizeHint(self, option, index)
        return s + QSize(18, 0)
    
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.setAutoFillBackground(True)
        editor.setEditable(True)
        editor.setFrame(False)
        return editor
    
    def setEditorData(self, editor, index):
        statuses = index.model().statuses
        editor.addItem("")
        for status in statuses:
            editor.addItem(status)
        editor.setCurrentIndex(editor.findText(index.data()))
    
    def setModelData(self, editor, model, index):
        val = editor.currentText()
        model.setData(index, val)