#!/usr/bin/env python
# --!-- coding: utf8 --!--

import tempfile

from manuskript.converter import getConverter
from manuskript.data import Project, OutlineItem, OutlineFolder, OutlineText
from manuskript.exporter.abstractExporter import AbstractExporter
from manuskript.exporter.htmlExporter import HTMLExporter
from manuskript.io import formatByExtension
from manuskript.util import validString


class PDFExporter(AbstractExporter):

    def __init__(self):
        AbstractExporter.__init__(self, "pdf")
        self.htmlExporter = HTMLExporter()

    def getName(self) -> str:
        return "PDF"

    def export(self, project: Project) -> str | None:
        converter = getConverter("html", "pdf")

        html = self.htmlExporter.export(project)
        htmlFile = tempfile.NamedTemporaryFile(suffix=".html")

        htmlFile.write(html.encode('utf-8'))
        htmlFile.flush()

        pdfFile = tempfile.NamedTemporaryFile(suffix=".pdf")

        if converter.convertFile(htmlFile.name, pdfFile.name, "html", "pdf"):
            data = pdfFile.read()
        else:
            data = b""
        
        pdfFile.close()
        htmlFile.close()
        
        return data
