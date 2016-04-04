#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtWidgets import QTextEdit

from manuskript.exporter.basic import basicExporter, basicFormat

class plainText(basicFormat):
    name = "Plain text"
    description = "Simplest export to plain text. Allows you to use your own markup not understood " \
                  "by manuskript, for example <a href='www.fountain.io'>Fountain</a>."
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