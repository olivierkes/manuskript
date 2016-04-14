#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtGui import QTextCharFormat, QFont
from PyQt5.QtWidgets import QPlainTextEdit, QGroupBox, qApp, QVBoxLayout, QCheckBox

from manuskript.exporter.manuskript.markdown import markdown as manuskriptMarkdown
from manuskript.exporter.manuskript.markdown import markdownSettings as manuskriptMarkdownSettings
from manuskript.functions import mainWindow
from manuskript.ui.editors.MMDHighlighter import MMDHighlighter
from manuskript.ui.exporters.manuskript.plainTextSettings import exporterSettings


class markdown(manuskriptMarkdown):
    name = "Markdown"
    description = qApp.translate("Export", """Export to markdown, using pandoc. Allows more formatting options
    than the basic manuskript exporter.""")

    exportVarName = "lastPandocMarkdown"

    def settingsWidget(self):
        w = markdownSettings(self)
        w.loadSettings()
        return w

    def preview(self, settingsWidget, previewWidget):
        settings = settingsWidget.getSettings()

        # Save settings
        settingsWidget.writeSettings()

        # Prepares text edit
        self.preparesTextEditViewMarkdown(previewWidget, settingsWidget.settings)
        self.preparesTextEditView(previewWidget, settings["Preview"]["PreviewFont"])

        r = self.concatenate(mainWindow().mdlOutline.rootItem, settings)
        previewWidget.setPlainText(r)


class markdownSettings(manuskriptMarkdownSettings):
    def __init__(self, _format, parent=None):
        manuskriptMarkdownSettings.__init__(self, _format, parent)

        # # Adds markdown syntax highlighter setting
        # w = self.toolBox.widget(self.toolBox.count() - 1)
        # self.grpMarkdown = QGroupBox(self.tr("Markdown"))
        # self.grpMarkdown.setLayout(QVBoxLayout())
        # self.chkMarkdownHighlighter = QCheckBox(qApp.translate("Export", "Preview with highlighter."))
        # self.grpMarkdown.layout().addWidget(self.chkMarkdownHighlighter)
        #
        # w.layout().insertWidget(w.layout().count() - 1, self.grpMarkdown)

    def updateFromSettings(self):
        manuskriptMarkdownSettings.updateFromSettings(self)

        # s = self.settings["Preview"]
        # val = s.get("MarkdownHighlighter", False)
        # self.chkMarkdownHighlighter.setChecked(val)

    def getSettings(self):
        self.settings = manuskriptMarkdownSettings.getSettings(self)
        # self.settings["Preview"]["MarkdownHighlighter"] = self.chkMarkdownHighlighter.isChecked()

        return self.settings