#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.converter import getConverter
from manuskript.data import Project
from manuskript.io import TextFile


class AbstractExporter:

    def __init__(self, outputFormat: str):
        self.exportFormat = outputFormat

    def getName(self) -> str:
        return str(type(self))

    def getMimeType(self) -> str:
        return "text/plain"

    def getIcon(self) -> str:
        return "text-x-generic"

    def isValid(self) -> bool:
        converter = getConverter("*", self.exportFormat)
        return False if converter is None else True

    def exportFile(self, outputPath: str, project: Project) -> bool:
        text = self.export(project)

        if text is None:
            return False

        textFile = TextFile(outputPath)
        textFile.save(text)
        return True

    def export(self, project: Project) -> str | None:
        return None
