#!/usr/bin/env python
# --!-- coding: utf8 --!--

try:
    import icu
except ModuleNotFoundError:
    icu = None

from manuskript.editor.abstractSplitter import AbstractSplitter
from manuskript.editor.splitResult import SplitResult, SplitTuple


class ICUSplitter(AbstractSplitter):
    def __init__(self) -> None:
        AbstractSplitter.__init__(self)

    def isValid(self) -> bool:
        return icu is not None

    def splitText(self, text: str, lang: str | None = None) -> SplitResult:
        result: SplitResult = SplitResult(text)
        locale = icu.Locale("" if lang is None else lang)

        breaker = icu.BreakIterator.createWordInstance(locale)
        breaker.setText(text)

        begin = breaker.first()
        for end in breaker:
            if breaker.getRuleStatus() > 0:
                result.tuples.append(SplitTuple(begin, end, lang))
            begin = end

        return result
