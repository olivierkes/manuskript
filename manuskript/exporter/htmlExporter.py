#!/usr/bin/env python
# --!-- coding: utf8 --!--

from io import StringIO

from manuskript.converter import getConverter
from manuskript.data import Project, OutlineItem, OutlineFolder, OutlineText
from manuskript.exporter.abstractExporter import AbstractExporter
from manuskript.io import formatByExtension
from manuskript.util import validString


class HTMLExporter(AbstractExporter):

    def __init__(self):
        AbstractExporter.__init__(self, "html")

    def getName(self) -> str:
        return "HTML"

    def getMimeType(self) -> str:
        return "text/html"

    def getIcon(self) -> str:
        return "text-html"

    def __exportItem(self, outlineItem: OutlineItem, output: StringIO, level: int = 1):
        if type(outlineItem) is OutlineFolder:
            output.write("<h")
            output.write(str(level))
            output.write(">")
            output.write(validString(outlineItem.title))
            output.write("</h")
            output.write(str(level))
            output.write(">\n")

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
        output.write("<!DOCTYPE html>\n")
        output.write("<html>\n")
        output.write("<head>\n")

        output.write("<title>{0}</title>\n".format(validString(project.info.title)))

        output.write("<meta charset=\"UTF-8\" />\n")
        output.write("<meta name=\"description\" content=\"{0}\" />\n".format(validString(project.summary.sentence)))
        output.write("<meta name=\"keywords\" content=\"{0}\" />\n".format(validString(project.info.genre)))
        output.write("<meta name=\"author\" content=\"{0}\" />\n".format(validString(project.info.author)))

        output.write("</head>\n")
        output.write("<body>\n")

        for outlineItem in project.outline:
            self.__exportItem(outlineItem, output, 1)

        output.write("</body>\n")
        output.write("</html>\n")

        text = output.getvalue()
        output.close()
        return text
