#!/usr/bin/python
# -*- coding: utf8 -*-
from manuskript.ui.editors.basicHighlighter import basicHighlighter


class MMDHighlighter(basicHighlighter):

    def __init__(self, editor, style="Default"):
        basicHighlighter.__init__(self, editor)

    def highlightBlock(self, text):
        basicHighlighter.highlightBlockBefore(self, text)

        # FIXME

        basicHighlighter.highlightBlockAfter(self, text)
