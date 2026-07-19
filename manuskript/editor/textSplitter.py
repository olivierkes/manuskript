#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.editor.abstractSplitter import AbstractSplitter
from manuskript.editor.splitResult import SplitResult, SplitTuple


class TextSplitter(AbstractSplitter):

    def __init__(self):
        AbstractSplitter.__init__(self)

    def isValid(self) -> bool:
        return True

    def splitText(self, text: str, lang: str|None = None) -> SplitResult:
        result: SplitResult = SplitResult(text)

        begin: int = 0
        end: int = len(text)

        for sub in text.split():
            begin = text.index(sub, begin, end)
            result.tuples.append(SplitTuple(begin, begin + len(sub), lang))
        
        return result
