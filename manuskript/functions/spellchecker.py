#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os, gzip, json, glob
from PyQt5.QtCore import QLocale
from collections import OrderedDict
from manuskript.functions import writablePath

try:
    import enchant
except ImportError:
    enchant = None

try:
    import spellchecker as pyspellchecker
except ImportError:
    pyspellchecker = None

SYMSPELLPY_MIN_VERSION = "6.3.8"
try:
    import symspellpy
    import distutils.version

    if distutils.version.LooseVersion(symspellpy.__version__) < SYMSPELLPY_MIN_VERSION:
        symspellpy = None
    
except ImportError:
    symspellpy = None


class Spellchecker:
    dictionaries = {}
    # In order of priority
    implementations = []

    def __init__(self):
        pass

    @staticmethod
    def registerImplementation(impl):
        Spellchecker.implementations.append(impl)

    @staticmethod
    def isInstalled():
        for impl in Spellchecker.implementations:
            if impl.isInstalled():
                return True
        return False

    @staticmethod
    def supportedLibraries():
        libs = OrderedDict()
        for impl in Spellchecker.implementations:
            libs[impl.getLibraryName()] = impl.getLibraryRequirement()
        return libs

    @staticmethod
    def availableLibraries():
        ret = []
        for impl in Spellchecker.implementations:
            if impl.isInstalled():
                ret.append(impl.getLibraryName())
        return ret

    @staticmethod
    def availableDictionaries():
        dictionaries = OrderedDict()
        for impl in Spellchecker.implementations:
            if impl.isInstalled():
                dictionaries[impl.getLibraryName()] = impl.availableDictionaries()
        return dictionaries

    @staticmethod
    def normalizeDictName(lib, dictionary):
        return "{}:{}".format(lib, dictionary)

    @staticmethod
    def getDefaultDictionary():
        for impl in Spellchecker.implementations:
            default = impl.getDefaultDictionary()
            if default:
                return Spellchecker.normalizeDictName(impl.getLibraryName(), default)
        return None

    @staticmethod
    def getLibraryURL(lib=None):
        urls = {}
        for impl in Spellchecker.implementations:
            urls[impl.getLibraryName()] = impl.getLibraryURL()
        if lib:
            return urls.get(lib, None)
        return urls

    @staticmethod
    def getDictionary(dictionary):
        if not dictionary:
            dictionary = Spellchecker.getDefaultDictionary()
        if not dictionary:
            return None

        values = dictionary.split(":", 1)
        if len(values) == 1:
            (lib, name) = (Spellchecker.implementations[0].getLibraryName(), dictionary)
            dictionary = Spellchecker.normalizeDictName(lib, name)
        else:
            (lib, name) = values
        try:
            d = Spellchecker.dictionaries.get(dictionary, None)
            if d is None:
                for impl in Spellchecker.implementations:
                    if impl.isInstalled() and lib == impl.getLibraryName():
                        d = impl(name)
                        Spellchecker.dictionaries[dictionary] = d
                        break
            return d
        except Exception as e:
            pass
        return None

class BasicDictionary:
    def __init__(self, name):
        self._lang = name
        if not self._lang:
            self._lang = self.getDefaultDictionary()

        self._customDict = set()
        customPath = self.getCustomDictionaryPath()
        try:
            with gzip.open(customPath, "rt", encoding='utf-8') as f:
                self._customDict = set(json.loads(f.read()))
                self.addCustomEntries(self._customDict)
        except:
            # If error loading the file, overwrite with empty dictionary
            self._saveCustomDict()

    @property
    def name(self):
        return self._lang

    @staticmethod
    def getLibraryName():
        raise NotImplemented

    @staticmethod
    def getLibraryRequirement():
        return None

    @staticmethod
    def getLibraryURL():
        raise NotImplemented

    @staticmethod
    def isInstalled():
        raise NotImplemented

    @staticmethod
    def getDefaultDictionary():
        raise NotImplemented

    @staticmethod
    def availableDictionaries():
        raise NotImplemented

    def isMisspelled(self, word):
        raise NotImplemented

    def getSuggestions(self, word):
        raise NotImplemented

    def isCustomWord(self, word):
        return word.lower() in self._customDict

    def addWord(self, word):
        word = word.lower()
        if not word in self._customDict:
            self._customDict.add(word)
            self._saveCustomDict()

    def removeWord(self, word):
        word = word.lower()
        if word in self._customDict:
            self._customDict.remove(word)
            self._saveCustomDict()

    @classmethod
    def getResourcesPath(cls):
        path = os.path.join(writablePath(), "resources", "dictionaries", cls.getLibraryName())
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def getCustomDictionaryPath(self):
        return os.path.join(self.getResourcesPath(), "{}.json.gz".format(self._lang))

    def _saveCustomDict(self):
        customPath = self.getCustomDictionaryPath()
        with gzip.open(customPath, "wt") as f:
            f.write(json.dumps(list(self._customDict)))
    
    def addCustomEntries(self, words):
        """
        Adds words from the custom dictionary, or another custom set of words 
        (such as character names), to the spellcheching engine. This method
        does not permenantly add the given words to the custom dictionary,
        it only loads the words into the spell-checking engine.

        Takes any iterable of string entries.
        """
        for word in words:
            self._dict.create_dictionary_entry(word, self.CUSTOM_COUNT)



class EnchantDictionary(BasicDictionary):

    def __init__(self, name):
        self._lang = name
        if not (self._lang and enchant.dict_exists(self._lang)):
            self._lang = self.getDefaultDictionary()

        self._dict = enchant.DictWithPWL(self._lang, self.getCustomDictionaryPath())

    @staticmethod
    def getLibraryName():
        return "PyEnchant"

    @staticmethod
    def getLibraryURL():
        return "https://pypi.org/project/pyenchant/"

    @staticmethod
    def isInstalled():
        return enchant is not None

    @staticmethod
    def availableDictionaries():
        if EnchantDictionary.isInstalled():
            return list(map(lambda i: str(i[0]), enchant.list_dicts()))
        return []

    @staticmethod
    def getDefaultDictionary():
        if not EnchantDictionary.isInstalled():
            return None

        default_locale = enchant.get_default_language()
        if default_locale and not enchant.dict_exists(default_locale):
            default_locale = None

        if default_locale is None:
            default_locale = QLocale.system().name()
        if default_locale is None:
            default_locale = self.availableDictionaries()[0]

        return default_locale

    def isMisspelled(self, word):
        return not self._dict.check(word)

    def getSuggestions(self, word):
        return self._dict.suggest(word)

    def isCustomWord(self, word):
        return self._dict.is_added(word)

    def addWord(self, word):
        self._dict.add(word)

    def removeWord(self, word):
        self._dict.remove(word)

    def getCustomDictionaryPath(self):
        return os.path.join(self.getResourcesPath(), "{}.txt".format(self.name))

class PySpellcheckerDictionary(BasicDictionary):

    def __init__(self, name):
        BasicDictionary.__init__(self, name)

        self._dict = pyspellchecker.SpellChecker(self.name)
        self._dict.word_frequency.load_words(self._customDict)

    @staticmethod
    def getLibraryName():
        return "pyspellchecker"

    @staticmethod
    def getLibraryURL():
        return "https://pyspellchecker.readthedocs.io/en/latest/"

    @staticmethod
    def isInstalled():
        return pyspellchecker is not None

    @staticmethod
    def availableDictionaries():
        if PySpellcheckerDictionary.isInstalled():
            dictionaries = []
            files = glob.glob(os.path.join(pyspellchecker.__path__[0], "resources", "*.json.gz"))
            for file in files:
                dictionaries.append(os.path.basename(file)[:-8])
            return dictionaries
        return []

    @staticmethod
    def getDefaultDictionary():
        if not PySpellcheckerDictionary.isInstalled():
            return None

        default_locale = QLocale.system().name()
        if default_locale:
            default_locale = default_locale[0:2]
        if default_locale is None:
            default_locale = "en"

        return default_locale

    def isMisspelled(self, word):
        return len(self._dict.unknown([word])) > 0

    def getSuggestions(self, word):
        candidates = self._dict.candidates(word)
        if word in candidates:
            candidates.remove(word)
        return candidates

    def addWord(self, word):
        BasicDictionary.addWord(self, word)
        self._dict.word_frequency.add(word.lower())

    def removeWord(self, word):
        BasicDictionary.removeWord(self, word)
        self._dict.word_frequency.remove(word.lower())

class SymSpellDictionary(BasicDictionary):
    CUSTOM_COUNT = 1
    DISTANCE = 2

    def __init__(self, name):
        BasicDictionary.__init__(self, name)

        self._dict = symspellpy.SymSpell(self.DISTANCE)

        cachePath = self.getCachedDictionaryPath()
        try:
            if not self._dict.load_pickle(cachePath, False):
                raise Exception("Can't load cached dictionary. " +
                                "File might be corrupted or incompatible with installed symspellpy version")
        except:
            if pyspellchecker:
                path = os.path.join(pyspellchecker.__path__[0], "resources", "{}.json.gz".format(self.name))
                if os.path.exists(path):
                    with gzip.open(path, "rt", encoding='utf-8') as f:
                        data = json.loads(f.read())
                        for key in data:
                            self._dict.create_dictionary_entry(key, data[key])
                    self._dict.save_pickle(cachePath, False)
        for word in self._customDict:
            self._dict.create_dictionary_entry(word, self.CUSTOM_COUNT)

    def getCachedDictionaryPath(self):
        return os.path.join(self.getResourcesPath(), "{}.sym".format(self.name))

    @staticmethod
    def getLibraryName():
        return "symspellpy"

    @staticmethod
    def getLibraryRequirement():
        return ">= " + SYMSPELLPY_MIN_VERSION

    @staticmethod
    def getLibraryURL():
        return "https://github.com/mammothb/symspellpy"

    @staticmethod
    def isInstalled():
        return symspellpy is not None

    @classmethod
    def availableDictionaries(cls):
        if SymSpellDictionary.isInstalled():
            files = glob.glob(os.path.join(cls.getResourcesPath(), "*.sym"))
            dictionaries = []
            for file in files:
                dictionaries.append(os.path.basename(file)[:-4])
            for sp_dict in PySpellcheckerDictionary.availableDictionaries():
                if not sp_dict in dictionaries:
                    dictionaries.append(sp_dict)
            return dictionaries
        return []

    @staticmethod
    def getDefaultDictionary():
        if not SymSpellDictionary.isInstalled():
            return None

        return PySpellcheckerDictionary.getDefaultDictionary()

    def isMisspelled(self, word):
        suggestions = self._dict.lookup(word.lower(), symspellpy.Verbosity.TOP)
        if len(suggestions) > 0 and suggestions[0].distance == 0:
            return False
        # Try the word as is, since a dictionary might have uppercase letter as part
        # of it's spelling ("I'm" or "January" for example)
        suggestions = self._dict.lookup(word, symspellpy.Verbosity.TOP)
        if len(suggestions) > 0 and suggestions[0].distance == 0:
            return False
        return True

    def getSuggestions(self, word):
        upper = word.isupper()
        upper1 = word[0].isupper()
        suggestions = self._dict.lookup_compound(word, 2)
        suggestions.extend(self._dict.lookup(word, symspellpy.Verbosity.CLOSEST))
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

    def addWord(self, word):
        BasicDictionary.addWord(self, word)
        self._dict.create_dictionary_entry(word.lower(), self.CUSTOM_COUNT)

    def removeWord(self, word):
        BasicDictionary.removeWord(self, word)
        # Since 6.3.8
        self._dict.delete_dictionary_entry(word)


# Register the implementations in order of priority
Spellchecker.implementations.append(EnchantDictionary)
Spellchecker.registerImplementation(SymSpellDictionary)
Spellchecker.registerImplementation(PySpellcheckerDictionary)
