#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version('Gdk', '3.0')

from gi.repository import GObject, Gtk

from manuskript.ui.chooser.fileFilter import FileFilter


def openFileDialog(window, fileFilter: FileFilter = None) -> str | None:
    dialog = Gtk.FileChooserDialog(
        "Please choose a file",
        window,
        Gtk.FileChooserAction.OPEN,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
         Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
    )

    if fileFilter is not None:
        fileFilter.addToChooser(dialog)
        FileFilter("All files", "*").addToChooser(dialog)

    response = dialog.run()
    result = None

    if response == Gtk.ResponseType.OK:
        result = dialog.get_filename()

    dialog.destroy()
    return result
