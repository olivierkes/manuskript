#!/usr/bin/env python
# --!-- coding: utf8 --!--

import datetime
from io import StringIO
import tempfile

from manuskript.converter import getConverter
from manuskript.data import Project, OutlineItem, OutlineFolder, OutlineText
from manuskript.exporter.abstractExporter import AbstractExporter
from manuskript.io import formatByExtension
from manuskript.util import validString


class LaTeXExporter(AbstractExporter):

    def __init__(self):
        AbstractExporter.__init__(self, "latex")

    def getName(self) -> str:
        return "LaTeX"

    def __commandFromLevel(self, level: int) -> str | None:
        commands = [
            "part",
            "chapter",
            "section",
            "subsection",
            "subsubsection",
            "paragraph",
            "subparagraph"
        ]

        if (level >= 0) and (level < len(commands)):
            return commands[level]
        else:
            return None

    def __exportItem(self, outlineItem: OutlineItem, output: StringIO, level: int = 1):
        if type(outlineItem) is OutlineFolder:
            sectionCommand = self.__commandFromLevel(level)

            if sectionCommand:
                output.write("\\" + sectionCommand + "{" + validString(outlineItem.title) + "}\n")

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

        output.write("\\documentclass{book}\n\n")
        output.write("\\title{" + validString(project.info.title) + "}\n")
        output.write("\\date{" + datetime.datetime.now().strftime("%Y-%m-%d") + "}\n")
        output.write("\\author{" + validString(project.info.author) + "}\n")

        output.write("\n\\providecommand{\\tightlist}{}\n")
        output.write("\n\\begin{document}\n\n")

        output.write("\\maketitle\n")
        output.write("\\tableofcontents\n\n")

        for outlineItem in project.outline:
            self.__exportItem(outlineItem, output, 1)

        output.write("\n\\end{document}\n")

        text = output.getvalue()
        output.close()
        return text
