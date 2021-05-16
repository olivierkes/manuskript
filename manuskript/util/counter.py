#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class CharCounter:

    @classmethod
    def count(cls, text: str, use_spaces: bool = False):
        t = text.strip()

        if not use_spaces:
            t = t.replace(" ", "")

        return len(t)


class WordCounter:

    @classmethod
    def count(cls, text: str):
        t = text.strip().replace(" ", "\n").split("\n")
        t = [l for l in t if len(l) > 0]
        return len(t)


class PageCounter:

    @classmethod
    def count(cls, text: str):
        wc = WordCounter.count(text)
        return int(wc / 25) / 10.
