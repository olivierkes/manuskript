#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk, Handy

from manuskript.ui.abstractDialog import AbstractDialog


class FrequencyWindow(AbstractDialog):

    def __init__(self, mainWindow):
        AbstractDialog.__init__(self, mainWindow, "ui/frequency.glade", "frequency_window")

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

    def _backClicked(self, button: Gtk.Button):
        if self.wordLeaflet.get_visible_child_name() == "wordlist_view":
            self.wordLeaflet.set_visible_child_name("wordfilter_view")
        else:
            self.hide()

    def _analyzeWordsClicked(self, button: Gtk.Button):
        self.wordLeaflet.set_visible_child_name("wordlist_view")
    
    def _analyzePhrasesClicked(self, button: Gtk.Button):
        pass
    
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
