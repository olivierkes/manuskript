#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtWidgets import QTextEdit

from manuskript.exporter.basic import basicExporter, basicFormat

class markdownFormat(basicFormat):
    name = "Markdown"
    description = "A lightweigh markup language used by many tools."
    implemented = False
    requires = {
        "Settings": True,
        "PreviewBefore": True,
        "PreviewAfter": False,
    }

    @classmethod
    def settingsWidget(cls):
        sW = QTextEdit()
        return sW

class manuskriptExporter(basicExporter):

    name = "Manuskript"
    description = "Default exporter, provides basic formats used by other exporters."
    exportTo = [
        markdownFormat
    ]

    @classmethod
    def isValid(cls):
        return True