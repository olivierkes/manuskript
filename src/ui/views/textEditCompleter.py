#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from functions import *
from ui.views.textEditView import *
from ui.editors.completer import *
from models.references import *
import settings
import re

try:
    import enchant
except ImportError:
    enchant = None
    
class textEditCompleter(textEditView):
    
    def __init__(self, parent=None, index=None, html=None, spellcheck=True, highlighting=False, dict="", autoResize=False):
        textEditView.__init__(self, parent=parent, index=index, html=html, spellcheck=spellcheck, highlighting=True, dict=dict, autoResize=autoResize)
        
        self.completer = None
        
    def setCurrentModelIndex(self, index):
        textEditView.setCurrentModelIndex(self, index)
        
        if self._index:
            self.setCompleter(completer())
        
    def setCompleter(self, completer):
        self.completer = completer
        self.completer.activated.connect(self.insertCompletion)
        
    def insertCompletion(self, txt):
        tc = self.textCursor()
        tc.insertText(txt)
        self.setTextCursor(tc)
        
    def textUnderCursor(self, select=False):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        if select:
            self.setTextCursor(tc)
        return tc.selectedText()
        
    def refUnderCursor(self, cursor):
        pos = cursor.position()
        cursor.select(QTextCursor.LineUnderCursor)
        text = cursor.selectedText()
        pos -= cursor.selectionStart()
        match = re.findall(r"::\w:\d+?::", text)
        for m in match:
            if text.find(m) <= pos <= text.find(m) + len(m):
                return m
        
    def event(self, event):
        if event.type() == QEvent.ToolTip:
            cursor = self.cursorForPosition(event.pos())
            ref = self.refUnderCursor(cursor)
            if ref:
                QToolTip.showText(self.mapToGlobal(event.pos()), infoForRef(ref))
            else:
                QToolTip.hideText()
            return True
        return textEditView.event(self, event)
        
    def createStandardContextMenu(self):
        menu = textEditView.createStandardContextMenu(self)
        
        a = QAction(self.tr("Insert reference"), menu)
        a.triggered.connect(self.popupCompleter)
        menu.insertSeparator(menu.actions()[0])
        menu.insertAction(menu.actions()[0], a)
        
        return menu
        
    def keyPressEvent(self, event):
        if self.completer.isVisible():
            if event.key() in (
                    Qt.Key_Enter,
                    Qt.Key_Return,
                    Qt.Key_Escape,
                    Qt.Key_Tab,
                    Qt.Key_Backtab):
                event.ignore()
                return
        
        isShortcut = (event.modifiers() == Qt.ControlModifier and\
                      event.key() == Qt.Key_Space)
        
        if not self.completer or not isShortcut:
            self.completer.setVisible(False)
            textEditView.keyPressEvent(self, event)
            return
        
        self.popupCompleter()
        
    def popupCompleter(self):
        if self.completer:
            cr = self.cursorRect()
            cr.moveTopLeft(self.mapToGlobal(cr.bottomLeft()))
            cr.setWidth(self.completer.sizeHint().width())
            self.completer.setGeometry(cr)
            self.completer.popup(self.textUnderCursor(select=True))
        
        
        
        