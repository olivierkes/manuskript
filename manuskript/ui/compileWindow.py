#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tempfile

from gi.repository import GLib, GObject, Gtk, Handy, WebKit2

from manuskript.ui.abstractDialog import AbstractDialog

from manuskript.converter import getConverter
from manuskript.exporter import getExporters, getExporterByName
from manuskript.data import Project, OutlineItem, OutlineFolder, OutlineText
from manuskript.io import BinaryFile
from manuskript.util import validString


class CompileWindow(AbstractDialog):

    def __init__(self, mainWindow):
        AbstractDialog.__init__(self, mainWindow, "ui/compile.glade", "compile_window")

        self.headerBar = None
        self.back = None
        self.forward = None
        self.previewLeaflet = None
        self.previewBox = None
        self.previewWebView = None
        self.manageExportersButton = None
        self.previewButton = None

    def initWindow(self, builder, window):
        self.headerBar = builder.get_object("header_bar")
        self.back = builder.get_object("back")
        self.forward = builder.get_object("forward")
        self.previewLeaflet = builder.get_object("preview_leaflet")
        self.previewBox = builder.get_object("preview_box")
        self.manageExportersButton = builder.get_object("manage_exporters")
        self.fileFormatStore = builder.get_object("file_format_store")
        self.fileFormatCombobox = builder.get_object("file_format_combobox")
        self.previewButton = builder.get_object("preview_button")
        self.exportButton = builder.get_object("export_button")

        self.previewWebView = WebKit2.WebView()
        self.previewBox.pack_start(self.previewWebView, True, True, 0)
        self.previewBox.show_all()

        for exporter in getExporters():
            tree_iter = self.fileFormatStore.append()
            
            if tree_iter is None:
                continue

            self.fileFormatStore.set_value(tree_iter, 0, validString(exporter.getName()))
            self.fileFormatStore.set_value(tree_iter, 1, validString(exporter.getMimeType()))
            self.fileFormatStore.set_value(tree_iter, 2, validString(exporter.getIcon()))
        
        self.fileFormatCombobox.set_active(0)

        self.previewLeaflet.bind_property("folded", self.back, "visible",
                                          GObject.BindingFlags.SYNC_CREATE)
        self.previewLeaflet.bind_property("folded", self.forward, "visible",
                                          GObject.BindingFlags.SYNC_CREATE)
        self.previewLeaflet.bind_property("folded", self.headerBar, "show-close-button",
                                          GObject.BindingFlags.SYNC_CREATE |
                                          GObject.BindingFlags.INVERT_BOOLEAN)
        
        self.back.connect("clicked", self._backClicked)
        self.forward.connect("clicked", self._forwardClicked)
        self.fileFormatCombobox.connect("changed", self._fileFormatComboboxChanged)
        self.previewButton.connect("clicked", self._previewButtonClicked)
        self.exportButton.connect("clicked", self._exportButtonClicked)

    def getProject(self) -> Project:
        return self.mainWindow.getProject()

    def getExporter(self) -> AbstractExporter:
        tree_iter = self.fileFormatCombobox.get_active_iter()
        name = validString(self.fileFormatStore.get_value(tree_iter, 0))
        return getExporterByName(name)

    def _backClicked(self, button: Gtk.Button):
        if self.previewLeaflet.get_visible_child_name() == "preview_box":
            self.previewLeaflet.set_visible_child_name("settings_box")
        else:
            self.hide()

    def _forwardClicked(self, button: Gtk.Button):
        if self.previewLeaflet.get_visible_child_name() == "settings_box":
            self.previewLeaflet.set_visible_child_name("preview_box")

    def _fileFormatComboboxChanged(self, combobox: Gtk.ComboBox):
        self.previewButton.set_sensitive(False if self.getExporter() is None else True)

    def _previewButtonClicked(self, button: Gtk.Button):
        self.preview()

    def _exportButtonClicked(self, button: Gtk.Button):
        self.export()

    def preview(self):
        exporter = self.getExporter()
        project = self.getProject()

        if (exporter is None) or (project is None):
            return

        if exporter.exportFormat == "pdf":
            pdf = b"" if exporter is None else exporter.export(project)
            self.previewWebView.load_bytes(GLib.Bytes(pdf), exporter.getMimeType(), None, None)
        elif exporter.exportFormat == "html":
            html = "" if exporter is None else exporter.export(project)
            self.previewWebView.load_html(html, None)
        else:
            text = "" if exporter is None else exporter.export(project)
            self.previewWebView.load_plain_text(text)

    def export(self):
        exporter = self.getExporter()
        project = self.getProject()

        if (exporter is None) or (project is None):
            return
        
        dialog = Gtk.FileChooserDialog(
            title="Export project",
            parent=self.window,
            action=Gtk.FileChooserAction.SAVE,
            buttons=(
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN,
                Gtk.ResponseType.ACCEPT,
            ),
        )

        response = dialog.run()

        if response == Gtk.ResponseType.ACCEPT:
            exporter.exportFile(dialog.get_filename(), project)

        dialog.destroy()
