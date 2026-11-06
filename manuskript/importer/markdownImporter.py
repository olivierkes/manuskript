#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os
from typing import Optional

from manuskript.converter import AbstractConverter, getConverter
from manuskript.data import Project
from manuskript.data.outline import OutlineText
from manuskript.importer.abstractImporter import AbstractImporter
from manuskript.io import TextFile


class MarkdownImporter(AbstractImporter):
    def __init__(self) -> None:
        AbstractImporter.__init__(self, "markdown")

    def getName(self) -> str:
        return "Markdown"

    def getMimeType(self) -> str:
        return "text/plain"

    def getIcon(self) -> str:
        return "text-x-markdown"

    def importFile(self, inputPath: str, project: Project) -> bool:
        textFile = TextFile(inputPath)
        text: Optional[str] = textFile.load()

        if text is None:
            return False

        name: str = os.path.basename(inputPath)
        return self.importText(project, name, text, "md")
