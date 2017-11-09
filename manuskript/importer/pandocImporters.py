#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.importer.abstractImporter import abstractImporter
from manuskript.exporter.pandoc import pandocExporter
from manuskript.importer.opmlImporter import opmlImporter
from manuskript.importer.markdownImporter import markdownImporter
from PyQt5.QtWidgets import qApp


class pandocImporter(abstractImporter):

    formatFrom = ""
    engine = "Pandoc"
    extraArgs = []

    @classmethod
    def isValid(cls):
        return pandocExporter().isValid()

    def startImport(self, filePath, parentItem, settingsWidget):

        formatTo = self.getSetting("formatTo").value().lower()
        wrap = self.getSetting("wrap").value().lower()

        # pandoc --from=markdown filename --to=opml --standalone
        args = [
            "--from={}".format(self.formatFrom),
            filePath,
            "--to={}".format(formatTo),
            "--wrap={}".format(wrap),
        ]

        if formatTo == "opml":
            args.append("--standalone")

        args += self.extraArgs

        r = pandocExporter().run(args)

        if formatTo == "opml":
            return self.opmlImporter.startImport("", parentItem,
                                            settingsWidget, fromString=r)
        elif formatTo == "markdown":
            return self.mdImporter.startImport(filePath, parentItem,
                                                settingsWidget, fromString=r)

    def settingsWidget(self, widget):
        """
        Takes a QWidget that can be modified and must be returned.
        """

        # Add group
        group = self.addGroup(widget.toolBox.widget(0),
                              qApp.translate("Import", "Pandoc import"))

        self.addSetting("info", "label",
                        qApp.translate("Import", """<b>Info:</b> Manuskript can
                        import from <b>markdown</b> or <b>OPML</b>. Pandoc will
                        convert your document to either (see option below), and
                        then it will be imported in manuskript. One or the other
                        might give better result depending on your document.
                        <br/>&nbsp;"""))

        self.addSetting("formatTo", "combo",
                        qApp.translate("Import", "Import using:"),
                        vals="markdown|OPML")

        self.addSetting("wrap", "combo",
                        qApp.translate("Import", "Wrap lines:"),
                        vals="auto|none|preserve",
                        default="none",
                        tooltip=qApp.translate("Import", """<p>Should pandoc create
                        cosmetic / non-semantic line-breaks?</p><p>
                        <b>auto</b>: wraps at 72 characters.<br>
                        <b>none</b>: no line wrap.<br>
                        <b>preserve</b>: tries to preserves line wrap from the
                        original document.</p>"""))

        for s in self.settings:
            self.settings[s].widget(group)

        self.mdImporter = markdownImporter()
        widget = self.mdImporter.settingsWidget(widget)
        self.opmlImporter = opmlImporter()
        widget = self.opmlImporter.settingsWidget(widget)

        return widget


class markdownPandocImporter(pandocImporter):

    name = "Markdown"
    description = "Markdown, using pandoc"
    fileFormat = "Markdown files (*.md *.txt *)"
    icon = "text-x-markdown"
    formatFrom = "markdown"

class ePubPandocImporter(pandocImporter):

    name = "ePub"
    description = ""
    fileFormat = "ePub files (*.epub)"
    icon = "application-epub+zip"
    formatFrom = "epub"

class docXPandocImporter(pandocImporter):

    name = "DocX"
    description = ""
    fileFormat = "DocX files (*.docx)"
    icon = "application-vnd.openxmlformats-officedocument.wordprocessingml.document"
    formatFrom = "docx"

class odtPandocImporter(pandocImporter):

    name = "ODT"
    description = ""
    fileFormat = "Open Document files (*.odt)"
    icon = "application-vnd.oasis.opendocument.text"
    formatFrom = "odt"

class rstPandocImporter(pandocImporter):

    name = "reStructuredText"
    description = ""
    fileFormat = "reStructuredText files (*.rst)"
    icon = "text-plain"
    formatFrom = "rst"

class HTMLPandocImporter(pandocImporter):

    name = "HTML"
    description = ""
    fileFormat = "HTML files (*.htm *.html)"
    icon = "text-html"
    formatFrom = "html"

class LaTeXPandocImporter(pandocImporter):

    name = "LaTeX"
    description = ""
    fileFormat = "LaTeX files (*.tex)"
    icon = "text-x-tex"
    formatFrom = "latex"

class OPMLPandocImporter(pandocImporter):

    name = "OPML"
    description = ""
    fileFormat = "OPML files (*.opml *.xml)"
    icon = "text-x-opml+xml"
    formatFrom = "opml"



