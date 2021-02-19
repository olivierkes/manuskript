#!/usr/bin/python
# -*- coding: utf8 -*-
import re

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCharFormat, QFont, QTextCursor, QFontMetrics

from manuskript.ui.highlighters import BasicHighlighter


class MMDHighlighter(BasicHighlighter):

    MARKDOWN_REGEX = {
        'Bold':             r'(\*\*)(.+?)(\*\*)',
        'Bold2':            '(__)(.+?)(__)',
        'Italic':           r'(\*)([^\*].+?[^\*])(\*)',
        'Italic2':          '(_)([^_].+?[^_])(_)',
        'Title':            r'^(#+)(\s*)(.*)(#*)',
        'HTML':             '<.+?>',
        'Blockquotes':      '^(> )+.*$',
        'OrderedList':      r'^\d+\.\s+',
        'UnorderedList':    r'^[\*\+-]\s+',
        'Code':             r'^\s{4,}.*$',
        'Links-inline':     r'(\[)(.*?)(\])(\()(.*?)(\))',
        'Links-ref':        r'(\[)(.*?)(\])\s?(\[)(.*?)(\])',
        'Links-ref2':       r'^\s{,3}(\[)(.*?)(\]:)\s+([^\s]*)\s*(.*?)*$',
    }

    def __init__(self, editor, style="Default"):
        BasicHighlighter.__init__(self, editor)

        self.editor = editor

        self.rules = {}
        for key in self.MARKDOWN_REGEX:
            self.rules[key] = re.compile(self.MARKDOWN_REGEX[key])

    def doHighlightBlock(self, text):
        """
        A quick-n-dirty very basic highlighter, that fails in most non-trivial cases. And is ugly.
        """

        # Creates textCharFormat
        cfOperator = QTextCharFormat()
        cfOperator.setForeground(Qt.lightGray)
        cfBold = QTextCharFormat()
        cfBold.setFontWeight(QFont.Bold)
        cfItalic = QTextCharFormat()
        cfItalic.setFontItalic(True)

        # Titles (only atx-style, with #, not underlined)
        defaultSize = self._defaultCharFormat.font().pointSize()
        r = self.rules["Title"]
        for m in r.finditer(text):
            cfOperator.setFontPointSize(defaultSize + 12 - 2 * len(m.group(1)))
            cfBold.setFontPointSize(defaultSize + 12 - 2 * len(m.group(1)))

            self.setFormat(m.start(1), len(m.group(1)), cfOperator)
            self.setFormat(m.start(3), len(m.group(3)), cfBold)
            self.setFormat(m.start(4), len(m.group(4)), cfOperator)

        # Code blocks
        r = self.rules["Code"]
        format = QTextCharFormat()
        format.setForeground(Qt.darkGray)
        format.setFontFixedPitch(True)
        for m in r.finditer(text):
            self.setFormat(m.start(), m.end() - m.start(), format)

        # Basic stuff
        stuff = [
            ("Blockquotes", Qt.blue),
            ("OrderedList", Qt.red),
            ("UnorderedList", Qt.darkRed),
            ("HTML", Qt.darkGreen),
        ]
        for name, color in stuff:
            r = self.rules[name]
            format = QTextCharFormat()
            format.setForeground(color)
            for m in r.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), format)

        # Bold and Italic
        for name, style in [
            ("Italic", cfItalic),
            ("Italic2", cfItalic),
            ("Bold", cfBold),
            ("Bold2", cfBold),
        ]:
            r = self.rules[name]

            for m in r.finditer(text):
                self.setFormat(m.start(1), len(m.group(1)), cfOperator)
                self.setFormat(m.start(2), len(m.group(2)), style)
                self.setFormat(m.start(3), len(m.group(3)), cfOperator)

        # Links
        cfURL = QTextCharFormat()
        cfURL.setForeground(Qt.darkGreen)
        cfURL.setFontItalic(True)
        cfText = QTextCharFormat()
        cfText.setForeground(Qt.darkBlue)
        cfIdentifier = QTextCharFormat()
        cfIdentifier.setForeground(Qt.darkMagenta)

        for type in ['Links-inline', 'Links-ref']:
            r = self.rules[type]
            for m in r.finditer(text):
                self.setFormat(m.start(1), len(m.group(1)), cfOperator)
                self.setFormat(m.start(2), len(m.group(2)), cfText)
                self.setFormat(m.start(3), len(m.group(3)), cfOperator)
                self.setFormat(m.start(4), len(m.group(4)), cfOperator)
                self.setFormat(m.start(5), len(m.group(5)), cfURL if "inline" in type else cfIdentifier)
                self.setFormat(m.start(6), len(m.group(6)), cfOperator)

        r = self.rules["Links-ref2"]
        for m in r.finditer(text):
            self.setFormat(m.start(1), len(m.group(1)), cfOperator)
            self.setFormat(m.start(2), len(m.group(2)), cfIdentifier)
            self.setFormat(m.start(3), len(m.group(3)), cfOperator)
            self.setFormat(m.start(4), len(m.group(4)), cfURL)
            self.setFormat(m.start(5), len(m.group(5)), cfText)
