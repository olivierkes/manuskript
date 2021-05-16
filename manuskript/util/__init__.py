#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from manuskript.util.counter import CharCounter, WordCounter, PageCounter


def validString(invalid: str) -> str:
    return "" if invalid is None else invalid


def invalidString(valid: str) -> str:
    return None if len(valid) == 0 else valid
