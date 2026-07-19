#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.editor.splitResult import SplitResult, SplitTuple

import icu
import re


class AbstractSplitter:

    def __init__(self):
        pass

    def getName(self) -> str:
        return str(type(self))

    def isValid(self) -> bool:
        return False

    def splitText(self, text: str, lang: str|None = None) -> SplitResult:
        result: SplitResult = SplitResult(text)
        result.tuples.append(SplitTuple(0, len(text), lang))
        return result

    def splitRegions(self, regions: SplitResult) -> SplitResult:
        result: SplitResult = SplitResult(regions.text)

        for region in regions.tuples:
            text: str = regions.text[region.begin:region.end]

            for part in splitText(text, region.lang).tuples:
                part.begin += region.begin
                part.end += region.end

                result.tuples.append(
                    SplitTuple(region.begin + part.begin, region.begin + part.end, part.lang)
                )

        return result
