#!/usr/bin/env python
# --!-- coding: utf8 --!--

from io import StringIO

from manuskript.converter import getConverter
from manuskript.data import Project, OutlineItem, OutlineFolder, OutlineText
from manuskript.exporter.abstractExporter import AbstractExporter
from manuskript.io import formatByExtension
from manuskript.util import validString


class MarkdownExporter(AbstractExporter):

    def __init__(self):
        AbstractExporter.__init__(self, "markdown")

    def getName(self) -> str:
        return "Markdown"

    def __exportItem(self, outlineItem: OutlineItem, output: StringIO, level: int = 1):
        if type(outlineItem) is OutlineFolder:
            output.write("#" * level)
            output.write(" ")
            output.write(validString(outlineItem.title))
            output.write("\n\n")

            for item in outlineItem:
                self.__exportItem(item, output, level + 1)
                output.write("\n")
        elif type(outlineItem) is OutlineText:
            inputFormat = formatByExtension(outlineItem.type)
            converter = getConverter(inputFormat, self.exportFormat)

            if converter:
                text = converter.convert(outlineItem.text, inputFormat, self.exportFormat)
            else:
                text = None

            output.write(validString(text))
            output.write("\n")

    def export(self, project: Project) -> str | None:
        output = StringIO()

        output.write("# ")
        output.write(validString(project.info.title))
        output.write("\n\n")

        for outlineItem in project.outline:
            self.__exportItem(outlineItem, output, 2)
        
        text = output.getvalue()
        output.close()
        return text
