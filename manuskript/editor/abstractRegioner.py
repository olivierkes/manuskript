#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.editor.splitResult import SplitResult, SplitTuple


class AbstractRegioner:

    def __init__(self, languages: list[str] = []):
        self.supportedLanguages: list[str] = languages

    def getName(self) -> str:
        return str(type(self))

    def isValid(self) -> bool:
        return False if len(self.self.supportedLanguages) == 0 else True

    def splitText(self, text: str) -> SplitResult:
        result: SplitResult = SplitResult(text)
        language: str|None = None

        if len(self.supportedLanguages) > 0:
            language = self.supportedLanguages[0]

        result.tuples.append(SplitTuple(0, len(text), language))
        return result
