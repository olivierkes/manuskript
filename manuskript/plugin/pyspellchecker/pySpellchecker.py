#!/usr/bin/env python
# --!-- coding: utf8 --!--

try:
    import spellchecker as pyspellchecker
except ImportError:
    pyspellchecker = None

from manuskript.spellchecker.abstractSpellchecker import AbstractSpellchecker


class PySpellchecker(AbstractSpellchecker):

    def __init__(self, language: str):
        AbstractSpellchecker.__init__(self, [language])

        self.dictionary = pyspellchecker.SpellChecker(language)
    
    def getName(self) -> str:
        return "pyspellchecker"

    def isValid(self) -> bool:
        return False if pyspellchecker is None else True
    
    def isMisspelled(self, word: str) -> bool:
        return len(self.dictionary.unknown([word])) > 0
    
    def getSuggestions(self, word: str) -> list[str]:
        candidates = self.dictionary.candidates(word)
        if word in candidates:
            candidates.remove(word)
        return candidates
