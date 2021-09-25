#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from manuskript.ui.abstractDialog import AbstractDialog


class FrequencyWindow(AbstractDialog):

    def __init__(self, mainWindow):
        AbstractDialog.__init__(self, mainWindow, "ui/frequency.glade", "frequency_window")

    def initWindow(self, builder, window):
        self.backward = builder.get_object("backward")
        self.foreward = builder.get_object("foreward")

        self.backward.connect("clicked", self._backwardClicked)

    def _backwardClicked(self, button: Gtk.Button):
        self.hide()
