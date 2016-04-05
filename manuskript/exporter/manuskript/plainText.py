#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtWidgets import QPlainTextEdit

from manuskript.exporter.basic import basicExporter, basicFormat
from manuskript.functions import mainWindow
from manuskript.models.outlineModel import outlineItem
from manuskript.ui.exporters.exporterSettings import exporterSettings


class plainText(basicFormat):
    name = "Plain text"
    description = "Simplest export to plain text. Allows you to use your own markup not understood " \
                  "by manuskript, for example <a href='www.fountain.io'>Fountain</a>."
    implemented = True
    requires = {
        "Settings": True,
        "Preview": True,
    }

    @classmethod
    def settingsWidget(cls):
        w = exporterSettings()
        return w

    @classmethod
    def previewWidget(cls):
        w = QPlainTextEdit()
        w.setReadOnly(True)
        return w

    @classmethod
    def preview(cls, settingsWidget, previewWidget):
        previewWidget.setPlainText(cls.concatenate(mainWindow().mdlOutline.rootItem))

    @classmethod
    def concatenate(cls, item: outlineItem,
                    processTitle=lambda x: x + "\n",
                    processText=lambda x: x + "\n",
                    processContent=lambda x: x + "\n",
                    textSep="", folderSep="", textFolderSep="", folderTextSep="") -> str:

        r = ""

        if not item.compile():
            return ""

        if item.level() >= 0:  # item is not root

            # Adds item title
            r += processTitle(item.title())

            # Adds item text
            r += processText(item.text())

        content = ""

        # Add item children
        last = None
        for c in item.children():

            # Separator
            if last:
                # Between folder
                if last == c.type() == "folder":
                    content += folderSep
                elif last == c.type() == "md":
                    content += textSep
                elif last == "folder" and c.type() == "md":
                    content += folderTextSep
                elif last == "md" and c.type() == "folder":
                    content += textFolderSep

            content += cls.concatenate(c)

            last = c.type()

        r += processContent(content)

        return r