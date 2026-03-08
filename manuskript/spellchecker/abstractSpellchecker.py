#!/usr/bin/env python
# --!-- coding: utf8 --!--

from io import StringIO


class AbstractSpellchecker:

    def __init__(self, languages: list[str] = []):
        self.languages = languages
    
    def getName(self) -> str:
        return __class__.__name__
    
    def getTitle(self) -> str:
        output = StringIO()
        output.write(self.getName())
        output.write(": [")
        output.write(" ".join(self.languages))
        output.write("]")

        title = output.getvalue()
        output.close()
        return title

    def isValid(self) -> bool:
        return False

    def supportsLanguage(self, language: str) -> bool:
        if len(self.languages) == 0:
            return False
        elif language == "*":
            return True

        return language in self.languages
    
    def isMisspelled(self, word: str) -> bool:
        return False
    
    def getSuggestions(self, word: str) -> list[str]:
        return []
    
    def isCustomWord(self, word: str) -> bool:
        return False
    
    def addCustomWord(self, word: str) -> bool:
        return False
    
    def removeCustomWord(self, word: str) -> bool:
        return False
