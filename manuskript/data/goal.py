#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.util import CounterKind, countText


class Goal:

    def __init__(self, value: int = 0, kind: CounterKind = CounterKind.WORDS):
        self.value = max(value, 0)
        self.kind = kind

    def prettyString(self):
        return str(self.value) + " " + self.kind.name.lower()

    def __str__(self):
        if self.kind != CounterKind.WORDS:
            return self.prettyString()
        else:
            return str(self.value)

    def count(self, text: str):
        return countText(text, self.kind)

    @classmethod
    def parse(cls, string: str):
        if string is None:
            return None

        parts = string.split(" ")

        try:
            value = int(parts[0])
            kind = CounterKind[parts[1].upper()] if len(parts) > 1 else CounterKind.WORDS
        except ValueError:
            return None

        return Goal(value, kind)
