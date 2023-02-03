#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from manuskript.util.counter import CounterKind, CharCounter, WordCounter, PageCounter


def safeInt(s: str, d: int) -> int:
    if s is None:
        return d

    try:
        return int(s)
    except ValueError:
        return d


def validString(invalid) -> str:
    return "" if invalid is None else str(invalid)


def invalidString(valid: str) -> str:
    return None if len(valid) == 0 else valid


def validInt(invalid) -> int:
    return 0 if invalid is None else int(invalid)


def invalidInt(valid: int) -> int:
    return None if valid == 0 else valid


def safeFilename(filename: str, extension: str = None) -> str:
    if extension is not None:
        filename = "%s.%s" % (filename, extension)

    name = filename.encode('ascii', 'replace').decode('ascii')
    filenamesToAvoid = list(["CON", "PRN", "AUX", "NUL"])

    for i in range(1, 9):
        filenamesToAvoid.append("COM" + str(i))
        filenamesToAvoid.append("LPT" + str(i))

    if name.upper() in filenamesToAvoid:
        name = "_" + name

    return re.sub(r"[^a-zA-Z0-9._\-+()]", "_", name)


def countText(text: str, kind: CounterKind = CounterKind.WORDS):
    if text is None:
        return 0

    if kind == CounterKind.CHARACTERS:
        return CharCounter.count(text)
    elif kind == CounterKind.WORDS:
        return WordCounter.count(text)
    elif kind == CounterKind.PAGES:
        return PageCounter.count(text)
    else:
        return 0


def safeFraction(value, low, high) -> float:
    if value < low:
        return 0.0
    elif value > high:
        return 1.0
    else:
        return 1.0 * (value - low) / (high - low)
