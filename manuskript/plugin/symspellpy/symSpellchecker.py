#!/usr/bin/env python
# --!-- coding: utf8 --!--

SYMSPELLPY_MIN_VERSION = "6.3.8"
try:
    import symspellpy
    import distutils.version

    if distutils.version.LooseVersion(symspellpy.__version__) < SYMSPELLPY_MIN_VERSION:
        symspellpy = None
    
except ImportError:
    symspellpy = None

from manuskript.spellchecker.abstractSpellchecker import AbstractSpellchecker


class SymSpellchecker(AbstractSpellchecker):

    def __init__(self, language: str):
        AbstractSpellchecker.__init__(self, [language])

        self.custom_words = dict()
        self.dictionary = symspellpy.SymSpell(2)
    
    def getName(self) -> str:
        return "symspellpy"

    def isValid(self) -> bool:
        return False if symspellpy is None else True
    
    def isMisspelled(self, word: str) -> bool:
        suggestions = self.dictionary.lookup(word.lower(), symspellpy.Verbosity.TOP)
        if (len(suggestions) > 0) and (suggestions[0].distance == 0):
            return False
        
        # Try the word as is, since a dictionary might have uppercase letter as part
        # of it's spelling ("I'm" or "January" for example)
        suggestions = self.dictionary.lookup(word, symspellpy.Verbosity.TOP)
        if (len(suggestions) > 0) and (suggestions[0].distance == 0):
            return False
        
        return True
    
    def getSuggestions(self, word: str) -> list[str]:
        upper = word.isupper()
        upper1 = word[0].isupper()

        suggestions = self.dictionary.lookup_compound(word, 2)
        suggestions.extend(self.dictionary.lookup(word, symspellpy.Verbosity.CLOSEST))
        candidates = []

        for sug in suggestions:
            if upper:
                term = sug.term.upper()
            elif upper1:
                term = sug.term[0].upper() + sug.term[1:]
            else:
                term = sug.term
            
            if sug.distance > 0 and not term in candidates:
                candidates.append(term)
        
        return candidates
    
    def isCustomWord(self, word: str) -> bool:
        lower: str = word.lower()
        return lower in self.custom_words
    
    def addCustomWord(self, word: str) -> bool:
        lower: str = word.lower()
        self.custom_words[lower] = True
        return self.dictionary.create_dictionary_entry(lower, 1)
    
    def removeCustomWord(self, word: str) -> bool:
        lower: str = word.lower()
        del self.custom_words[lower]
        return self.dictionary.delete_dictionary_entry(lower)
