#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from manuskript.util import WordCounter, PageCounter


class SummaryView:

    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file("ui/summary.glade")

        self.widget = builder.get_object("summary_view")
        self.stack = builder.get_object("stack")

        stackCombo = builder.get_object("stack_combo")
        stackCombo.connect("changed", self.summaryStackChanged)

        self.situationBuffer = builder.get_object("situation")

        self.oneSentenceBuffer = builder.get_object("summary_one_sentence")
        self.oneSentenceLabel = builder.get_object("one_sentence_label")

        self.oneParagraphBuffer = builder.get_object("summary_one_paragraph")
        self.oneParagraphLabel = builder.get_object("one_paragraph_label")

        self.onePageBuffer = builder.get_object("summary_one_page")
        self.onePageLabel = builder.get_object("one_page_label")

        self.fullBuffer = builder.get_object("summary_full")
        self.fullLabel = builder.get_object("full_label")

        self.situationBuffer.connect("deleted-text", self.situationDeletedText)
        self.situationBuffer.connect("inserted-text", self.situationInsertedText)
        self.oneSentenceBuffer.connect("changed", self.summaryOneSentenceChanged)
        self.oneParagraphBuffer.connect("changed", self.summaryOneParagraphChanged)
        self.onePageBuffer.connect("changed", self.summaryOnePageChanged)
        self.fullBuffer.connect("changed", self.summaryFullChanged)

    def show(self):
        self.widget.show_all()

    def summaryStackChanged(self, combo):
        tree_iter = combo.get_active_iter()

        if tree_iter is None:
            return

        model = combo.get_model()
        page = model[tree_iter][1]

        self.stack.set_visible_child_name(page)

    def situationChanged(self, buffer: Gtk.EntryBuffer):
        print(buffer.get_text())

    def situationDeletedText(self, buffer: Gtk.EntryBuffer, position, count):
        self.situationChanged(buffer)

    def situationInsertedText(self, buffer: Gtk.EntryBuffer, position, value, count):
        self.situationChanged(buffer)

    def summaryOneSentenceChanged(self, buffer: Gtk.TextBuffer):
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.oneSentenceLabel.set_text("Words: {}".format(WordCounter.count(text)))

    def summaryOneParagraphChanged(self, buffer: Gtk.TextBuffer):
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.oneParagraphLabel.set_text("Words: {}".format(WordCounter.count(text)))

    def summaryOnePageChanged(self, buffer: Gtk.TextBuffer):
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.onePageLabel.set_text("Words: {} (~{} pages)".format(WordCounter.count(text), PageCounter.count(text)))

    def summaryFullChanged(self, buffer: Gtk.TextBuffer):
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        text = buffer.get_text(start_iter, end_iter, False)

        self.fullLabel.set_text("Words: {} (~{} pages)".format(WordCounter.count(text), PageCounter.count(text)))
