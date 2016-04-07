#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtGui import QTextCharFormat, QFont
from PyQt5.QtWidgets import QPlainTextEdit, QGroupBox, qApp, QVBoxLayout, QCheckBox

from manuskript.exporter.manuskript.plainText import plainText
from manuskript.functions import mainWindow
from manuskript.ui.editors.MMDHighlighter import MMDHighlighter
from manuskript.ui.exporters.manuskript.plainTextSettings import exporterSettings


class markdown(plainText):
    name = qApp.tr("Markdown")
    description = qApp.tr("Just like plain text, excepts adds markdown titles. \
                          Presupposes that texts are formatted in markdown.")

    @classmethod
    def settingsWidget(cls):
        w = markdownSettings(cls)
        w.loadSettings()
        return w

    @classmethod
    def preview(cls, settingsWidget, previewWidget):
        # plainText.preview(settingsWidget, previewWidget)
        # Don't know why, if I call superclass here, then concatenate does not call this processTitle function,
        # But that of of plainText.

        # ---------------------------
        # From plainText:

        settings = settingsWidget.getSettings()

        # Save settings
        settingsWidget.writeSettings()

        # ---------------------------
        # Specific to markdown

        s = settingsWidget.settings
        if s["Preview"]["MarkdownHighlighter"]:
            cls.highlighter = MMDHighlighter(previewWidget)
        else:
            cls.highlighter = None

        # ---------------------------
        # From plainText:

        r = cls.concatenate(mainWindow().mdlOutline.rootItem, settings)

        # Set preview font
        cf = QTextCharFormat()
        f = QFont()
        f.fromString(settings["Preview"]["PreviewFont"])
        cf.setFont(f)
        previewWidget.setCurrentCharFormat(cf)

        previewWidget.setPlainText(r)

    @classmethod
    def processTitle(cls, text, level, settings):
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
        self.chkMarkdownHighlighter = QCheckBox(self.tr("Preview with highlighter."))
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