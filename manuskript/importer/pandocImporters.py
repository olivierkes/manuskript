#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.importer.abstractImporter import abstractImporter
from manuskript.exporter.pandoc import pandocExporter
from manuskript.importer.opmlImporter import opmlImporter

class pandocImporter(abstractImporter):

    formatFrom = ""

    @classmethod
    def isValid(cls):
        return pandocExporter().isValid()

    @classmethod
    def startImport(cls, filePath, parentItem, settingsWidget):

        # pandoc --from=markdown filename --to=opml --standalone
        args = [
            "--from={}".format(cls.formatFrom),
            filePath,
            "--to=opml",
            "--standalone"
        ]

        r = pandocExporter().run(args)

        return opmlImporter.startImport("", parentItem,
                                        settingsWidget, fromString=r)


class markdownPandocImporter(pandocImporter):

    name = "Markdown (pandoc)"
    description = "Markdown, using pandoc"
    fileFormat = "Markdown files (*.md *.txt *)"
    icon = "text-x-markdown"
    formatFrom = "markdown"

class ePubPandocImporter(pandocImporter):

    name = "ePub (pandoc)"
    description = ""
    fileFormat = "ePub files (*.epub)"
    icon = "application-epub+zip"
    formatFrom = "epub"

class docXPandocImporter(pandocImporter):

    name = "DocX (pandoc)"
    description = ""
    fileFormat = "DocX files (*.docx)"
    icon = "application-vnd.openxmlformats-officedocument.wordprocessingml.document"
    formatFrom = "docx"

class odtPandocImporter(pandocImporter):

    name = "ODT (pandoc)"
    description = ""
    fileFormat = "Open Document files (*.odt)"
    icon = "application-vnd.oasis.opendocument.text"
    formatFrom = "odt"

class rstPandocImporter(pandocImporter):

    name = "reStructuredText (pandoc)"
    description = ""
    fileFormat = "reStructuredText files (*.rst)"
    icon = "text-plain"
    formatFrom = "rst"

class HTMLPandocImporter(pandocImporter):

    name = "HTML (pandoc)"
    description = ""
    fileFormat = "HTML files (*.htm *.html)"
    icon = "text-html"
    formatFrom = "html"

class LaTeXPandocImporter(pandocImporter):

    name = "LaTeX (pandoc)"
    description = ""
    fileFormat = "LaTeX files (*.tex)"
    icon = "text-x-tex"
    formatFrom = "latex"




