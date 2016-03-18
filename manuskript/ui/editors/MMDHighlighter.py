#!/usr/bin/python
# -*- coding: utf8 -*-
import re

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCharFormat, QFont, QTextCursor, QFontMetrics

from manuskript.ui.editors.basicHighlighter import basicHighlighter


class MMDHighlighter(basicHighlighter):

    MARKDOWN_REGEX = {
        'Bold':             '(\*\*)(.+?)(\*\*)',
        'Bold2':            '(__)(.+?)(__)',
        'Italic':           '(\*)([^\*].+?[^\*])(\*)',
        'Italic2':          '(_)([^_].+?[^_])(_)',
        'Title':            '^(#+)(\s*)(.*)(#*)',
        'HTML':             '<.+?>',
    }

    def __init__(self, editor, style="Default"):
        basicHighlighter.__init__(self, editor)

        self.editor = editor

    def highlightBlock(self, text):
        basicHighlighter.highlightBlockBefore(self, text)

        self.doHighlightBlock(text)

        basicHighlighter.highlightBlockAfter(self, text)

    def doHighlightBlock(self, text):

        fop = QTextCharFormat()
        fop.setForeground(Qt.lightGray)
        fb = QTextCharFormat()
        fb.setFontWeight(QFont.Bold)
        fi = QTextCharFormat()
        fi.setFontItalic(True)

        for name, style in [
            ("Italic", fi),
            ("Italic2", fi),
            ("Bold", fb),
            ("Bold2", fb),
        ]:
            r = re.compile(self.MARKDOWN_REGEX[name])

            for m in r.finditer(text):
                self.setFormat(m.start(1), len(m.group(1)), fop)
                self.setFormat(m.start(2), len(m.group(2)), style)
                self.setFormat(m.start(3), len(m.group(3)), fop)

        fps = self._defaultCharFormat.font().pointSize()

        r = re.compile(self.MARKDOWN_REGEX["Title"])
        for m in r.finditer(text):
            fop.setFontPointSize(fps + 12 - 2 * len(m.group(1)))
            fb.setFontPointSize(fps + 12 - 2 * len(m.group(1)))

            self.setFormat(m.start(1), len(m.group(1)), fop)
            self.setFormat(m.start(3), len(m.group(3)), fb)
            self.setFormat(m.start(4), len(m.group(4)), fop)