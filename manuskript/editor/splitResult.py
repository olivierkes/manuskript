#!/usr/bin/env python
# --!-- coding: utf8 --!--

from io import StringIO
from typing import Optional


class SplitTuple:
    def __init__(self, begin: int, end: int, lang: str | None = None) -> None:
        self.begin: int = begin
        self.end: int = end
        self.lang: Optional[str] = lang


class SplitResult:
    def __init__(self, text: str) -> None:
        self.text: str = text
        self.tuples: list[SplitTuple] = []

    def __str__(self) -> str:
        result = self.text

        with StringIO() as s:
            empty = True
            s.write("[ ")

            for tuple in self.tuples:
                if not empty:
                    s.write(" | ")

                s.write(self.text[tuple.begin : tuple.end])

                if tuple.lang is not None:
                    s.write(" (")
                    s.write(tuple.lang)
                    s.write(")")

                empty = False

            s.write(" ]")
            result = s.getvalue()

        return result
