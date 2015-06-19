#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from ui.editors.t2tHighlighter import *
from functions import *

try:
    import enchant
except ImportError:
    enchant = None
    
class textEditView(QTextEdit):
    
    def __init__(self, parent=None, index=None, html=None, spellcheck=True, dict="", autoResize=False):
        QTextEdit.__init__(self, parent)
        
        self._column = Outline.text.value
        self._index = None
        self._indexes = None
        self._placeholderText = None
        self._updating = False
        self._item = None
        self._highlighting = True
        
        self.spellcheck = spellcheck
        self.currentDict = dict
        self.highlighter = None
        self._autoResize = autoResize
        self._defaultBlockFormat = QTextBlockFormat()
        self.highlightWord = ""
        self.highligtCS = False
        self.defaultFontPointSize = qApp.font().pointSize()
        self._dict = None
        
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
        self._model.dataChanged.connect(self.update)
        
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
            self._item = index.internalPointer()
            if self._placeholderText != None:
                self.setPlaceholderText(self._placeholderText)
                
            self._model = index.model()
            self.document().contentsChanged.connect(self.submit)
            self._model.dataChanged.connect(self.update)
            self.updateText()
            
            if self._highlighting and not self.highlighter:
                self.highlighter = t2tHighlighter(self)
                self.highlighter.setDefaultBlockFormat(self._defaultBlockFormat)
        
    def setCurrentModelIndexes(self, indexes):
        self._index = None
        self._indexes = []
        
        for i in indexes:
            if i.isValid():
                if i.column() != self._column:
                    i = i.sibling(i.row(), self._column)
                self._indexes.append(i)
                
        self.document().contentsChanged.connect(self.submit)
        self.updateText()
        
    def update(self, topLeft, bottomRight):
        if self._updating:
            return
        
        elif self._index:
            if topLeft.row() <= self._index.row() <= bottomRight.row():
                self.updateText()
                
        elif self._indexes:
            update = False
            for i in self._indexes:
                if topLeft.row() <= i.row() <= bottomRight.row():
                    update = True
            if update:
                self.updateText()
            
    def updateText(self):
        self._updating = True
        if self._index:
            if self.toPlainText() != toString(self._model.data(self._index)):
                self.document().setPlainText(toString(self._model.data(self._index)))
                
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
            #item = self._index.internalPointer()
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
            
    # -----------------------------------------------------------------------------------------------------
    # Spellchecking based on http://john.nachtimwald.com/2009/08/22/qplaintextedit-with-in-line-spell-check/

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
        
    # -----------------------------------------------------------------------------------------------------