#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from manuskript.data import Summary
from manuskript.util import WordCounter, PageCounter, validString, invalidString


class SummaryView:

    def __init__(self, summary: Summary):
        self.summary = summary

        builder = Gtk.Builder()
        builder.add_from_file("ui/summary.glade")

        self.widget = builder.get_object("summary_view")
        self.stack = builder.get_object("stack")

        self.stackCombo = builder.get_object("stack_combo")
        self.stackCombo.connect("changed", self._summaryStackChanged)

        self.situationBuffer = builder.get_object("situation")
        self.situationBuffer.connect("deleted-text", self._situationDeletedText)
        self.situationBuffer.connect("inserted-text", self._situationInsertedText)
        self.situationBuffer.set_text(validString(self.summary.situation), -1)

        self.oneSentenceLabel = builder.get_object("one_sentence_label")
        self.oneSentenceBuffer = builder.get_object("summary_one_sentence")
        self.oneSentenceBuffer.connect("changed", self._summaryOneSentenceChanged)
        self.oneSentenceBuffer.set_text(validString(self.summary.sentence), -1)

        self.oneParagraphLabel = builder.get_object("one_paragraph_label")
        self.oneParagraphBuffer = builder.get_object("summary_one_paragraph")
        self.oneParagraphBuffer.connect("changed", self._summaryOneParagraphChanged)
        self.oneParagraphBuffer.set_text(validString(self.summary.paragraph), -1)

        self.onePageLabel = builder.get_object("one_page_label")
        self.onePageBuffer = builder.get_object("summary_one_page")
        self.onePageBuffer.connect("changed", self._summaryOnePageChanged)
        self.onePageBuffer.set_text(validString(self.summary.page), -1)

        self.fullLabel = builder.get_object("full_label")
        self.fullBuffer = builder.get_object("summary_full")
        self.fullBuffer.connect("changed", self._summaryFullChanged)
        self.fullBuffer.set_text(validString(self.summary.full), -1)

        self.nextButton = builder.get_object("next_button")
        self.nextButton.connect("clicked", self._nextClicked)

    def show(self):
        self.widget.show_all()

    def _summaryStackChanged(self, combo: Gtk.ComboBox):
        tree_iter = combo.get_active_iter()

        if tree_iter is None:
            return

        model = combo.get_model()
        page = model[tree_iter][1]

        self.nextButton.set_visible(not (model.iter_next(tree_iter) is None))
        self.stack.set_visible_child_name(page)

    def __situationChanged(self, buffer: Gtk.EntryBuffer):
        self.summary.situation = invalidString(buffer.get_text())

    def _situationDeletedText(self, buffer: Gtk.EntryBuffer, position, count):
        self.__situationChanged(buffer)

    def _situationInsertedText(self, buffer: Gtk.EntryBuffer, position, value, count):
        self.__situationChanged(buffer)

    def _summaryOneSentenceChanged(self, buffer: Gtk.TextBuffer):
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.oneSentenceLabel.set_text("Words: {}".format(WordCounter.count(text)))
        self.summary.sentence = invalidString(text)

    def _summaryOneParagraphChanged(self, buffer: Gtk.TextBuffer):
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.oneParagraphLabel.set_text("Words: {}".format(WordCounter.count(text)))
        self.summary.paragraph = invalidString(text)

    def _summaryOnePageChanged(self, buffer: Gtk.TextBuffer):
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.onePageLabel.set_text("Words: {} (~{} pages)".format(WordCounter.count(text), PageCounter.count(text)))
        self.summary.page = invalidString(text)

    def _summaryFullChanged(self, buffer: Gtk.TextBuffer):
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.fullLabel.set_text("Words: {} (~{} pages)".format(WordCounter.count(text), PageCounter.count(text)))
        self.summary.full = invalidString(text)

    def _nextClicked(self, button: Gtk.Button):
        tree_iter = self.stackCombo.get_active_iter()

        if tree_iter is None:
            return

        model = self.stackCombo.get_model()
        tree_iter = model.iter_next(tree_iter)

        if tree_iter is None:
            return
        else:
            self.stackCombo.set_active_iter(tree_iter)
