#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from io import StringIO
import tempfile
from typing import Any, Optional

from gi.repository import GLib, GObject, Gtk, Handy, WebKit2

from manuskript.converter import getConverter
from manuskript.data import OutlineFolder, OutlineItem, OutlineText, Project
from manuskript.exporter import AbstractExporter, getExporterByName, getExporters
from manuskript.io import BinaryFile
from manuskript.ui.abstractDialog import AbstractDialog
from manuskript.util import validString


class CompileWindow(AbstractDialog):
    def __init__(self, mainWindow: Any) -> None:
        AbstractDialog.__init__(self, mainWindow, "ui/compile.glade", "compile_window")

        self.idlePreview = 0

        self.headerBar: Gtk.HeaderBar = None
        self.back: Gtk.Button = None
        self.forward: Gtk.Button = None
        self.previewLeaflet: Handy.Leaflet = None
        self.previewLabel: Gtk.Label = None
        self.previewBox: Gtk.Box = None
        self.previewWebView: WebKit2.WebView = None
        self.manageExportersButton: Gtk.Button = None
        self.previewButton: Gtk.Button = None

        self.contentExpander: Gtk.Expander = None
        self.separationsExpander: Gtk.Expander = None
        self.transformationsExpander: Gtk.Expander = None
        self.previewExpander: Gtk.Expander = None

        self.expanders: list[Gtk.Expander] = []

        self.betweenFoldersCombo: Gtk.ComboBox = None
        self.betweenFoldersEntry: Gtk.Entry = None
        self.betweenTextsCombo: Gtk.ComboBox = None
        self.betweenTextsEntry: Gtk.Entry = None
        self.betweenFolderAndTextCombo: Gtk.ComboBox = None
        self.betweenFolderAndTextEntry: Gtk.Entry = None
        self.betweenTextAndFolderCombo: Gtk.ComboBox = None
        self.betweenTextAndFolderEntry: Gtk.Entry = None

    def initWindow(self, builder: Gtk.Builder, window: Any) -> None:
        self.headerBar = builder.get_object("header_bar")
        self.back = builder.get_object("back")
        self.forward = builder.get_object("forward")
        self.previewLeaflet = builder.get_object("preview_leaflet")
        self.previewLabel = builder.get_object("preview_label")
        self.previewBox = builder.get_object("preview_box")
        self.manageExportersButton = builder.get_object("manage_exporters")
        self.fileFormatStore = builder.get_object("file_format_store")
        self.fileFormatCombobox = builder.get_object("file_format_combobox")
        self.previewButton = builder.get_object("preview_button")
        self.exportButton = builder.get_object("export_button")

        self.contentExpander = builder.get_object("content_expander")
        self.separationsExpander = builder.get_object("separations_expander")
        self.transformationsExpander = builder.get_object("transformations_expander")
        self.previewExpander = builder.get_object("preview_expander")

        self.expanders = [
            self.contentExpander,
            self.separationsExpander,
            self.transformationsExpander,
            self.previewExpander
        ]

        self.betweenFoldersCombo = builder.get_object("between_folders_combo")
        self.betweenFoldersEntry = builder.get_object("between_folders_entry")
        self.betweenTextsCombo = builder.get_object("between_texts_combo")
        self.betweenTextsEntry = builder.get_object("between_texts_entry")
        self.betweenFolderAndTextCombo = builder.get_object("between_folder_and_text_combo")
        self.betweenFolderAndTextEntry = builder.get_object("between_folder_and_text_entry")
        self.betweenTextAndFolderCombo = builder.get_object("between_text_and_folder_combo")
        self.betweenTextAndFolderEntry = builder.get_object("between_text_and_folder_entry")

        self.previewWebView = WebKit2.WebView()
        self.previewBox.pack_start(self.previewWebView, True, True, 0)
        self.previewBox.show_all()

        count_exporters: int = 0
        for exporter in getExporters():
            tree_iter = self.fileFormatStore.append()
            count_exporters += 1

            if tree_iter is None:
                continue

            self.fileFormatStore.set_value(tree_iter, 0, validString(exporter.getName()))
            self.fileFormatStore.set_value(tree_iter, 1, validString(exporter.getMimeType()))
            self.fileFormatStore.set_value(tree_iter, 2, validString(exporter.getIcon()))

        self.previewLabel.set_visible(False)
        self.previewBox.set_visible(False)

        self.fileFormatCombobox.set_active(0)
        self.previewButton.set_sensitive(count_exporters > 0)
        self.exportButton.set_sensitive(count_exporters > 0)

        self.previewLeaflet.bind_property(
            "folded", self.back, "visible", GObject.BindingFlags.SYNC_CREATE
        )
        self.previewLeaflet.bind_property(
            "folded", self.forward, "visible", GObject.BindingFlags.SYNC_CREATE
        )
        self.previewLeaflet.bind_property(
            "folded",
            self.headerBar,
            "show-close-button",
            GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.INVERT_BOOLEAN,
        )

        self._idlePreview()

        self.back.connect("clicked", self._backClicked)
        self.forward.connect("clicked", self._forwardClicked)
        self.fileFormatCombobox.connect("changed", self._fileFormatComboboxChanged)
        self.previewButton.connect("clicked", self._previewButtonClicked)
        self.exportButton.connect("clicked", self._exportButtonClicked)

        for expander in self.expanders:
            expander.connect("activate", self._expanderActivated)

        self.betweenFoldersCombo.connect("changed", self._betweenFoldersChanged)
        self.betweenTextsCombo.connect("changed", self._betweenTextsChanged)
        self.betweenFolderAndTextCombo.connect("changed", self._betweenFolderAndTextChanged)
        self.betweenTextAndFolderCombo.connect("changed", self._betweenTextAndFolderChanged)

    def __completeIdlePreview(self) -> bool:
        self.idlePreview = 0
        self.preview()
        return False

    def _idlePreview(self, preview: bool = True) -> None:
        if (self.idlePreview > 0) == preview:
            return

        if (self.idlePreview > 0) and (GLib.source_remove(self.idlePreview)):
            self.idlePreview = 0
        else:
            self.idlePreview = GLib.idle_add(self.__completeIdlePreview)

    def show(self) -> None:
        AbstractDialog.show(self)
        self._idlePreview()

    def hide(self) -> None:
        AbstractDialog.hide(self)
        self._idlePreview(False)

    def getProject(self) -> Project:
        return self.mainWindow.getProject()

    def getExporter(self) -> AbstractExporter | None:
        tree_iter = self.fileFormatCombobox.get_active_iter()
        if tree_iter is None:
            return None

        name = validString(self.fileFormatStore.get_value(tree_iter, 0))
        return getExporterByName(name)

    def _backClicked(self, button: Gtk.Button) -> None:
        if self.previewLeaflet.get_visible_child_name() == "preview_box":
            self.previewLeaflet.set_visible_child_name("settings_box")
        else:
            self.hide()

    def _forwardClicked(self, button: Gtk.Button) -> None:
        if self.previewLeaflet.get_visible_child_name() == "settings_box":
            self.previewLeaflet.set_visible_child_name("preview_box")

    def _fileFormatComboboxChanged(self, combobox: Gtk.ComboBox) -> None:
        exporter: Optional[AbstractExporter] = self.getExporter()
        can_preview: bool = (exporter is not None) and (exporter.allowsPreview())

        if self.previewButton is not None:
            self.previewButton.set_sensitive(can_preview)

        self._idlePreview(can_preview)
        if can_preview:
            return

        if self.previewLabel is not None:
            self.previewLabel.set_visible(can_preview)
        if self.previewBox is not None:
            self.previewBox.set_visible(can_preview)

    def _previewButtonClicked(self, button: Gtk.Button) -> None:
        self._idlePreview(False)
        self.preview()

    def _exportButtonClicked(self, button: Gtk.Button) -> None:
        self.export()

    def _expanderActivated(self, expander: Gtk.Expander) -> None:
        for other in self.expanders:
            if other is expander:
                continue

            other.set_expanded(False)

    def _betweenFoldersChanged(self, combo: Gtk.ComboBox) -> None:
        iter: Gtk.TreeIter = combo.get_active_iter()
        model: Gtk.TreeModel = combo.get_model()

        self.betweenFoldersEntry.set_sensitive(model.get_value(iter, 1))

    def _betweenTextsChanged(self, combo: Gtk.ComboBox) -> None:
        iter: Gtk.TreeIter = combo.get_active_iter()
        model: Gtk.TreeModel = combo.get_model()

        self.betweenTextsEntry.set_sensitive(model.get_value(iter, 1))

    def _betweenFolderAndTextChanged(self, combo: Gtk.ComboBox) -> None:
        iter: Gtk.TreeIter = combo.get_active_iter()
        model: Gtk.TreeModel = combo.get_model()

        self.betweenFolderAndTextEntry.set_sensitive(model.get_value(iter, 1))

    def _betweenTextAndFolderChanged(self, combo: Gtk.ComboBox) -> None:
        iter: Gtk.TreeIter = combo.get_active_iter()
        model: Gtk.TreeModel = combo.get_model()

        self.betweenTextAndFolderEntry.set_sensitive(model.get_value(iter, 1))

    def __previewError(self, error: Optional[str]) -> None:
        text: StringIO = StringIO()
        text.write("PREVIEW_ERROR:\n\n")
        text.write("Unknown error!" if error is None else error)

        self.previewWebView.load_plain_text(text.getvalue())

    def preview(self) -> None:
        exporter: Optional[AbstractExporter] = self.getExporter()
        project: Project = self.getProject()

        if (exporter is None) or (project is None) or (not exporter.allowsPreview()):
            return

        if exporter.exportFormat == "pdf":
            pdf: Optional[bytes] = None if exporter is None else exporter.export(project)
            if (pdf is None) or (len(pdf) <= 0):
                self.__previewError(exporter.getError())
            else:
                self.previewWebView.load_bytes(GLib.Bytes(b"" if pdf is None else pdf), exporter.getMimeType(), None, None)
        elif exporter.exportFormat == "html":
            html: Optional[str] = None if exporter is None else exporter.exportText(project)
            if (html is None) or (len(html) <= 0):
                self.__previewError(exporter.getError())
            else:
                self.previewWebView.load_html(validString(html), None)
        else:
            text: Optional[str] = None if exporter is None else exporter.exportText(project)
            if text is None:
                self.__previewError(exporter.getError())
            else:
                self.previewWebView.load_plain_text(validString(text))

        if self.previewLabel is not None:
            self.previewLabel.set_visible(True)
        if self.previewBox is not None:
            self.previewBox.set_visible(True)

    def export(self) -> None:
        exporter = self.getExporter()
        project = self.getProject()

        if (exporter is None) or (project is None):
            return

        filter: Gtk.FileFilter = Gtk.FileFilter()
        filter.set_name(exporter.getName())
        filter.add_mime_type(exporter.getMimeType())

        dialog = Gtk.FileChooserDialog(
            title="Export project",
            parent=self.window,
            action=Gtk.FileChooserAction.SAVE,
            buttons=(
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE_AS,
                Gtk.ResponseType.ACCEPT,
            ),
        )

        filename: StringIO = StringIO()
        filename.write(project.getName())
        filename.write(exporter.getExtension())

        dialog.set_current_name(filename.getvalue())
        dialog.set_create_folders(True)
        dialog.add_filter(filter)

        response = dialog.run()

        if response == Gtk.ResponseType.ACCEPT:
            exporter.exportFile(dialog.get_filename(), project)

        dialog.destroy()
