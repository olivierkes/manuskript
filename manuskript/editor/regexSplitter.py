#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.editor.abstractSplitter import AbstractSplitter
from manuskript.editor.splitResult import SplitResult, SplitTuple

import re


class RegexSplitter(AbstractSplitter):

    def __init__(self, expression: str = "(\\w|(['’]\\w))+"):
        AbstractSplitter.__init__(self)
        
        self.regex = re.compile(expression)

    def isValid(self) -> bool:
        return True

    def splitText(self, text: str, lang: str|None = None) -> SplitResult:
        result: SplitResult = SplitResult(text)
        result.tuples = [ SplitTuple(match.span()[0], match.span()[1], lang) for match in self.regex.finditer(result.text) ]
        return result
