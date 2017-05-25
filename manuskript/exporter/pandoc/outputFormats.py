#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtWidgets import qApp

from manuskript.exporter.pandoc.abstractOutput import abstractOutput


class ePub(abstractOutput):
    name = "ePub"
    description = qApp.translate("Export", """Books that don't kill trees.""")
    icon = "application-epub+zip"

    exportVarName = "lastPandocePub"
    toFormat = "epub"
    exportFilter = "ePub files (*.epub);; Any files (*)"


class OpenDocument(abstractOutput):
    name = "OpenDocument"
    description = qApp.translate("Export", "OpenDocument format. Used by LibreOffice for example.")

    exportVarName = "lastPandocODT"
    toFormat = "odt"
    icon = "application-vnd.oasis.opendocument.text"
    exportFilter = "OpenDocument files (*.odt);; Any files (*)"


class DocX(abstractOutput):
    name = "DocX"
    description = qApp.translate("Export", "Microsoft Office (.docx) document.")

    exportVarName = "lastPandocDocX"
    toFormat = "docx"
    icon = "application-vnd.openxmlformats-officedocument.wordprocessingml.document"
    exportFilter = "DocX files (*.docx);; Any files (*)"

