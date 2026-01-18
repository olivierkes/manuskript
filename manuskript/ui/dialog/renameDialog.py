#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from manuskript.ui.abstractDialog import AbstractDialog


class RenameDialog(AbstractDialog):

    def __init__(self, mainWindow, callback, closure):
        AbstractDialog.__init__(self, mainWindow, "ui/dialog/rename.glade", "rename_dialog")
        self.callback = callback
        self.closure = closure

        self.nameEntry = None

    def initWindow(self, builder, window):
        self.nameEntry = builder.get_object("name_entry")

        self.window.set_default_response(Gtk.ResponseType.OK)
        self.nameEntry.set_activates_default(True)

        self.window.connect("response", self._dialogResponse)
        self.nameEntry.connect("activate", self._nameEntryActivate)

    def _dialogResponse(self, dialog: Gtk.Dialog, response_id: int):
        if response_id == Gtk.ResponseType.OK:
            if self.callback is None:
                return

            self.callback(self.nameEntry.get_text(), self.closure)

        dialog.close()

    def _nameEntryActivate(self, entry: Gtk.Entry):
        if entry.get_text_length() <= 0:
            return

        self.window.response(Gtk.ResponseType.OK)

    def show(self, text: str|None = None):
        AbstractDialog.show(self)

        if (self.nameEntry is None) or (text is None):
            return

        self.nameEntry.set_placeholder_text(text)
        self.nameEntry.set_text(text)
        self.nameEntry.select_region(0, len(text))
