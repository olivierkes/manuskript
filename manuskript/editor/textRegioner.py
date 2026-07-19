#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.editor.abstractRegioner import AbstractRegioner
from manuskript.editor.splitResult import SplitResult, SplitTuple


class TextRegioner(AbstractRegioner):

    def __init__(self):
        AbstractRegioner.__init__(self, [None])
