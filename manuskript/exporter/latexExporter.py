#!/usr/bin/env python
# --!-- coding: utf8 --!--

import tempfile

from manuskript.converter import getConverter
from manuskript.data import Project
from manuskript.exporter.abstractExporter import AbstractExporter
from manuskript.exporter.htmlExporter import HTMLExporter


class LaTeXExporter(AbstractExporter):

    def __init__(self):
        AbstractExporter.__init__(self, "latex")
        self.htmlExporter = HTMLExporter()

    def getName(self) -> str:
        return "LaTeX"
    
    def isValid(self) -> bool:
        return (AbstractExporter.isValid(self)) and (self.htmlExporter.isValid())

    def export(self, project: Project) -> str | None:
        converter = getConverter("html", self.exportFormat)

        html = self.htmlExporter.export(project)
        latex = converter.convert(html, "html", self.exportFormat)
        
        return latex
