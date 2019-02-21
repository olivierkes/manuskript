
from PyQt5.QtCore import QLocale

try:
    import enchant
except ImportError:
    enchant = None

class Spellchecker:
    dictionaries = {}

    def __init__(self):
        pass

    @staticmethod
    def isInstalled():
        return enchant is not None

    @staticmethod
    def availableDictionaries():
        return EnchantDictionary.availableDictionaries()

    @staticmethod
    def getDefaultDictionary():
        return EnchantDictionary.getDefaultDictionary()

    @staticmethod
    def getLibraryURL():
        return EnchantDictionary.getLibraryURL()

    @staticmethod
    def getDictionary(dictionary):
        if not dictionary:
            dictionary = Spellchecker.getDefaultDictionary()
        try:
            d = Spellchecker.dictionaries.get(dictionary, None)
            if d is None:
                d = EnchantDictionary(dictionary)
                Spellchecker.dictionaries[d.name] = d
            return d
        except Exception as e:
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
        return "pyEnchant"

    @staticmethod
    def getLibraryURL():
        return "https://pypi.org/project/pyenchant/"

    @staticmethod
    def availableDictionaries():
        if enchant:
            return list(map(lambda i: str(i[0]), enchant.list_dicts()))
        return []

    @staticmethod
    def getDefaultDictionary():
        if not enchant:
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
