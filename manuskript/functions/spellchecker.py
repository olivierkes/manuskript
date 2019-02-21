
import os, gzip, json
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


class Spellchecker:
    dictionaries = {}
    # In order of priority
    implementations = []

    def __init__(self):
        pass

    @staticmethod
    def isInstalled():
        for impl in Spellchecker.implementations:
            if impl.isInstalled():
                return True
        return False

    @staticmethod
    def supportedLibraries():
        libs = []
        for impl in Spellchecker.implementations:
            libs.append(impl.getLibraryName())
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
    def getResourcesPath(library):
        path = os.path.join(writablePath(), "resources", "dictionaries", library)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

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
                    if lib == impl.getLibraryName():
                        d = impl(name)
                        Spellchecker.dictionaries[dictionary] = d
                        break
            return d
        except Exception as e:
            pass
        return None

class BasicDictionary:
    def __init__(self, name):
        pass

    @property
    def name(self):
        raise NotImplemented

    @staticmethod
    def getLibraryName():
        raise NotImplemented

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
        raise NotImplemented

    def addWord(self, word):
        raise NotImplemented

    def removeWord(self, word):
        raise NotImplemented

class EnchantDictionary(BasicDictionary):

    def __init__(self, name):
        self._lang = name
        if not (self._lang and enchant.dict_exists(self._lang)):
            self._lang = self.getDefaultDictionary()

        self._dict = enchant.Dict(self._lang)

    @property
    def name(self):
        return self._lang

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
Spellchecker.implementations.append(EnchantDictionary)


class PySpellcheckerDictionary(BasicDictionary):

    def __init__(self, name):
        self._lang = name
        if not self._lang:
            self._lang = self.getDefaultDictionary()

        self._dict = pyspellchecker.SpellChecker(self._lang)
        self._customDict = None
        customPath = self.getCustomDictionaryPath()
        try:
            self._customDict = pyspellchecker.SpellChecker(local_dictionary=customPath)
            self._dict.word_frequency.load_dictionary(customPath)
        except:
            # If error loading the file, overwrite with empty dictionary
            with gzip.open(customPath, "wt") as f:
                f.write(json.dumps({}))
                
        self._customDict = pyspellchecker.SpellChecker(local_dictionary=customPath)
        self._dict.word_frequency.load_dictionary(customPath)

    def getCustomDictionaryPath(self):
        return os.path.join(Spellchecker.getResourcesPath(self.getLibraryName()), "{}.json.gz".format(self._lang))

    @property
    def name(self):
        return self._lang

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
            # TODO: If pyspellchecker eventually adds a way to get this list
            # programmatically or if the list changes, we need to update it here
            return ["de", "en", "es", "fr", "pt"]
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

    def isCustomWord(self, word):
        return len(self._customDict.known([word])) > 0

    def addWord(self, word):
        self._dict.word_frequency.add(word)
        self._customDict.word_frequency.add(word)
        self._customDict.export(self.getCustomDictionaryPath(), gzipped=True)

    def removeWord(self, word):
        self._dict.word_frequency.remove(word)
        self._customDict.word_frequency.remove(word)
        self._customDict.export(self.getCustomDictionaryPath(), gzipped=True)

Spellchecker.implementations.append(PySpellcheckerDictionary)
