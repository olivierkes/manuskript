#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtGui import QTextCharFormat, QFont
from PyQt5.QtWidgets import QPlainTextEdit, QGroupBox, qApp, QVBoxLayout, QCheckBox

from manuskript.exporter.manuskript.plainText import plainText
from manuskript.functions import mainWindow
from manuskript.ui.editors.MMDHighlighter import MMDHighlighter
from manuskript.ui.exporters.manuskript.plainTextSettings import exporterSettings


class markdown(plainText):
    name = "Markdown"
    description = qApp.translate("Export", """Just like plain text, excepts adds markdown titles.
                          Presupposes that texts are formatted in markdown.""")

    exportVarName = "lastManuskriptMarkdown"
    exportFilter = "Markdown files (*.md);; Any files (*)"
    icon = "text-x-markdown"

    def settingsWidget(self):
        w = markdownSettings(self)
        w.loadSettings()
        return w

    def preparesTextEditViewMarkdown(self, view, settings):
        if settings["Preview"]["MarkdownHighlighter"]:
            self.highlighter = MMDHighlighter(view)
        else:
            self.highlighter = None

    def preview(self, settingsWidget, previewWidget):
        settings = settingsWidget.getSettings()

        # Save settings
        settingsWidget.writeSettings()

        # Prepares text edit
        self.preparesTextEditViewMarkdown(previewWidget, settingsWidget.settings)
        self.preparesTextEditView(previewWidget, settings["Preview"]["PreviewFont"])

        previewWidget.setPlainText(self.output(settingsWidget))

    def processTitle(self, text, level, settings):
        return "{} {}\n".format(
            "#" * (level + 1),
            text
        )


class markdownSettings(exporterSettings):
    def __init__(self, _format, parent=None):
        exporterSettings.__init__(self, _format, parent)

        # Adds markdown syntax highlighter setting
        w = self.toolBox.widget(self.toolBox.count() - 1)
        self.grpMarkdown = QGroupBox(self.tr("Markdown"))
        self.grpMarkdown.setLayout(QVBoxLayout())
        self.chkMarkdownHighlighter = QCheckBox(qApp.translate("Export", "Preview with highlighter."))
        self.grpMarkdown.layout().addWidget(self.chkMarkdownHighlighter)

        w.layout().insertWidget(w.layout().count() - 1, self.grpMarkdown)

    def updateFromSettings(self):
        exporterSettings.updateFromSettings(self)

        s = self.settings["Preview"]
        val = s.get("MarkdownHighlighter", False)
        self.chkMarkdownHighlighter.setChecked(val)

    def getSettings(self):
        self.settings = exporterSettings.getSettings(self)
        self.settings["Preview"]["MarkdownHighlighter"] = self.chkMarkdownHighlighter.isChecked()

        return self.settings