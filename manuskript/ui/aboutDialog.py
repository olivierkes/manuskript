#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk

from manuskript.ui.abstractDialog import AbstractDialog


class AboutDialog(AbstractDialog):
    def __init__(self, mainWindow: Gtk.Window) -> None:
        AbstractDialog.__init__(self, mainWindow, "ui/about.glade", "about_dialog")

    def initWindow(self, builder: Gtk.Builder, window: Gtk.Dialog) -> None:
        super().initWindow(builder, window)
        self.window.connect("response", self._windowResponse)

    def _windowResponse(self, dialog: Gtk.Dialog, responseId: Gtk.ResponseType) -> None:
        if responseId == Gtk.ResponseType.DELETE_EVENT:
            dialog.hide()
