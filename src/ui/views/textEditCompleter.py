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
        
    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
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
        
        print(isShortcut)
        
        if not self.completer or not isShortcut:
            self.completer.setVisible(False)
            textEditView.keyPressEvent(self, event)
            return
            
        completionPrefix = self.textUnderCursor()
        
        cr = self.cursorRect()
        cr.moveTopLeft(self.mapToGlobal(cr.bottomLeft()))
        cr.setWidth(self.completer.sizeHint().width())
        self.completer.setGeometry(cr)
        self.completer.popup()
        
    def keyPressEvent_(self, event):
        if self.completer and self.completer.popup() and self.completer.popup().isVisible():
            if event.key() in (
            Qt.Key_Enter,
            Qt.Key_Return,
            Qt.Key_Escape,
            Qt.Key_Tab,
            Qt.Key_Backtab):
                event.ignore()
                return
        ## has ctrl-Space been pressed??
        isShortcut = (event.modifiers() == Qt.ControlModifier and\
                      event.key() == Qt.Key_Space)
        ## modifier to complete suggestion inline ctrl-e
        inline = (event.modifiers() == Qt.ControlModifier and \
                  event.key() == Qt.Key_E)
        ## if inline completion has been chosen
        if inline:
            # set completion mode as inline
            self.completer.setCompletionMode(QCompleter.InlineCompletion)
            completionPrefix = self.textUnderCursor()
            if (completionPrefix != self.completer.completionPrefix()):
                self.completer.setCompletionPrefix(completionPrefix)
            self.completer.complete()
#            self.completer.setCurrentRow(0)
#            self.completer.activated.emit(self.completer.currentCompletion())
            # set the current suggestion in the text box
            self.completer.activated.emit(self.completer.currentCompletion())
            # reset the completion mode
            self.completer.setCompletionMode(QCompleter.PopupCompletion)
            return
        if (not self.completer or not isShortcut):
            pass
            QTextEdit.keyPressEvent(self, event)
        # debug
        print("After controlspace")
        print("isShortcut is: {}".format(isShortcut))
        # debug over
        ## ctrl or shift key on it's own??
        #ctrlOrShift = event.modifiers() in (Qt.ControlModifier ,\
                #Qt.ShiftModifier)
        #if ctrlOrShift and event.text()== '':
##             ctrl or shift key on it's own
            #return
        # debug
        print("After on its own")
        print("isShortcut is: {}".format(isShortcut))
        # debug over
#         eow = QString("~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-=") #end of word
#        eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-=" #end of word
        eow = "~!@#$%^&*+{}|:\"<>?,./;'[]\\-=" #end of word

        #hasModifier = ((event.modifiers() != Qt.NoModifier) and\
                        #not ctrlOrShift)

        completionPrefix = self.textUnderCursor()
#         print('event . text = {}'.format(event.text().right(1)))
#         if (not isShortcut and (hasModifier or event.text()=='' or\
#                                 len(completionPrefix) < 3 or \
#                                 eow.contains(event.text().right(1)))):
        if not isShortcut :
            if self.completer.popup():
                self.completer.popup().hide()
            return
        print("complPref: {}".format(completionPrefix))
        print("completer.complPref: {}".format(self.completer.completionPrefix()))
        print("mode: {}".format(self.completer.completionMode()))
    #        if (completionPrefix != self.completer.completionPrefix()):
        print("Poping up")
        self.completer.setCompletionPrefix(completionPrefix)
        popup = self.completer.popup()
        popup.setCurrentIndex(
            self.completer.completionModel().index(0,0))
        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0)
            + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr) ## popup it up!
        
        