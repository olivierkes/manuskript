#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
import tempfile

gi.require_version("Gtk", "3.0")
gi.require_version("Handy", "1")
gi.require_version("WebKit2", "4.0")
from gi.repository import GLib, GObject, Gtk, Handy, WebKit2

Handy.init()

from manuskript.ui.abstractDialog import AbstractDialog

from manuskript.converter import getConverter
from manuskript.exporter import getExporterByFormat
from manuskript.data import Project, OutlineItem, OutlineFolder, OutlineText
from manuskript.io import BinaryFile


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
        self.previewButton = builder.get_object("preview_button")

        self.previewWebView = WebKit2.WebView()
        self.previewBox.pack_start(self.previewWebView, True, True, 0)
        self.previewBox.show_all()

        self.previewLeaflet.bind_property("folded", self.back, "visible",
                                          GObject.BindingFlags.SYNC_CREATE)
        self.previewLeaflet.bind_property("folded", self.forward, "visible",
                                          GObject.BindingFlags.SYNC_CREATE)
        self.previewLeaflet.bind_property("folded", self.headerBar, "show-close-button",
                                          GObject.BindingFlags.SYNC_CREATE |
                                          GObject.BindingFlags.INVERT_BOOLEAN)
        
        self.back.connect("clicked", self._backClicked)
        self.forward.connect("clicked", self._forwardClicked)
        self.previewButton.connect("clicked", self._previewButtonClicked)

    def getProject(self) -> Project:
        return self.mainWindow.getProject()

    def _backClicked(self, button: Gtk.Button):
        if self.previewLeaflet.get_visible_child_name() == "preview_box":
            self.previewLeaflet.set_visible_child_name("settings_box")
        else:
            self.hide()

    def _forwardClicked(self, button: Gtk.Button):
        if self.previewLeaflet.get_visible_child_name() == "settings_box":
            self.previewLeaflet.set_visible_child_name("preview_box")
    
    def _previewButtonClicked(self, button: Gtk.Button):
        self.preview()

    def preview(self):
        exporter = getExporterByFormat("pdf")
        project = self.getProject()

        if exporter.exportFormat == "pdf":
            pdf = b"" if exporter is None else exporter.export(project)

            self.previewWebView.load_bytes(GLib.Bytes(pdf), "application/pdf", None, None)
        elif exporter.exportFormat == "html":
            html = "" if exporter is None else exporter.export(project)

            self.previewWebView.load_html(html, None)
        else:
            text = "" if exporter is None else exporter.export(project)

            self.previewWebView.load_plain_text(text)
