#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.editor.splitResult import SplitResult, SplitTuple


class AbstractRegioner:

    def __init__(self, languages: list[str] = []):
        self.supportedLanguages: list[str] = languages

    def getName(self) -> str:
        return str(type(self))

    def isValid(self) -> bool:
        return len(self.supportedLanguages) != 0

    def splitText(self, text: str) -> SplitResult:
        result: SplitResult = SplitResult(text)
        language: str|None = None

        if len(self.supportedLanguages) > 0:
            language = self.supportedLanguages[0]

        start = 0
        while start < len(text):
          end = text.find('\n', start)
          if end < start:
            end = len(text)

          result.tuples.append(SplitTuple(start, end, language))
          start = end + 1

        return result
