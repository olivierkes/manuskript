#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from enum import Enum, unique

_char_pattern_with_spaces = re.compile(r"[\S ]")
_char_pattern_without_spaces = re.compile(r"\S")
_word_pattern = re.compile(r"\S+")


@unique
class CounterKind(Enum):
    WORDS = 0
    CHARACTERS = 1
    PAGES = 2


class CharCounter:

    @classmethod
    def count(cls, text: str, use_spaces: bool = False):
        if use_spaces:
            return len(_char_pattern_with_spaces.findall(text))
        else:
            return len(_char_pattern_without_spaces.findall(text))


class WordCounter:

    @classmethod
    def count(cls, text: str):
        return len(_word_pattern.findall(text))


class PageCounter:

    @classmethod
    def count(cls, text: str):
        wc = WordCounter.count(text)
        return int(wc / 25) / 10.
