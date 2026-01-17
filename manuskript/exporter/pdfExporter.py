#!/usr/bin/env python
# --!-- coding: utf8 --!--

import tempfile

from manuskript.converter import getConverter
from manuskript.data import Project
from manuskript.exporter.abstractExporter import AbstractExporter
from manuskript.exporter.latexExporter import LaTeXExporter


class PDFExporter(AbstractExporter):

    def __init__(self):
        AbstractExporter.__init__(self, "pdf")
        self.latexExporter = LaTeXExporter()

    def getName(self) -> str:
        return "PDF"

    def getMimeType(self) -> str:
        return "application/pdf"

    def getIcon(self) -> str:
        return "x-office-document"

    def exportFile(self, outputPath: str, project: Project) -> bool:
        converter = getConverter("latex", self.exportFormat)

        latex = self.latexExporter.export(project)
        latexFile = tempfile.NamedTemporaryFile(suffix=".tex")

        latexFile.write(latex.encode('utf-8'))
        latexFile.flush()

        result = converter.convertFile(
            latexFile.name,
            outputPath,
            "latex",
            self.exportFormat
        )

        latexFile.close()
        return result

    def export(self, project: Project) -> str | None:
        pdfFile = tempfile.NamedTemporaryFile(suffix=".pdf")

        if self.exportFile(pdfFile.name, project):
            data = pdfFile.read()
        else:
            data = b""

        pdfFile.close()
        return data
