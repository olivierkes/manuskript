#!/usr/bin/env python
# --!-- coding: utf8 --!--

import tempfile
from typing import Optional

from manuskript.converter import getConverter
from manuskript.data import Project
from manuskript.exporter.abstractExporter import AbstractExporter
from manuskript.exporter.htmlExporter import HTMLExporter


class OdtExporter(AbstractExporter):
    def __init__(self) -> None:
        AbstractExporter.__init__(self, "odt")
        self.htmlExporter: HTMLExporter = HTMLExporter()
        self.conversionError: Optional[str] = None

    def getName(self) -> str:
        return "OpenDocument"

    def getMimeType(self) -> str:
        return "application/vnd.oasis.opendocument.text"

    def getIcon(self) -> str:
        return "application-vnd.oasis.opendocument.text"

    def getError(self) -> str | None:
        error: Optional[str] = self.htmlExporter.getError()
        if error is not None:
            return error

        return self.conversionError

    def exportFile(self, outputPath: str, project: Project) -> bool:
        converter = getConverter("html", self.exportFormat)
        if converter is None:
            return False

        html: Optional[bytes] = self.htmlExporter.export(project)
        if html is None:
            return False

        htmlFile = tempfile.NamedTemporaryFile(suffix=".html")
        htmlFile.write(html)
        htmlFile.flush()

        result = converter.convertFile(htmlFile.name, outputPath, "html", self.exportFormat)
        self.conversionError = None if result else converter.getError()

        htmlFile.close()
        return result

    def export(self, project: Project) -> bytes | None:
        odtFile = tempfile.NamedTemporaryFile(suffix=".odt")

        if self.exportFile(odtFile.name, project):
            data = odtFile.read()
        else:
            data = None

        odtFile.close()
        return data
