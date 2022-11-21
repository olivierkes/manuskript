#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os, gzip, json, glob, re
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


use_language_check = False

try:
    try:
        import language_tool_python as languagetool
    except:
        import language_check as languagetool
        use_language_check = True
except:
    languagetool = None

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
            if d == None:
                for impl in Spellchecker.implementations:
                    if impl.isInstalled() and lib == impl.getLibraryName():
                        d = impl(name)
                        Spellchecker.dictionaries[dictionary] = d
                        break
            return d
        except Exception as e:
            pass
        return None

class BasicMatch:
    def __init__(self, startIndex, endIndex):
        self.start = startIndex
        self.end = endIndex
        self.locqualityissuetype = 'misspelling'
        self.replacements = []
        self.msg = ''

    def getWord(self, text):
        return text[self.start:self.end]

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
                for word in self._customDict:
                    self._dict.create_dictionary_entry(word, self.CUSTOM_COUNT)
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

    def checkText(self, text):
        # Based on http://john.nachtimwald.com/2009/08/22/qplaintextedit-with-in-line-spell-check/
        WORDS = r'(?iu)((?:[^_\W]|\')+)[^A-Za-z0-9\']'
        #         (?iu) means case insensitive and Unicode
        #              ((?:[^_\W]|\')+) means words exclude underscores but include apostrophes
        #                              [^A-Za-z0-9\'] used with above hack to prevent spellcheck while typing word
        #
        # See also https://stackoverflow.com/questions/2062169/regex-w-in-utf-8

        matches = []

        for word_object in re.finditer(WORDS, text):
            word = word_object.group(1)

            if (self.isMisspelled(word) and not self.isCustomWord(word)):
                matches.append(BasicMatch(
                    word_object.start(1), word_object.end(1)
                ))

        return matches

    def isMisspelled(self, word):
        raise NotImplemented

    def getSuggestions(self, word):
        raise NotImplemented

    def findSuggestions(self, text, start, end):
        if start < end:
            word = text[start:end]

            if (self.isMisspelled(word) and not self.isCustomWord(word)):
                match = BasicMatch(start, end)
                match.replacements = self.getSuggestions(word)

                return [ match ]

        return []

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
        return enchant != None

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

        if default_locale == None:
            default_locale = QLocale.system().name()
        if default_locale == None:
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
        return pyspellchecker != None

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
        if default_locale == None:
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
        return symspellpy != None

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

def get_languagetool_match_errorLength(match):
    if use_language_check:
        return match.errorlength
    else:
        return match.errorLength

def get_languagetool_match_ruleIssueType(match):
    if use_language_check:
        return match.locqualityissuetype
    else:
        return match.ruleIssueType

def get_languagetool_match_message(match):
    if use_language_check:
        return match.msg
    else:
        return match.message

class LanguageToolCache:

    def __init__(self, tool, text):
        self._length = len(text)
        self._matches = self._buildMatches(tool, text)

    def getMatches(self):
        return self._matches

    def _buildMatches(self, tool, text):
        matches = []

        for match in tool.check(text):
            start = match.offset
            end = start + get_languagetool_match_errorLength(match)

            basic_match = BasicMatch(start, end)
            basic_match.locqualityissuetype = get_languagetool_match_ruleIssueType(match)
            basic_match.replacements = match.replacements
            basic_match.msg = get_languagetool_match_message(match)

            matches.append(basic_match)

        return matches

    def update(self, tool, text):
        if len(text) != self._length:
            self._matches = self._buildMatches(tool, text)

def get_languagetool_languages(tool):
    if use_language_check:
        return languagetool.get_languages()
    else:
        return tool._get_languages()

def get_languagetool_locale_language():
    if use_language_check:
        return languagetool.get_locale_language()
    else:
        return languagetool.utils.get_locale_language()

class LanguageToolDictionary(BasicDictionary):

    _tool = None

    def __init__(self, name):
        BasicDictionary.__init__(self, name)

        if not (self._lang and self._lang in get_languagetool_languages(self.getTool())):
            self._lang = self.getDefaultDictionary()

        self.tool = languagetool.LanguageTool(self._lang)
        self._cache = {}

    @staticmethod
    def getTool():
        if LanguageToolDictionary._tool == None:
            try:
                LanguageToolDictionary._tool = languagetool.LanguageTool()
            except:
                return None

        return LanguageToolDictionary._tool

    @staticmethod
    def getLibraryName():
        return "LanguageTool"

    @staticmethod
    def getLibraryURL():
        if use_language_check:
            return "https://pypi.org/project/language-check/"
        else:
            return "https://pypi.org/project/language-tool-python/"

    @staticmethod
    def isInstalled():
        if (languagetool != None) and (LanguageToolDictionary.getTool() != None):

            # This check, if Java is installed, is necessary to
            # make sure LanguageTool can be run without problems.
            #
            return (os.system('java -version') == 0)

        return False

    @staticmethod
    def availableDictionaries():
        if LanguageToolDictionary.isInstalled():
            tool = LanguageToolDictionary.getTool()
            languages = list(get_languagetool_languages(tool))
            languages.sort()
            return languages

        return []

    @staticmethod
    def getDefaultDictionary():
        if not LanguageToolDictionary.isInstalled():
            return None

        default_locale = get_languagetool_locale_language()
        tool = LanguageToolDictionary.getTool()

        if default_locale and not default_locale in get_languagetool_languages(tool):
            default_locale = None

        if default_locale == None:
            default_locale = QLocale.system().name()
        if default_locale == None:
            default_locale = self.availableDictionaries()[0]

        return default_locale

    def checkText(self, text):
        matches = []

        if len(text) == 0:
            return matches

        textId = hash(text)
        cacheEntry = None

        if not textId in self._cache:
            cacheEntry = LanguageToolCache(self.tool, text)

            self._cache[textId] = cacheEntry
        else:
            cacheEntry = self._cache[textId]
            cacheEntry.update(self.tool, text)

        for match in cacheEntry.getMatches():
            word = match.getWord(text)

            if not (match.locqualityissuetype == 'misspelling' and self.isCustomWord(word)):
                matches.append(match)

        return matches

    def isMisspelled(self, word):
        if self.isCustomWord(word):
            return False

        for match in self.checkText(word):
            if match.locqualityissuetype == 'misspelling':
                return True

        return False

    def getSuggestions(self, word):
        suggestions = []

        for match in self.checkText(word):
            suggestions += match.replacements

        return suggestions

    def findSuggestions(self, text, start, end):
        matches = []
        checked = self.checkText(text)

        if start == end:
            # Check for containing area:
            for match in checked:
                if (start >= match.start and start <= match.end):
                    matches.append(match)
        else:
            # Check for overlapping area:
            for match in checked:
                if (match.end > start and match.start < end):
                    matches.append(match)

        return matches


# Register the implementations in order of priority
Spellchecker.registerImplementation(EnchantDictionary)
Spellchecker.registerImplementation(SymSpellDictionary)
Spellchecker.registerImplementation(PySpellcheckerDictionary)
Spellchecker.registerImplementation(LanguageToolDictionary)
