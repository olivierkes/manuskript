#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from manuskript.ui.abstractDialog import AbstractDialog
from gi.repository import Gtk

class AboutDialog(AbstractDialog):

    def __init__(self, mainWindow):
        AbstractDialog.__init__(self, mainWindow, "ui/about.glade", "about_dialog")

    def initWindow(self, builder, window):
        super().initWindow(builder, window)
        self.window.connect("response", self._windowResponse)

    def _windowResponse(self, dialog, response_id):
        if response_id == Gtk.ResponseType.DELETE_EVENT:
            dialog.hide()