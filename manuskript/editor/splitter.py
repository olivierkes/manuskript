#!/usr/bin/env python
# --!-- coding: utf8 --!--

import icu
import re


class TextSplitTuple:

    def __init__(self, begin: int, end: int):
        self.begin: int = begin
        self.end: int = end


class TextSplitResult:

    def __init__(self, text: str):
        self.text: str = text
        self.tuples: list[TextSplitTuple] = []


class TextSplitter:

    def __init__(self, expression: str = "(\\w|(['’]\\w))+"):
        self.reg = re.compile(expression)

    def split(self, text: str) -> TextSplitResult:
        result = TextSplitResult(text)
        result.tuples = [ TextSplitTuple(match.span()[0], match.span()[1]) for match in self.reg.finditer(result.text) ]
        return result


#TODO: ICU is generally faster than Regex but it requires pyicu to be installed!
class ICUSplitter(TextSplitter):

    def __init__(self):
        self.breaker = icu.BreakIterator.createWordInstance(icu.Locale.getRoot())

    def split(self, text: str) -> TextSplitResult:
        result = TextSplitResult(text)

        self.breaker.setText(text)
        start = self.breaker.first()
        for end in self.breaker:
            if self.breaker.getRuleStatus() > 0:
                result.tuples.append(TextSplitTuple(start, end))
            start = end

        return result
