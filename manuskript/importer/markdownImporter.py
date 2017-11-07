#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.importer.abstractImporter import abstractImporter


class markdownImporter(abstractImporter):

    name = "Markdown"
    description = ""
    fileFormat = "Markdown files (*.md; *.txt; *)"
    icon = "text-x-markdown"
