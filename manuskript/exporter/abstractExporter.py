#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.converter import getConverter
from manuskript.data import Project


class AbstractExporter:

    def __init__(self, outputFormat: str):
        self.exportFormat = outputFormat
    
    def getName(self) -> str:
        return str(type(self))

    def isValid(self) -> bool:
        converter = getConverter("*", self.exportFormat)
        return False if converter is None else True

    def export(self, project: Project) -> str | None:
        return None
