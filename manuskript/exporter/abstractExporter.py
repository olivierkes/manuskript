#!/usr/bin/env python
# --!-- coding: utf8 --!--

from typing import Optional

from manuskript.converter import getConverter
from manuskript.data import Project
from manuskript.io import TextFile


class AbstractExporter:
    def __init__(self, outputFormat: str) -> None:
        self.exportFormat = outputFormat

    def getName(self) -> str:
        return str(type(self))

    def getExtension(self) -> str:
        return ""

    def getMimeType(self) -> str:
        return "text/plain"

    def getIcon(self) -> str:
        return "text-x-generic"

    def isValid(self) -> bool:
        converter = getConverter("*", self.exportFormat)
        return False if converter is None else True

    def allowsPreview(self) -> bool:
        return False

    def getError(self) -> str | None:
        return None

    def exportFile(self, outputPath: str, project: Project) -> bool:
        text: Optional[str] = self.exportText(project)
        if text is None:
            return False

        textFile = TextFile(outputPath)
        textFile.save(text)
        return True

    def exportText(self, project: Project) -> str | None:
        return None

    def export(self, project: Project) -> bytes | None:
        text: Optional[str] = self.exportText(project)
        if text is None:
            return None

        return text.encode("utf-8")
