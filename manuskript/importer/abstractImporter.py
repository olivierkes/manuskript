#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os
from typing import Optional

from manuskript.converter import AbstractConverter, getConverter
from manuskript.data import Project
from manuskript.data.outline import OutlineText
from manuskript.io import TextFile


class AbstractImporter:
    def __init__(self, inputFormat: str) -> None:
        self.importFormat = inputFormat

    def getName(self) -> str:
        return str(type(self))

    def getMimeType(self) -> str:
        return "text/plain"

    def getIcon(self) -> str:
        return "text-x-generic"

    def isValid(self) -> bool:
        converter: Optional[AbstractConverter] = getConverter(self.importFormat, "*")
        return False if converter is None else True

    def getError(self) -> str | None:
        return None

    def importFile(self, inputPath: str, project: Project) -> bool:
        textFile = TextFile(inputPath)
        text: Optional[str] = textFile.load()

        if text is None:
            return False

        name: str = os.path.basename(inputPath)
        return self.importText(project, name, text)

    def importText(self, project: Project, name: str, text: str, textFormat: str = "txt") -> bool:
        outline_text: OutlineText = project.outline.addText(name)
        converter: Optional[AbstractConverter] = getConverter(self.importFormat, outline_text.type)
        content: Optional[str] = None

        if converter is not None:
            content = converter.convert(text, textFormat, outline_text.type)

        if content is None:
            project.outline.removeItem(outline_text)
            return False

        outline_text.text = content
        return True
