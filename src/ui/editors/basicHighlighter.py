#!/usr/bin/python
# -*- coding: utf8 -*-

from qt import *
import re

class basicHighlighter(QSyntaxHighlighter):

    def __init__(self, editor):
        QSyntaxHighlighter.__init__(self, editor.document())

        self.editor = editor

    def setDefaultBlockFormat(self, bf):
        self._defaultBlockFormat = bf
        self.rehighlight()
    
    def setMisspelledColor(self, color):
        self._misspelledColor = color
    
    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """

        QTextCursor(self.currentBlock()).setBlockFormat(self._defaultBlockFormat)
        
        # Spell checking
        # Based on http://john.nachtimwald.com/2009/08/22/qplaintextedit-with-in-line-spell-check/
        WORDS = '(?iu)[\w\']+'
        if self.editor.spellcheck:
            for word_object in re.finditer(WORDS, text):
                if self.editor._dict and not self.editor._dict.check(word_object.group()):
                    format = self.format(word_object.start())
                    format.setUnderlineColor(self._misspelledColor)
                    format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
                    self.setFormat(word_object.start(),
                        word_object.end() - word_object.start(), format)
