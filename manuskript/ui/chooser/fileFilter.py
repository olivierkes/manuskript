#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version('Gdk', '3.0')

from gi.repository import GObject, Gtk


class FileFilter:

    def __init__(self, name: str, pattern: str):
        self.name = name
        self.pattern = pattern

    def addToChooser(self, chooser: Gtk.FileChooser):
        fileFilter = Gtk.FileFilter()
        fileFilter.set_name(self.name)
        fileFilter.add_pattern(self.pattern)

        chooser.add_filter(fileFilter)
