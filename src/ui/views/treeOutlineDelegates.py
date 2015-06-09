#!/usr/bin/env python
#--!-- coding: utf8 --!--

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
        #if item.isFolder():  # No POV for folders
            #return
        
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
        editor.showPopup()
    
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
    def __init__(self, rootIndex=None, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.rootIndex = rootIndex
        
    def sizeHint(self, option, index):
        sh = QStyledItemDelegate.sizeHint(self, option, index)
        #if sh.width() > 50:
        sh.setWidth(100)
        return sh
        
    def paint(self, painter, option, index):
        if not index.isValid():
            return QStyledItemDelegate.paint(self, painter, option, index)
        
        QStyledItemDelegate.paint(self, painter, option, index)
        
        item = index.internalPointer()
        
        if not item.data(Outline.goal.value):
            return
        
        p = toFloat(item.data(Outline.goalPercentage.value))

        typ = item.data(Outline.type.value)
        
        level = item.level()
        if self.rootIndex:
            level -= self.rootIndex.internalPointer().level() + 1
        
        margin = 5
        height = max(min(option.rect.height() - 2*margin, 12) - 2 * level, 6)
        
        painter.save()
        
        rect = option.rect.adjusted(margin, margin, -margin, -margin)
        
        # Move
        rect.translate(level * rect.width() / 10, 0)
        rect.setWidth(rect.width() - level * rect.width() / 10)
        
        rect.setHeight(height)
        rect.setTop(option.rect.top() + (option.rect.height() - height) / 2)
        
        drawProgress(painter, rect, p) # from functions
        
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
        editor.showPopup()
    
    def setModelData(self, editor, model, index):
        val = editor.currentText()
        model.setData(index, val)
        
        
class treeOutlineLabelDelegate(QStyledItemDelegate):
    
    def __init__(self, mdlLabels, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.mdlLabels = mdlLabels
        
    #def sizeHint(self, option, index):
        #s = QStyledItemDelegate.sizeHint(self, option, index)
        #if s.width() > 200:
            #s.setWidth(200)
        #elif s.width() < 100:
            #s.setWidth(100)
        #return s + QSize(18, 0)
    
    def createEditor(self, parent, option, index):
        item = index.internalPointer()
        editor = QComboBox(parent)
        editor.setAutoFillBackground(True)
        editor.setFrame(False)
        return editor
    
    def setEditorData(self, editor, index):
        for i in range(self.mdlLabels.rowCount()):
            editor.addItem(self.mdlLabels.item(i, 0).icon(),
                           self.mdlLabels.item(i, 0).text())
            
        val = index.internalPointer().data(Outline.label.value)
        if not val: val = 0
        editor.setCurrentIndex(int(val))
        editor.showPopup()
    
    def setModelData(self, editor, model, index):
        val = editor.currentIndex()
        model.setData(index, val)
        
    def paint(self, painter, option, index):
        if not index.isValid():
            return QStyledItemDelegate.paint(self, painter, option, index)
        else:
            item = index.internalPointer()
        
        d = item.data(index.column(), Qt.DisplayRole)
        if not d: 
            d = 0
        
        lbl = self.mdlLabels.item(int(d), 0)
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, self.mdlLabels.indexFromItem(lbl))
        
        qApp.style().drawControl(QStyle.CE_ItemViewItem, opt, painter)
        