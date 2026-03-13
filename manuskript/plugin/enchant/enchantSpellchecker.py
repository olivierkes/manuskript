#!/usr/bin/env python
# --!-- coding: utf8 --!--

try:
    import enchant
except ModuleNotFoundError:
    enchant = None

from manuskript.spellchecker.abstractSpellchecker import AbstractSpellchecker


class EnchantSpellchecker(AbstractSpellchecker):

    def __init__(self, language: str):
        AbstractSpellchecker.__init__(self, [language])

        self.dictionary = enchant.DictWithPWL(language)
    
    def getName(self) -> str:
        return "PyEnchant"

    def isValid(self) -> bool:
        return False if enchant is None else True
    
    def isMisspelled(self, word: str) -> bool:
        return not self.dictionary.check(word)
    
    def getSuggestions(self, word: str) -> list[str]:
        return self.dictionary.suggest(word)
    
    def isCustomWord(self, word: str) -> bool:
        return self.dictionary.is_added(word)
    
    def addCustomWord(self, word: str) -> bool:
        self.dictionary.add(word)
        return True
    
    def removeCustomWord(self, word: str) -> bool:
        self.dictionary.remove(word)
        return True
