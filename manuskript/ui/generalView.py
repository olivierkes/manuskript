#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class GeneralView:

    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file("ui/general.glade")

        self.widget = builder.get_object("general_view")

        self.titleBuffer = builder.get_object("title")
        self.subtitleBuffer = builder.get_object("subtitle")
        self.seriesBuffer = builder.get_object("series")
        self.volumeBuffer = builder.get_object("volume")
        self.genreBuffer = builder.get_object("genre")
        self.licenseBuffer = builder.get_object("license")
        self.nameBuffer = builder.get_object("name")
        self.emailBuffer = builder.get_object("email")

        self.titleBuffer.connect("deleted-text", self._titleDeletedText)
        self.titleBuffer.connect("inserted-text", self._titleInsertedText)
        self.subtitleBuffer.connect("deleted-text", self._subtitleDeletedText)
        self.subtitleBuffer.connect("inserted-text", self._subtitleInsertedText)
        self.seriesBuffer.connect("deleted-text", self._seriesDeletedText)
        self.seriesBuffer.connect("inserted-text", self._seriesInsertedText)
        self.volumeBuffer.connect("deleted-text", self._volumeDeletedText)
        self.volumeBuffer.connect("inserted-text", self._volumeInsertedText)
        self.genreBuffer.connect("deleted-text", self._genreDeletedText)
        self.genreBuffer.connect("inserted-text", self._genreInsertedText)
        self.licenseBuffer.connect("deleted-text", self._licenseDeletedText)
        self.licenseBuffer.connect("inserted-text", self._licenseInsertedText)
        self.nameBuffer.connect("deleted-text", self._nameDeletedText)
        self.nameBuffer.connect("inserted-text", self._nameInsertedText)
        self.emailBuffer.connect("deleted-text", self._emailDeletedText)
        self.emailBuffer.connect("inserted-text", self._emailInsertedText)

    def titleChanged(self, buffer: Gtk.EntryBuffer):
        print("title: " + buffer.get_text())

    def subtitleChanged(self, buffer: Gtk.EntryBuffer):
        print("subtitle: " + buffer.get_text())

    def seriesChanged(self, buffer: Gtk.EntryBuffer):
        print("series: " + buffer.get_text())

    def volumeChanged(self, buffer: Gtk.EntryBuffer):
        print("volume: " + buffer.get_text())

    def genreChanged(self, buffer: Gtk.EntryBuffer):
        print("genre: " + buffer.get_text())

    def licenseChanged(self, buffer: Gtk.EntryBuffer):
        print("license: " + buffer.get_text())

    def nameChanged(self, buffer: Gtk.EntryBuffer):
        print("name: " + buffer.get_text())

    def emailChanged(self, buffer: Gtk.EntryBuffer):
        print("email: " + buffer.get_text())

    def _titleDeletedText(self, buffer: Gtk.EntryBuffer, position, count):
        self.titleChanged(buffer)

    def _titleInsertedText(self, buffer: Gtk.EntryBuffer, position, value, count):
        self.titleChanged(buffer)

    def _subtitleDeletedText(self, buffer: Gtk.EntryBuffer, position, count):
        self.subtitleChanged(buffer)

    def _subtitleInsertedText(self, buffer: Gtk.EntryBuffer, position, value, count):
        self.subtitleChanged(buffer)

    def _seriesDeletedText(self, buffer: Gtk.EntryBuffer, position, count):
        self.seriesChanged(buffer)

    def _seriesInsertedText(self, buffer: Gtk.EntryBuffer, position, value, count):
        self.seriesChanged(buffer)

    def _volumeDeletedText(self, buffer: Gtk.EntryBuffer, position, count):
        self.volumeChanged(buffer)

    def _volumeInsertedText(self, buffer: Gtk.EntryBuffer, position, value, count):
        self.volumeChanged(buffer)

    def _genreDeletedText(self, buffer: Gtk.EntryBuffer, position, count):
        self.genreChanged(buffer)

    def _genreInsertedText(self, buffer: Gtk.EntryBuffer, position, value, count):
        self.genreChanged(buffer)

    def _licenseDeletedText(self, buffer: Gtk.EntryBuffer, position, count):
        self.licenseChanged(buffer)

    def _licenseInsertedText(self, buffer: Gtk.EntryBuffer, position, value, count):
        self.licenseChanged(buffer)

    def _nameDeletedText(self, buffer: Gtk.EntryBuffer, position, count):
        self.nameChanged(buffer)

    def _nameInsertedText(self, buffer: Gtk.EntryBuffer, position, value, count):
        self.nameChanged(buffer)

    def _emailDeletedText(self, buffer: Gtk.EntryBuffer, position, count):
        self.emailChanged(buffer)

    def _emailInsertedText(self, buffer: Gtk.EntryBuffer, position, value, count):
        self.emailChanged(buffer)

    def show(self):
        self.widget.show_all()
