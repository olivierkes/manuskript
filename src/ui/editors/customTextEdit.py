#!/usr/bin/env python
#--!-- coding: utf8 --!--
 



from qt import *
from enums import *
from ui.editors.t2tHighlighter import *
try:
    import enchant
except ImportError:
    enchant = None
    
class customTextEdit(QTextEdit):
    
    def __init__(self, parent=None, index=None, html=None, spellcheck=True, dict="", autoResize=False):
        QTextEdit.__init__(self, parent)
        
        self.currentIndex = None
        self.item = None
        self.spellcheck = spellcheck
        self.currentDict = dict
        
        if index:
            self.setCurrentModelIndex(index)
            
        elif html:
            self.document().setHtml(html)
            self.setReadOnly(True)
        
        self.autoResize = autoResize
        if autoResize:
            self.document().contentsChanged.connect(self.sizeChange)
            self.heightMin = 0
            self.heightMax = 65000
            self.sizeChange()
            
    def setCurrentModelIndex(self, index):
        if index.isValid():
            self.currentIndex = index
            self.item = index.internalPointer()
            self._model = index.model()
            self.document().contentsChanged.connect(self.submit)
            self._model.dataChanged.connect(self.update)
            self.updateText()
            
            self.defaultFontPointSize = qApp.font().pointSize()
            self.highlightWord = ""
            self.highligtCS = False
            
            self.highlighter = t2tHighlighter(self)
                
            # Spellchecking
            if enchant and self.spellcheck:
                self.dict = enchant.Dict(self.currentDict if self.currentDict else enchant.get_default_language())
            else:
                self.spellcheck = False
        
    def submit(self):
        if self.toPlainText() != self.item.data(Outline.text.value):
            #self._model.setData(self.item.index(), self.toPlainText(), Outline.text.value)
            self.item.setData(Outline.text.value, self.toPlainText())
        
    def update(self, topLeft, bottomRight):
        if topLeft.row() <= self.currentIndex.row() <= bottomRight.row():
            self.updateText()
            
    def updateText(self):
        if self.item:
            if self.toPlainText() != self.item.data(Outline.text.value):
                self.document().setPlainText(self.item.data(Outline.text.value))
        
    def resizeEvent(self, e):
        QTextEdit.resizeEvent(self, e)
        if self.autoResize:
            self.sizeChange()

    def sizeChange(self):
        docHeight = self.document().size().height()
        if self.heightMin <= docHeight <= self.heightMax:
            self.setMinimumHeight(docHeight)
            
            
    # -----------------------------------------------------------------------------------------------------
    # Spellchecking based on http://john.nachtimwald.com/2009/08/22/qplaintextedit-with-in-line-spell-check/

    def setDict(self, d):
        self.dict = enchant.Dict(d)
        self.highlighter.rehighlight()
        
    def toggleSpellcheck(self, v):
        self.spellcheck = v
        self.highlighter.rehighlight()

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
            if not self.dict.check(text):
                spell_menu = QMenu('Spelling Suggestions')
                for word in self.dict.suggest(text):
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