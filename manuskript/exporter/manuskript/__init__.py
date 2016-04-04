#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtWidgets import QTextEdit

from manuskript.exporter.basic import basicExporter, basicFormat
from manuskript.exporter.manuskript.plainText import plainText


class manuskriptExporter(basicExporter):

    name = "Manuskript"
    description = "Default exporter, provides basic formats used by other exporters."
    exportTo = [
        plainText,
        basicFormat("HTML"),
        basicFormat("OPML")
    ]

    @classmethod
    def isValid(cls):
        return True