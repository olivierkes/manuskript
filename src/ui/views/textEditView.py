#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from ui.editors.t2tHighlighter import *
from ui.editors.basicHighlighter import *
from ui.editors.textFormat import *
from models.outlineModel import *
from functions import *

try:
    import enchant
except ImportError:
    enchant = None
    
class textEditView(QTextEdit):
    
    def __init__(self, parent=None, index=None, html=None, spellcheck=True, highlighting=False, dict="", autoResize=False):
        QTextEdit.__init__(self, parent)
        
        self._column = Outline.text.value
        self._index = None
        self._indexes = None
        self._placeholderText = None
        self._updating = False
        self._item = None
        self._highlighting = highlighting
        self._textFormat = "text"
        self.setAcceptRichText(False)
        
        self.spellcheck = spellcheck
        self.currentDict = dict
        self.highlighter = None
        self._autoResize = autoResize
        self._defaultBlockFormat = QTextBlockFormat()
        self.highlightWord = ""
        self.highligtCS = False
        self.defaultFontPointSize = qApp.font().pointSize()
        self._dict = None
        #self.document().contentsChanged.connect(self.submit, AUC)
        
        
        # Submit text changed only after 500ms without modifications
        self.updateTimer = QTimer()
        self.updateTimer.setInterval(500)
        self.updateTimer.setSingleShot(True)
        self.updateTimer.timeout.connect(self.submit)
        self.updateTimer.stop()
        self.document().contentsChanged.connect(self.updateTimer.start, AUC)
        #self.document().contentsChanged.connect(lambda: print(self.objectName(), "Contents changed"))
        
        if index:
            self.setCurrentModelIndex(index)
            
        elif html:
            self.document().setHtml(html)
            self.setReadOnly(True)
            
        self.setAutoResize(self._autoResize)
                    
        # Spellchecking
        if enchant and self.spellcheck:
            self._dict = enchant.Dict(self.currentDict if self.currentDict else enchant.get_default_language())
        else:
            self.spellcheck = False
            
        if self._highlighting and not self.highlighter:
            self.highlighter = t2tHighlighter(self)
            self.highlighter.setDefaultBlockFormat(self._defaultBlockFormat)
            
    def setModel(self, model):
        self._model = model
        self._model.dataChanged.connect(self.update, AUC)
        
    def setColumn(self, col):
        self._column = col
        
    def setHighlighting(self, val):
        self._highlighting = val
            
    def setDefaultBlockFormat(self, bf):
        self._defaultBlockFormat = bf
        if self.highlighter:
            self.highlighter.setDefaultBlockFormat(bf)
            
    def setCurrentModelIndex(self, index):
        self._indexes = None
        if index.isValid():
            if index.column() != self._column:
                index = index.sibling(index.row(), self._column)
            self._index = index
            if self._placeholderText != None:
                self.setPlaceholderText(self._placeholderText)
                
            self._model = index.model()
            try:
                self._model.dataChanged.connect(self.update, AUC)
            except TypeError:
                pass
            
            self.setupEditorForIndex(self._index)
            #self.document().contentsChanged.connect(self.submit, AUC)
            self.updateText()
            
            
        else:
            self._index = QModelIndex()
            try:
                self.document().contentsChanged.disconnect(self.submit)
                #self._model.dataChanged.disconnect(self.update)
            except:
                pass

            self.setPlainText("")
        
    def setupEditorForIndex(self, index):
        
        # what type of text are we editing?
        if type(index.model()) != outlineModel:
            self._textFormat = "text"
            return
        
        if self._column != Outline.text.value:
            self._textFormat = "text"
            return
        
        item = index.internalPointer()
        if item.isHTML():
            self._textFormat = "html"
        elif item.isT2T():
            self._textFormat = "t2t"
        else:
            self._textFormat = "text"
        
        # Setting highlighter
        if self._highlighting:
            item = index.internalPointer()
            if self._column == Outline.text.value and not item.isT2T():
                self.highlighter = basicHighlighter(self)
            else:
                self.highlighter = t2tHighlighter(self)
            
            self.highlighter.setDefaultBlockFormat(self._defaultBlockFormat)
        
            # Accept richtext maybe
            if self._textFormat == "html":
                self.setAcceptRichText(True)
            else:
                self.setAcceptRichText
        
    def setCurrentModelIndexes(self, indexes):
        self._index = None
        self._indexes = []
        
        for i in indexes:
            if i.isValid():
                if i.column() != self._column:
                    i = i.sibling(i.row(), self._column)
                self._indexes.append(i)
                
        #self.document().contentsChanged.connect(self.submit)
        self.updateText()
        
    def update(self, topLeft, bottomRight):
        if self._updating:
            return
        
        elif self._index:
            if topLeft.row() <= self._index.row() <= bottomRight.row():
                if topLeft.column() <= Outline.type.value <= bottomRight.column():
                    # If item type change, we reset the index to set the proper
                    # highlighter and other defaults
                    self.setupEditorForIndex(self._index)
                    self.updateText()
                    
                elif topLeft.column() <= self._column <= bottomRight.column():
                    self.updateText()
                
        elif self._indexes:
            update = False
            for i in self._indexes:
                if topLeft.row() <= i.row() <= bottomRight.row():
                    update = True
            if update:
                self.updateText()
            
    def disconnectDocument(self):
        try:
            self.document().contentsChanged.disconnect(self.updateTimer.start)
        except:
            pass
        
    def reconnectDocument(self):
        self.document().contentsChanged.connect(self.updateTimer.start, AUC)
            
    def updateText(self):
        
        if self._updating:
            return
        
        self._updating = True
        if self._index:
            self.disconnectDocument()
            if self._textFormat == "html":
                if self.toHtml() != toString(self._model.data(self._index)):
                    self.document().setHtml(toString(self._model.data(self._index)))
            else:
                if self.toPlainText() != toString(self._model.data(self._index)):
                    self.document().setPlainText(toString(self._model.data(self._index)))
            self.reconnectDocument()
            
        elif self._indexes:
            t = []
            same = True
            for i in self._indexes:
                item = i.internalPointer()
                t.append(toString(item.data(self._column)))
                
            for t2 in t[1:]:
                if t2 != t[0]:
                    same = False
                    break
            
            if same:
                # Assuming that we don't use HTML with multiple items
                self.document().setPlainText(t[0])
            else:
                self.document().setPlainText("")
                
                if not self._placeholderText:
                    self._placeholderText = self.placeholderText()
                    
                self.setPlaceholderText(self.tr("Various"))
        self._updating = False
        
    def submit(self):
        if self._updating:
            return
        
        if self._index:
            item = self._index.internalPointer()
            if self._textFormat == "html":
                if self.toHtml() != self._model.data(self._index):
                    self._updating = True
                    self._model.setData(self._index, self.toHtml())
                    self._updating = False
            else:
                if self.toPlainText() != self._model.data(self._index):
                    self._updating = True
                    self._model.setData(self._index, self.toPlainText())
                    self._updating = False
                
        elif self._indexes:
            self._updating = True
            for i in self._indexes:
                item = i.internalPointer()
                if self.toPlainText() != toString(item.data(self._column)):
                    self._model.setData(i, self.toPlainText())
            self._updating = False
            
    # -----------------------------------------------------------------------------------------------------
    # Resize stuff
    
    def resizeEvent(self, e):
        QTextEdit.resizeEvent(self, e)
        if self._autoResize:
            self.sizeChange()

    def sizeChange(self):
        docHeight = self.document().size().height()
        if self.heightMin <= docHeight <= self.heightMax:
            self.setMinimumHeight(docHeight)
            
    def setAutoResize(self, val):
        self._autoResize = val
        if self._autoResize:
            self.document().contentsChanged.connect(self.sizeChange)
            self.heightMin = 0
            self.heightMax = 65000
            self.sizeChange()
            
###############################################################################
# SPELLCHECKING
###############################################################################
# Based on http://john.nachtimwald.com/2009/08/22/qplaintextedit-with-in-line-spell-check/

    def setDict(self, d):
        self.currentDict = d
        self._dict = enchant.Dict(d)
        if self.highlighter:
            self.highlighter.rehighlight()
        
    def toggleSpellcheck(self, v):
        self.spellcheck = v
        if enchant and self.spellcheck and not self._dict:
            self._dict = enchant.Dict(self.currentDict if self.currentDict else enchant.get_default_language())
        if self.highlighter:
            self.highlighter.rehighlight()
        else:
            self.spellcheck = False

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            # Rewrite the mouse event to a left button event so the cursor is
            # moved to the location of the pointer.
            event = QMouseEvent(QEvent.MouseButtonPress, event.pos(),
                Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        QTextEdit.mousePressEvent(self, event)
        
    class SpellAction(QAction):
        "A special QAction that returns the text in a signal. Used for spellckech."
    
        correct = pyqtSignal(str)
    
        def __init__(self, *args):
            QAction.__init__(self, *args)
    
            self.triggered.connect(lambda x: self.correct.emit(
                str(self.text())))

    def contextMenuEvent(self, event):
        # Based on http://john.nachtimwald.com/2009/08/22/qplaintextedit-with-in-line-spell-check/

        if not self.spellcheck:
            QTextEdit.contextMenuEvent(self, event)
            return

        popup_menu = self.createStandardContextMenu()
 
        # Select the word under the cursor.
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        self.setTextCursor(cursor)
 
        # Check if the selected word is misspelled and offer spelling
        # suggestions if it is.
        if self.textCursor().hasSelection():
            text = str(self.textCursor().selectedText())
            if not self._dict.check(text):
                spell_menu = QMenu(self.tr('Spelling Suggestions'))
                for word in self._dict.suggest(text):
                    action = self.SpellAction(word, spell_menu)
                    action.correct.connect(self.correctWord)
                    spell_menu.addAction(action)
                # Only add the spelling suggests to the menu if there are
                # suggestions.
                if len(spell_menu.actions()) != 0:
                    popup_menu.insertSeparator(popup_menu.actions()[0])
                    popup_menu.insertMenu(popup_menu.actions()[0], spell_menu)
 
        popup_menu.exec_(event.globalPos())
    
    def correctWord(self, word):
        '''
        Replaces the selected text with word.
        '''
        cursor = self.textCursor()
        cursor.beginEditBlock()
 
        cursor.removeSelectedText()
        cursor.insertText(word)
 
        cursor.endEditBlock()
        
###############################################################################
# FORMATTING
###############################################################################
    
    def focusInEvent(self, event):
        "Finds textFormatter and attach them to that view."
        QTextEdit.focusInEvent(self, event)
        
        p = self.parent()
        while p.parent():
            p = p.parent()
        
        if self._index:
            for tF in p.findChildren(textFormat, QRegExp(".*"), Qt.FindChildrenRecursively):
                tF.updateFromIndex(self._index)
                tF.setTextEdit(self)
                
    def applyFormat(self, _format):
        print(_format)