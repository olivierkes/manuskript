#!/usr/bin/env python
# --!-- coding: utf8 --!--
import os
import shutil
import subprocess

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QCursor
from manuskript.qt_compat import qApp

from manuskript.converters import abstractConverter
from manuskript.functions import mainWindow

import logging
LOGGER = logging.getLogger(__name__)

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
        return MD != None

    @classmethod
    def convert(self, markdown):
        if not self.isValid:
            LOGGER.error("markdownConverter is called but not valid.")
            return ""

        html = MD.markdown(markdown)
        return html
