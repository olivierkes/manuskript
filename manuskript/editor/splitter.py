#!/usr/bin/env python
# --!-- coding: utf8 --!--

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

