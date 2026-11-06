#!/usr/bin/env python
# --!-- coding: utf8 --!--

import tempfile
from typing import Optional

from manuskript.converter import getConverter
from manuskript.data import Project
from manuskript.exporter.abstractExporter import AbstractExporter
from manuskript.exporter.latexExporter import LaTeXExporter


class PDFExporter(AbstractExporter):
    def __init__(self) -> None:
        AbstractExporter.__init__(self, "pdf")
        self.latexExporter: LaTeXExporter = LaTeXExporter()
        self.conversionError: Optional[str] = None

    def getName(self) -> str:
        return "PDF"

    def getMimeType(self) -> str:
        return "application/pdf"

    def getIcon(self) -> str:
        return "application-pdf"

    def allowsPreview(self) -> bool:
        return True

    def getError(self) -> str | None:
        error: Optional[str] = self.latexExporter.getError()
        if error is not None:
            return error

        return self.conversionError

    def exportFile(self, outputPath: str, project: Project) -> bool:
        converter = getConverter("latex", self.exportFormat)
        if converter is None:
            return False

        latex: Optional[bytes] = self.latexExporter.export(project)
        if latex is None:
            return False

        latexFile = tempfile.NamedTemporaryFile(suffix=".tex")
        latexFile.write(latex)
        latexFile.flush()

        result = converter.convertFile(latexFile.name, outputPath, "latex", self.exportFormat)
        self.conversionError = None if result else converter.getError()

        latexFile.close()
        return result

    def export(self, project: Project) -> bytes | None:
        pdfFile = tempfile.NamedTemporaryFile(suffix=".pdf")

        if self.exportFile(pdfFile.name, project):
            data = pdfFile.read()
        else:
            data = None

        pdfFile.close()
        return data
