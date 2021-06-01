#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re


class CharCounter:

    @classmethod
    def count(cls, text: str, use_spaces: bool = False):
        if use_spaces:
            return len(re.findall(r"[\S ]", text))
        else:
            return len(re.findall(r"\S", text))


class WordCounter:

    @classmethod
    def count(cls, text: str):
        return len(re.findall(r"\S+", text))


class PageCounter:

    @classmethod
    def count(cls, text: str):
        wc = WordCounter.count(text)
        return int(wc / 25) / 10.
