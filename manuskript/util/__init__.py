#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from manuskript.util.counter import CharCounter, WordCounter, PageCounter


def safeInt(s: str, d: int) -> int:
    if s is None:
        return d

    try:
        return int(s)
    except ValueError:
        return d


def validString(invalid: str) -> str:
    return "" if invalid is None else invalid


def invalidString(valid: str) -> str:
    return None if len(valid) == 0 else valid


def validInt(invalid: int) -> int:
    return 0 if invalid is None else invalid


def invalidInt(valid: int) -> int:
    return None if valid == 0 else valid
