#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtWidgets import qApp

from manuskript.exporter.pandoc.abstractPlainText import abstractPlainText


class markdown(abstractPlainText):
    name = "Markdown"
    description = qApp.translate("Export", """Export to markdown, using pandoc. Allows more formatting options
    than the basic manuskript exporter.""")
    icon = "text-x-markdown"

    exportVarName = "lastPandocMarkdown"
    toFormat = "markdown"
    exportFilter = "Markdown files (*.md);; Any files (*)"


class reST(abstractPlainText):
    name = "reST"
    description = qApp.translate("Export", """reStructuredText is a lightweight markup language...""")

    exportVarName = "lastPandocreST"
    toFormat = "rst"
    icon = "text-plain"
    exportFilter = "reST files (*.rst);; Any files (*)"


class latex(abstractPlainText):
    name = "LaTeX"
    description = qApp.translate("Export", """LaTeX is a word processor and document markup language used to create
                                              beautiful documents.""")

    exportVarName = "lastPandocLatex"
    toFormat = "latex"
    icon = "text-x-tex"
    exportFilter = "Tex files (*.tex);; Any files (*)"


class OPML(abstractPlainText):
    name = "OPML"
    description = qApp.translate("Export", """The purpose of this format is to provide a way to exchange information
                                              between outliners and Internet services that can be browsed or controlled
                                              through an outliner.""")

    exportVarName = "lastPandocOPML"
    toFormat = "opml"
    icon = "text-x-opml+xml"
    exportFilter = "OPML files (*.opml);; Any files (*)"


