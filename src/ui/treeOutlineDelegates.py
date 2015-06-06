#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from __future__ import print_function
from __future__ import unicode_literals

from qt import *
from enums import *
from functions import *

class treeOutlinePersoDelegate(QStyledItemDelegate):
    
    def __init__(self, mdlPersos, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.mdlPersos = mdlPersos
        
    def sizeHint(self, option, index):
        s = QStyledItemDelegate.sizeHint(self, option, index)
        if s.width() > 200:
            s.setWidth(200)
        elif s.width() < 100:
            s.setWidth(100)
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
        editor.addItem("")
        for i in range(self.mdlPersos.rowCount()):
            editor.addItem(self.mdlPersos.item(i, Perso.name.value).text(), self.mdlPersos.item(i, Perso.ID.value).text())
            editor.setItemData(i+1, self.mdlPersos.item(i, Perso.name.value).text(), Qt.ToolTipRole)
            
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
        
    def displayText(self, value, locale):
        return ""
    
class treeOutlineGoalPercentageDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        
    def paint(self, painter, option, index):
        if not index.isValid():
            return QStyledItemDelegate.paint(self, painter, option, index)
        
        QStyledItemDelegate.paint(self, painter, option, index)
        
        item = index.internalPointer()
        
        if not item.data(Outline.goal.value):
            return
        
        p = toFloat(item.data(Outline.goalPercentage.value))
        if p > 1: p = 1.

        typ = item.data(Outline.type.value)
        
        level = item.level()
        
        margin = 5
        height = max(min(option.rect.height() - 2*margin, 12) - 2 * level, 6)
        
        painter.save()
        
        rect = option.rect.adjusted(margin, margin, -margin, -margin)
        
        # Move
        rect.translate(level * rect.width() / 10, 0)
        rect.setWidth(rect.width() - level * rect.width() / 10)
        
        rect.setHeight(height)
        rect.setTop(option.rect.top() + (option.rect.height() - height) / 2)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#dddddd"))
        painter.drawRect(rect)
        
        c1 = QColor(Qt.red)
        c2 = QColor(Qt.blue)
        c3 = QColor(Qt.darkGreen)
        if p < 0.3:
            painter.setBrush(QBrush(c1))
        elif p < 0.8:
            painter.setBrush(QBrush(c2))
        else:
            painter.setBrush(QBrush(c3))
        
        #if typ == "folder":
            #painter.setBrush(QBrush(Qt.blue))
        #else:
            #painter.setBrush(QBrush(Qt.green))
            
        r2 = QRect(rect)
        r2.setWidth(r2.width() * p)
        painter.drawRect(r2)
        painter.restore()
        
    def displayText(self, value, locale):
        return ""
    
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