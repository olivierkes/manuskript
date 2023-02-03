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
        self.analyzeWords = None
        self.analyzePhrases = None

    def initWindow(self, builder, window):
        self.headerBar = builder.get_object("header_bar")
        self.back = builder.get_object("back")
        self.wordLeaflet = builder.get_object("word_leaflet")
        self.analyzeWords = builder.get_object("analyze_words")
        self.analyzePhrases = builder.get_object("analyze_phrases")

        self.wordLeaflet.bind_property("folded", self.back, "visible",
                                       GObject.BindingFlags.SYNC_CREATE)
        self.wordLeaflet.bind_property("folded", self.headerBar, "show-close-button",
                                       GObject.BindingFlags.SYNC_CREATE |
                                       GObject.BindingFlags.INVERT_BOOLEAN)

        self.back.connect("clicked", self._backClicked)
        self.analyzeWords.connect("clicked", self._analyzeWordsClicked)

    def _backClicked(self, button: Gtk.Button):
        if self.wordLeaflet.get_visible_child_name() == "wordlist_view":
            self.wordLeaflet.set_visible_child_name("wordfilter_view")
        else:
            self.hide()

    def _analyzeWordsClicked(self, button: Gtk.Button):
        self.wordLeaflet.set_visible_child_name("wordlist_view")
