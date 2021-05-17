#!/usr/bin/env python
# --!-- coding: utf8 --!--

from enum import Enum, unique


@unique
class Importance(Enum):
    MINOR = 0
    SECONDARY = 1
    MAIN = 2

    @classmethod
    def asValue(cls, importance):
        return 0 if importance is None else importance.value

    @classmethod
    def fromRawString(cls, raw: str):
        if raw is None:
            return None

        try:
            return Importance(int(raw))
        except ValueError:
            return None

    @classmethod
    def toRawString(cls, importance):
        return None if importance is None else str(importance.value)
