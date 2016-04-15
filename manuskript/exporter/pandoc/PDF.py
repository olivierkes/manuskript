#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import QUrl
from PyQt5.QtWebKit import QWebSettings
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtWidgets import qApp

from manuskript.exporter.manuskript import HTML as MskHTML
from manuskript.exporter.pandoc.abstractOutput import abstractOutput


class PDF(abstractOutput):
    name = "PDF"
    description = qApp.translate("Export", "Needs latex to be installed.")
    icon = "application-pdf"

    exportVarName = "lastPandocPDF"
    toFormat = "pdf"
    exportFilter = "PDF files (*.pdf);; Any files (*)"
    requires = {
        "Settings": True,
        "Preview": True,
    }

    def output(self, settingsWidget, outputfile=None):
        args = settingsWidget.runnableSettings()
        args.remove("--to=pdf")
        args.append("--to=latex")
        src = self.src(settingsWidget)
        return self.exporter.convert(src, args, outputfile)

    def previewWidget(self):
        web = QWebView()
        web.settings().setAttribute(QWebSettings.PluginsEnabled, True)
        # web.show()
        return web

    def preview(self, settingsWidget, previewWidget):
        filename = "/tmp/msk_asdlhadl.pdf"
        content = self.output(settingsWidget, outputfile=filename)

        previewWidget.setUrl(QUrl("file://"+filename))