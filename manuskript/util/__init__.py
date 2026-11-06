#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import time
import urllib.parse

from manuskript.util.counter import CounterKind, CharCounter, WordCounter, PageCounter
from manuskript.util.translation import Translation

_translation = Translation()
_translation.bind()


def getTranslation() -> Translation:
    return _translation


def _(message: str, plural_message: str | None = None, n: int = 1) -> str:
    return getTranslation().translate(message, plural_message, n)


def safeInt(s: str | None, d: int) -> int:
    if s is None:
        return d

    try:
        return int(s)
    except ValueError:
        return d


def validString(invalid: str | None) -> str:
    return "" if invalid is None else str(invalid)


def invalidString(valid: str) -> str | None:
    return None if len(valid) == 0 else valid


def validInt(invalid: int | None, defaultValue: int = 0) -> int:
    return defaultValue if invalid is None else int(invalid)


def invalidInt(valid: int) -> int | None:
    return None if valid == 0 else valid


def validBool(invalid: bool | str | None) -> bool:
    return str(invalid) != str(False)


def safeFilename(filename: str, extension: str | None = None) -> str:
    if extension is not None:
        filename = f"{filename}.{extension}"

    name = filename.encode("ascii", "replace").decode("ascii")
    filenamesToAvoid = ["CON", "PRN", "AUX", "NUL"]

    for i in range(1, 9):
        filenamesToAvoid.append("COM" + str(i))
        filenamesToAvoid.append("LPT" + str(i))

    if name.upper() in filenamesToAvoid:
        name = "_" + name

    return re.sub(r"[^a-zA-Z0-9._\-+()]", "_", name)


def parseFilenameFromURL(url: str) -> str | None:
    result = urllib.parse.urlparse(url)

    if result is None:
        return None

    if result.scheme != "file":
        return None

    return result.path


def countText(text: str, kind: CounterKind = CounterKind.WORDS) -> int:
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


def safeFraction(value: float, low: float, high: float) -> float:
    if value < low or high <= low:
        return 0.0
    elif value > high:
        return 1.0
    else:
        return 1.0 * (value - low) / (high - low)


def profileTime(func, *args):
    start = time.perf_counter()
    result = func(*args)
    end = time.perf_counter()
    print(f"{func.__module__}.{func.__name__}: {end - start}")
    return result
