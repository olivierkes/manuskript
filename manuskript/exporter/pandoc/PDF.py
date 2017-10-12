#!/usr/bin/env python
# --!-- coding: utf8 --!--
import random
import shutil

from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import qApp

from manuskript.exporter.pandoc.abstractOutput import abstractOutput
from manuskript.functions import tempFile
from manuskript.ui.views.PDFViewer import PDFViewer


class PDF(abstractOutput):
    """PDF Viewer using PDS.js. Cf. https://github.com/mozilla/pdf.js/wiki/Setup-PDF.js-in-a-website"""

    name = "PDF"
    description = qApp.translate("Export", "Needs latex to be installed.")
    InvalidBecause = qApp.translate("Export", """a valid latex installation. See pandoc recommendations on:
                     <a href="http://pandoc.org/installing.html">http://pandoc.org/installing.html</a>. If you want unicode support, you need xelatex.""")
    icon = "application-pdf"

    exportVarName = "lastPandocPDF"
    toFormat = "pdf"
    exportFilter = "PDF files (*.pdf);; Any files (*)"
    requires = {
        "Settings": True,
        "Preview": True,
    }

    def isValid(self):
        path = shutil.which("pdflatex") or shutil.which("xelatex")
        return path is not None

    def output(self, settingsWidget, outputfile=None):
        args = settingsWidget.runnableSettings()
        args.remove("--to=pdf")
        args.append("--to=latex")
        src = self.src(settingsWidget)
        return self.exporter.convert(src, args, outputfile)

    def previewWidget(self):
        return PDFViewer()

    def preview(self, settingsWidget, previewWidget):
        filename = tempFile("msk_pdfpreview.pdf")

        settingsWidget.writeSettings()
        content = self.output(settingsWidget, outputfile=filename)

        previewWidget.loadPDF(filename)
