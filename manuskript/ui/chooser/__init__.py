#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version('Gdk', '3.0')

from gi.repository import GObject, Gtk

from manuskript.ui.chooser.fileFilter import FileFilter


def openFileDialog(window, fileFilter_: FileFilter = None, appendAllFilter: bool = True) -> str | None:
    dialog = Gtk.FileChooserDialog(
        "Please choose a file",
        window,
        Gtk.FileChooserAction.OPEN,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
         Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
    )

    dialog.set_default_response(Gtk.ResponseType.OK)

    if fileFilter_ is not None:
        fileFilter_.addToChooser(dialog)

        if appendAllFilter:
            FileFilter("All files").addToChooser(dialog)

    response = dialog.run()
    result = None

    if response == Gtk.ResponseType.OK:
        result = dialog.get_filename()

    dialog.destroy()
    return result


def saveFileDialog(window, fileFilter_: FileFilter = None, appendAllFilter: bool = True) -> str | None:
    dialog = Gtk.FileChooserDialog(
        "Please choose a file",
        window,
        Gtk.FileChooserAction.SAVE,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
         Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
    )

    dialog.set_default_response(Gtk.ResponseType.OK)

    if fileFilter_ is not None:
        fileFilter_.addToChooser(dialog)

        if appendAllFilter:
            FileFilter("All files").addToChooser(dialog)

    response = dialog.run()
    result = None

    if response == Gtk.ResponseType.OK:
        result = dialog.get_filename()

        if ((fileFilter_ is not None) and (fileFilter_.name == dialog.get_filter().get_name()) and
                (not result.endswith("." + fileFilter_.extension))):
            result += "." + fileFilter_.extension

    dialog.destroy()
    return result
