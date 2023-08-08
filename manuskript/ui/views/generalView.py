#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from manuskript.data import Info
from manuskript.util import validString, invalidString
from manuskript.quoteOfTheDay import get_quote

class GeneralView:

    def __init__(self, info: Info):
        self.info = info

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
        
        self.quoteLabel = builder.get_object("quote_label")

        self.titleBuffer.set_text(validString(self.info.title), -1)
        self.subtitleBuffer.set_text(validString(self.info.subtitle), -1)
        self.seriesBuffer.set_text(validString(self.info.serie), -1)
        self.volumeBuffer.set_text(validString(self.info.volume), -1)
        self.genreBuffer.set_text(validString(self.info.genre), -1)
        self.licenseBuffer.set_text(validString(self.info.license), -1)
        self.nameBuffer.set_text(validString(self.info.author), -1)
        self.emailBuffer.set_text(validString(self.info.email), -1)

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
        
        self.quoteLabel.set_text(get_quote())


    def __titleChanged(self, buffer: Gtk.EntryBuffer):
        self.info.title = invalidString(buffer.get_text())

    def __subtitleChanged(self, buffer: Gtk.EntryBuffer):
        self.info.subtitle = invalidString(buffer.get_text())

    def __seriesChanged(self, buffer: Gtk.EntryBuffer):
        self.info.serie = invalidString(buffer.get_text())

    def __volumeChanged(self, buffer: Gtk.EntryBuffer):
        self.info.volume = invalidString(buffer.get_text())

    def __genreChanged(self, buffer: Gtk.EntryBuffer):
        self.info.genre = invalidString(buffer.get_text())

    def __licenseChanged(self, buffer: Gtk.EntryBuffer):
        self.info.license = invalidString(buffer.get_text())

    def __nameChanged(self, buffer: Gtk.EntryBuffer):
        self.info.author = invalidString(buffer.get_text())

    def __emailChanged(self, buffer: Gtk.EntryBuffer):
        self.info.email = invalidString(buffer.get_text())

    def _titleDeletedText(self, buffer: Gtk.EntryBuffer, position, count):
        self.__titleChanged(buffer)

    def _titleInsertedText(self, buffer: Gtk.EntryBuffer, position, value, count):
        self.__titleChanged(buffer)

    def _subtitleDeletedText(self, buffer: Gtk.EntryBuffer, position, count):
        self.__subtitleChanged(buffer)

    def _subtitleInsertedText(self, buffer: Gtk.EntryBuffer, position, value, count):
        self.__subtitleChanged(buffer)

    def _seriesDeletedText(self, buffer: Gtk.EntryBuffer, position, count):
        self.__seriesChanged(buffer)

    def _seriesInsertedText(self, buffer: Gtk.EntryBuffer, position, value, count):
        self.__seriesChanged(buffer)

    def _volumeDeletedText(self, buffer: Gtk.EntryBuffer, position, count):
        self.__volumeChanged(buffer)

    def _volumeInsertedText(self, buffer: Gtk.EntryBuffer, position, value, count):
        self.__volumeChanged(buffer)

    def _genreDeletedText(self, buffer: Gtk.EntryBuffer, position, count):
        self.__genreChanged(buffer)

    def _genreInsertedText(self, buffer: Gtk.EntryBuffer, position, value, count):
        self.__genreChanged(buffer)

    def _licenseDeletedText(self, buffer: Gtk.EntryBuffer, position, count):
        self.__licenseChanged(buffer)

    def _licenseInsertedText(self, buffer: Gtk.EntryBuffer, position, value, count):
        self.__licenseChanged(buffer)

    def _nameDeletedText(self, buffer: Gtk.EntryBuffer, position, count):
        self.__nameChanged(buffer)

    def _nameInsertedText(self, buffer: Gtk.EntryBuffer, position, value, count):
        self.__nameChanged(buffer)

    def _emailDeletedText(self, buffer: Gtk.EntryBuffer, position, count):
        self.__emailChanged(buffer)

    def _emailInsertedText(self, buffer: Gtk.EntryBuffer, position, value, count):
        self.__emailChanged(buffer)

    def show(self):
        self.widget.show_all()
