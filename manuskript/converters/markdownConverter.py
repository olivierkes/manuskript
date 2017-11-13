#!/usr/bin/env python
# --!-- coding: utf8 --!--
import os
import shutil
import subprocess

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import qApp, QMessageBox
from PyQt5.QtGui import QCursor

from manuskript.converters import abstractConverter
from manuskript.functions import mainWindow

try:
    import markdown as MD
except ImportError:
    MD = None


class markdownConverter(abstractConverter):
    """
    Converter using python module markdown.
    """

    name = "python module markdown"

    @classmethod
    def isValid(self):
        return MD is not None

    @classmethod
    def convert(self, markdown):
        if not self.isValid:
            print("ERROR: markdownConverter is called but not valid.")
            return ""

        html = MD.markdown(markdown)
        return html
