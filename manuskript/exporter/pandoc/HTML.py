#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtWidgets import qApp
from PyQt5.QtCore import QUrl

from manuskript.exporter.manuskript import HTML as MskHTML
from manuskript.exporter.pandoc.abstractPlainText import abstractPlainText
import os


class HTML(abstractPlainText):
    name = "HTML"
    description = qApp.translate("Export", """A little known format modestly used. You know, web sites for example.""")
    icon = "text-html"

    exportVarName = "lastPandocHTML"
    toFormat = "html"
    exportFilter = "HTML files (*.html);; Any files (*)"
    requires = {
        "Settings": True,
        "Preview": True,
    }

    def previewWidget(self):
        return MskHTML.previewWidget(self)

    def preview(self, settingsWidget, previewWidget):
        settings = settingsWidget.getSettings()

        # Save settings
        settingsWidget.writeSettings()

        src = self.src(settingsWidget)

        html = self.output(settingsWidget)
        path = os.path.join(self.projectPath(), "dummy.html")
        
        self.preparesTextEditView(previewWidget.widget(0), settings["Preview"]["PreviewFont"])
        self.preparesTextEditViewMarkdown(previewWidget.widget(0), settings)
        previewWidget.widget(0).setPlainText(src)
        self.preparesTextEditView(previewWidget.widget(1), settings["Preview"]["PreviewFont"])
        previewWidget.widget(1).setPlainText(html)
        previewWidget.widget(2).setHtml(html, QUrl.fromLocalFile(path))
