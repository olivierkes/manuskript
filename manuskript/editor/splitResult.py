#!/usr/bin/env python
# --!-- coding: utf8 --!--


class SplitTuple:

    def __init__(self, begin: int, end: int, lang: str|None = None):
        self.begin: int = begin
        self.end: int = end
        self.lang: str = lang


class SplitResult:

    def __init__(self, text: str):
        self.text: str = text
        self.tuples: list[SplitTuple] = []
