#!/usr/bin/python
# -*- coding: utf8 -*-

import re

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QTextCursor, QColor, QFont, QSyntaxHighlighter, QTextBlockFormat, QTextCharFormat

import manuskript.models.references as Ref


class basicHighlighter(QSyntaxHighlighter):
    def __init__(self, editor):
        QSyntaxHighlighter.__init__(self, editor.document())

        self.editor = editor
        self._misspelledColor = Qt.red
        self._defaultBlockFormat = QTextBlockFormat()
        self._defaultCharFormat = QTextCharFormat()

    def setDefaultBlockFormat(self, bf):
        self._defaultBlockFormat = bf
        self.rehighlight()

    def setDefaultCharFormat(self, cf):
        self._defaultCharFormat = cf
        self.rehighlight()

    def setMisspelledColor(self, color):
        self._misspelledColor = color

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        self.highlightBlockBefore(text)
        self.highlightBlockAfter(text)

    def highlightBlockBefore(self, text):
        """Highlighting to do before anything else.
        
        When subclassing basicHighlighter, you must call highlightBlockBefore
        before you do any custom highlighting.
        """

        #print(">", self.currentBlock().document().availableUndoSteps())
        c = QTextCursor(self.currentBlock())
        #c.joinPreviousEditBlock()
        bf = QTextBlockFormat(self._defaultBlockFormat)
        bf.setAlignment(c.blockFormat().alignment())
        if bf != c.blockFormat():
            c.setBlockFormat(bf)
        #c.endEditBlock()
        #print(" ", self.currentBlock().document().availableUndoSteps())

        # self.setFormat(0, len(text), self._defaultCharFormat)

    def highlightBlockAfter(self, text):
        """Highlighting to do after everything else.
        
        When subclassing basicHighlighter, you must call highlightBlockAfter
        after your custom highlighting.
        """

        # References
        for txt in re.finditer(Ref.RegEx, text):
            fmt = self.format(txt.start())
            fmt.setFontFixedPitch(True)
            fmt.setFontWeight(QFont.DemiBold)
            fmt.setForeground(Qt.black)  # or text becomes unreadable in some color scheme
            if txt.group(1) == Ref.TextLetter:
                fmt.setBackground(QBrush(QColor(Qt.blue).lighter(190)))
            elif txt.group(1) == Ref.CharacterLetter:
                fmt.setBackground(QBrush(QColor(Qt.yellow).lighter(170)))
            elif txt.group(1) == Ref.PlotLetter:
                fmt.setBackground(QBrush(QColor(Qt.red).lighter(170)))
            elif txt.group(1) == Ref.WorldLetter:
                fmt.setBackground(QBrush(QColor(Qt.green).lighter(170)))

            self.setFormat(txt.start(),
                           txt.end() - txt.start(),
                           fmt)

        # Spell checking
        # Based on http://john.nachtimwald.com/2009/08/22/qplaintextedit-with-in-line-spell-check/
        WORDS = '(?iu)[\w\']+'
        if hasattr(self.editor, "spellcheck") and self.editor.spellcheck:
            for word_object in re.finditer(WORDS, text):
                if self.editor._dict and not self.editor._dict.check(word_object.group()):
                    format = self.format(word_object.start())
                    format.setUnderlineColor(self._misspelledColor)
                    # SpellCheckUnderline fails with some fonts
                    format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
                    self.setFormat(word_object.start(),
                                   word_object.end() - word_object.start(), format)
