#!/usr/bin/env python
# --!-- coding: utf8 --!--

try:
    import icu
except ModuleNotFoundError:
    icu = None

from manuskript.editor.abstractSplitter import AbstractSplitter
from manuskript.editor.splitResult import SplitResult, SplitTuple


class ICUSplitter(AbstractSplitter):

    def __init__(self):
        AbstractSplitter.__init__(self)

        self.breaker = None if icu is None else icu.BreakIterator.createWordInstance(icu.Locale.getRoot())

    def isValid(self) -> bool:
        return False if icu is None else True

    def splitText(self, text: str, lang: str|None = None) -> SplitResult:
        result: SplitResult = SplitResult(text)

        self.breaker.setText(text)
        begin = self.breaker.first()
        for end in self.breaker:
            if self.breaker.getRuleStatus() > 0:
                result.tuples.append(SplitTuple(begin, end, lang))
            begin = end

        return result
