#!/usr/bin/env python
# --!-- coding: utf8 --!--

# from PyQt5.QtCore import
# from PyQt5.QtGui import
# from PyQt5.QtWidgets import

from manuskript.ui.views.textEditView import textEditView
from manuskript.ui.highlighters import MarkdownHighlighter


class MDEditView(textEditView):
    def __init__(self, parent=None, index=None, html=None, spellcheck=True,
                 highlighting=False, dict="", autoResize=False):
        textEditView.__init__(self, parent, index, html, spellcheck,
                              highlighting=True, dict=dict,
                              autoResize=autoResize)

        # Highlighter
        self._textFormat = "md"
        self._highlighterClass = MarkdownHighlighter
