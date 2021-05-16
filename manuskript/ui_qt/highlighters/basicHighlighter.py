#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QTextCursor, QColor, QFont, QSyntaxHighlighter
from PyQt5.QtGui import QTextBlockFormat, QTextCharFormat

import manuskript.models.references as Ref
import manuskript.ui_qt.style as S
from manuskript import settings
from manuskript import functions as F

import logging
LOGGER = logging.getLogger(__name__)

class BasicHighlighter(QSyntaxHighlighter):
    def __init__(self, editor):
        QSyntaxHighlighter.__init__(self, editor.document())

        self.editor = editor
        self._defaultBlockFormat = QTextBlockFormat()
        self._defaultCharFormat = QTextCharFormat()
        self.defaultTextColor = QColor(S.text)
        self.backgroundColor = QColor(S.base)
        self.markupColor = QColor(S.textLight)
        self.linkColor = QColor(S.link)
        self.spellingErrorColor = QColor(Qt.red)

        # Matches during checking can be separated by their type (all of them listed here):
        # https://languagetool.org/development/api/org/languagetool/rules/ITSIssueType.html
        #
        # These are the colors for actual spell-, grammar- and style-checking:
        self._errorColors = {
            'addition' : QColor(255, 215, 0),               # gold
            'characters' : QColor(135, 206, 235),           # sky blue
            'duplication' : QColor(0, 255, 255),            # cyan / aqua
            'formatting' : QColor(0, 128, 128),             # teal
            'grammar' : QColor(0, 0, 255),                  # blue
            'inconsistency' : QColor(128, 128, 0),          # olive
            'inconsistententities' : QColor(46, 139, 87),   # sea green
            'internationalization' : QColor(255, 165, 0),   # orange
            'legal' : QColor(255, 69, 0),                   # orange red
            'length' : QColor(47, 79, 79),                  # dark slate gray
            'localespecificcontent' : QColor(188, 143, 143),# rosy brown
            'localeviolation' : QColor(128, 0, 0),          # maroon
            'markup' : QColor(128, 0, 128),                 # purple
            'misspelling' : QColor(255, 0, 0),              # red
            'mistranslation' : QColor(255, 0, 255),         # magenta / fuchsia
            'nonconformance' : QColor(255, 218, 185),       # peach puff
            'numbers' : QColor(65, 105, 225),               # royal blue
            'omission' : QColor(255, 20, 147),              # deep pink
            'other' : QColor(138, 43, 226),                 # blue violet
            'patternproblem' : QColor(0, 128, 0),           # green
            'register' : QColor(112,128,144),               # slate gray
            'style' : QColor(0, 255, 0),                    # lime
            'terminology' : QColor(0, 0, 128),              # navy
            'typographical' : QColor(255, 255, 0),          # yellow
            'uncategorized' : QColor(128, 128, 128),        # gray
            'untranslated' : QColor(210, 105, 30),          # chocolate
            'whitespace' : QColor(192, 192, 192)            # silver
        }

    def setDefaultBlockFormat(self, bf):
        self._defaultBlockFormat = bf
        self.rehighlight()

    def setDefaultCharFormat(self, cf):
        self._defaultCharFormat = cf
        self.rehighlight()

    def setMisspelledColor(self, color):
        self._errorColors['misspelled'] = color

    def updateColorScheme(self, rehighlight=True):
        """
        Generates a base set of colors that will take account of user
        preferences, and use system style.
        """

        # Reading user settings
        opt = settings.textEditor

        if not self.editor._fromTheme or not self.editor._themeData:

            self.defaultTextColor = QColor(opt["fontColor"])
            self.backgroundColor = (QColor(opt["background"])
                                    if not opt["backgroundTransparent"]
                                    else QColor(S.window))
            self.markupColor = F.mixColors(self.defaultTextColor,
                                           self.backgroundColor,
                                           .3)
            self.linkColor = QColor(S.link)
            self.spellingErrorColor = QColor(opt["misspelled"])
            self._defaultCharFormat.setForeground(QBrush(self.defaultTextColor))

        # FullscreenEditor probably
        else:
            opt = self.editor._themeData
            self.defaultTextColor = QColor(opt["Text/Color"])
            self.backgroundColor =  F.mixColors(
                QColor(opt["Foreground/Color"]),
                QColor(opt["Background/Color"]),
                int(opt["Foreground/Opacity"])/100.)
            self.markupColor = F.mixColors(self.defaultTextColor,
                                           self.backgroundColor,
                                           .3)
            self.linkColor = QColor(S.link)
            self.spellingErrorColor = QColor(opt["Text/Misspelled"])

        if rehighlight:
            self.rehighlight()

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        self.highlightBlockBefore(text)
        self.doHighlightBlock(text)
        self.highlightBlockAfter(text)

    def doHighlightBlock(self, text):
        """
        Virtual function to subclass.
        """
        pass

    def highlightBlockBefore(self, text):
        """Highlighting to do before anything else.

        When subclassing BasicHighlighter, you must call highlightBlockBefore
        before you do any custom highlighting. Or implement doHighlightBlock.
        """

        #LOGGER.debug("undoSteps before: %s", self.currentBlock().document().availableUndoSteps())
        c = QTextCursor(self.currentBlock())
        #c.joinPreviousEditBlock()
        bf = QTextBlockFormat(self._defaultBlockFormat)
        if bf != c.blockFormat():
            c.setBlockFormat(bf)
        #c.endEditBlock()
        #LOGGER.debug("undoSteps after: %s", self.currentBlock().document().availableUndoSteps())

        # self.setFormat(0, len(text), self._defaultCharFormat)

    def highlightBlockAfter(self, text):
        """Highlighting to do after everything else.

        When subclassing BasicHighlighter, you must call highlightBlockAfter
        after your custom highlighting. Or implement doHighlightBlock.
        """

        # References
        for txt in re.finditer(Ref.RegEx, text):
            fmt = self.format(txt.start())
            fmt.setFontFixedPitch(True)
            fmt.setFontWeight(QFont.DemiBold)

            if txt.group(1) == Ref.TextLetter:
                fmt.setBackground(QBrush(Ref.TextHighlightColor))
            elif txt.group(1) == Ref.CharacterLetter:
                fmt.setBackground(QBrush(Ref.CharacterHighlightColor))
            elif txt.group(1) == Ref.PlotLetter:
                fmt.setBackground(QBrush(Ref.PlotHighlightColor))
            elif txt.group(1) == Ref.WorldLetter:
                fmt.setBackground(QBrush(Ref.WorldHighlightColor))

            self.setFormat(txt.start(),
                           txt.end() - txt.start(),
                           fmt)

        if hasattr(self.editor, "spellcheck") and self.editor.spellcheck and self.editor._dict:
            # Spell checking

            # Following algorithm would not check words at the end of line.
            # This hacks adds a space to every line where the text cursor is not
            # So that it doesn't spellcheck while typing, but still spellchecks at
            # end of lines. See github's issue #166.
            textedText = text
            if self.currentBlock().position() + len(text) != \
               self.editor.textCursor().position():
                textedText = text + " "

            # The text should only be checked once as a whole
            for match in self.editor._dict.checkText(textedText):
                if match.locqualityissuetype in self._errorColors:
                    highlight_color = self._errorColors[match.locqualityissuetype]

                    format = self.format(match.start)
                    format.setUnderlineColor(highlight_color)
                    # SpellCheckUnderline fails with some fonts
                    format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
                    self.setFormat(match.start, match.end - match.start, format)
