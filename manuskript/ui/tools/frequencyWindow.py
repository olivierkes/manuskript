#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk

import re

from enum import Enum, unique

from manuskript.data import OutlineFolder, OutlineText, OutlineState, Project
from manuskript.ui.abstractDialog import AbstractDialog
from manuskript.util import validString, validInt


@unique
class AnalyzeStatus(Enum):
    NONE = 0
    WORDS = 1
    PHRASES = 2


class FrequencyWindow(AbstractDialog):

    def __init__(self, mainWindow):
        AbstractDialog.__init__(self, mainWindow, "ui/frequency.glade", "frequency_window")

        self.analyzeStatus = AnalyzeStatus.NONE
        self.frequencies = dict()
        self.outlineCompletion = list()
        self.analyzeCompleted = 0

        self.headerBar = None
        self.back = None
        self.wordLeaflet = None
        self.wordsProgress = None
        self.analyzeWords = None
        self.phrasesProgress = None
        self.analyzePhrases = None
        self.wordEntry = None
        self.removeWord = None
        self.addWord = None

        self.excludeWordSelection = None
        self.excludeWordsStore = None
        self.wordsFrequencyStore = None
        self.phrasesFrequencyStore = None

        self.phraseMinimum = None
        self.phraseMaximum = None
        self.wordSize = None

    def initWindow(self, builder, window):
        self.headerBar = builder.get_object("header_bar")
        self.back = builder.get_object("back")
        self.wordLeaflet = builder.get_object("word_leaflet")
        self.wordsProgress = builder.get_object("words_progress")
        self.analyzeWords = builder.get_object("analyze_words")
        self.phrasesProgress = builder.get_object("phrases_progress")
        self.analyzePhrases = builder.get_object("analyze_phrases")
        self.wordEntry = builder.get_object("word_entry")
        self.removeWord = builder.get_object("remove_word")
        self.addWord = builder.get_object("add_word")

        self.excludeWordSelection = builder.get_object("exclude_word_selection")
        self.excludeWordsStore = builder.get_object("exclude_words_store")
        self.wordsFrequencyStore = builder.get_object("words_frequency_store")
        self.phrasesFrequencyStore = builder.get_object("phrases_frequency_store")

        self.phraseMinimum = builder.get_object("phrase_minimum")
        self.phraseMaximum = builder.get_object("phrase_maximum")
        self.wordSize = builder.get_object("word_size")

        self.wordLeaflet.bind_property("folded", self.back, "visible",
                                       GObject.BindingFlags.SYNC_CREATE)
        self.wordLeaflet.bind_property("folded", self.headerBar, "show-close-button",
                                       GObject.BindingFlags.SYNC_CREATE |
                                       GObject.BindingFlags.INVERT_BOOLEAN)

        self.back.connect("clicked", self._backClicked)
        self.analyzeWords.connect("clicked", self._analyzeWordsClicked)
        self.analyzePhrases.connect("clicked", self._analyzePhrasesClicked)
        self.excludeWordSelection.connect("changed", self._excludeWordSelectionChanged)
        self.removeWord.connect("clicked", self._removeWordClicked)
        self.addWord.connect("clicked", self._addWordClicked)
    
    def getProject(self) -> Project:
        return self.mainWindow.getProject()

    def _backClicked(self, button: Gtk.Button):
        if self.wordLeaflet.get_visible_child_name() == "wordlist_view":
            self.wordLeaflet.set_visible_child_name("wordfilter_view")
        else:
            self.hide()
    
    def __analyzeOutlineText(self, outlineText: OutlineText):
        if self.analyzeStatus == AnalyzeStatus.WORDS:
            word_size = validInt(self.wordSize.get_value())

            patterns = [re.compile(r"\w{" + str(word_size) + r",}")]
        elif self.analyzeStatus == AnalyzeStatus.PHRASES:
            patterns = []

            phrase_minimum = validInt(self.phraseMinimum.get_value())
            phrase_maximum = validInt(self.phraseMaximum.get_value())

            for n in range(phrase_minimum, phrase_maximum + 1):
                patterns.append(re.compile(r"\w+" + r"\s+\w+" * (n - 1)))
        else:
            return
        
        for pattern in patterns:
            for match in pattern.findall(outlineText.text):
                if match in self.frequencies:
                    self.frequencies[match] = self.frequencies[match] + 1
                else:
                    self.frequencies[match] = 1
    
    def __completeOutlineItem(self):
        outline_item = self.outlineCompletion.pop(0)

        if isinstance(outline_item, OutlineFolder):
            for item in outline_item:
                self.outlineCompletion.append(item)
        elif isinstance(outline_item, OutlineText):
            if outline_item.state != OutlineState.COMPLETE:
                outline_item.load(False)

            self.__analyzeOutlineText(outline_item)
        
        self.analyzeCompleted = self.analyzeCompleted + 1

        incomplete = len(self.outlineCompletion)
        complete = self.analyzeCompleted
        fraction = 1.0 * complete / (complete + incomplete)

        if self.analyzeStatus == AnalyzeStatus.WORDS:
            self.wordsProgress.set_fraction(fraction)
        elif self.analyzeStatus == AnalyzeStatus.PHRASES:
            self.phrasesProgress.set_fraction(fraction)

        if incomplete > 0:
            return True
        
        if self.analyzeStatus == AnalyzeStatus.WORDS:
            self.wordsFrequencyStore.clear()

            for word, frequency in self.frequencies.items():
                tree_iter = self.wordsFrequencyStore.append()

                if tree_iter is None:
                    continue

                self.wordsFrequencyStore.set_value(tree_iter, 0, validString(word))
                self.wordsFrequencyStore.set_value(tree_iter, 1, validInt(frequency))
            
            self.wordLeaflet.set_visible_child_name("wordlist_view")
        elif self.analyzeStatus == AnalyzeStatus.PHRASES:
            self.phrasesFrequencyStore.clear()

            for phrase, frequency in self.frequencies.items():
                tree_iter = self.phrasesFrequencyStore.append()

                if tree_iter is None:
                    continue

                self.phrasesFrequencyStore.set_value(tree_iter, 0, validString(phrase))
                self.phrasesFrequencyStore.set_value(tree_iter, 1, validInt(frequency))
        
        self.analyzeStatus = AnalyzeStatus.NONE
        self.frequencies = dict()
        return False
    
    def analyze(self, status: AnalyzeStatus):
        if self.analyzeStatus != AnalyzeStatus.NONE:
            return

        project = self.getProject()

        if project is None:
            return
        
        self.analyzeStatus = status

        if len(self.outlineCompletion) == 0:
            self.frequencies = dict()
            self.analyzeCompleted = 0

            if self.analyzeStatus == AnalyzeStatus.WORDS:
                self.wordsProgress.set_fraction(0.0)
            elif self.analyzeStatus == AnalyzeStatus.PHRASES:
                self.phrasesProgress.set_fraction(0.0)

            GObject.idle_add(self.__completeOutlineItem)
        for outline_item in project.outline:
            self.outlineCompletion.append(outline_item)

    def _analyzeWordsClicked(self, button: Gtk.Button):
        self.analyze(AnalyzeStatus.WORDS)
    
    def _analyzePhrasesClicked(self, button: Gtk.Button):
        self.analyze(AnalyzeStatus.PHRASES)
    
    def _excludeWordSelectionChanged(self, selection: Gtk.TreeSelection):
        model, tree_iter = selection.get_selected()

        self.removeWord.set_sensitive(tree_iter is not None)
    
    def _removeWordClicked(self, button: Gtk.Button):
        model, tree_iter = self.excludeWordSelection.get_selected()

        if tree_iter is None:
            return
        
        self.excludeWordsStore.remove(tree_iter)
    
    def _addWordClicked(self, button: Gtk.Button):
        tree_iter = self.excludeWordsStore.append()

        if tree_iter is None:
            return
        
        word = self.wordEntry.get_buffer().get_text()
        self.excludeWordsStore.set_value(tree_iter, 0, word)
