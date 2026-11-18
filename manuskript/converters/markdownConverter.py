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

import logging
LOGGER = logging.getLogger(__name__)
from manuskript import MD

# try:
#     from manuskript import MD
# except ImportError:
#     MD = None


class markdownConverter(abstractConverter):
    """
    Converter using python module markdown.
    """

    name = "python module markdown"

    @classmethod
    def isValid(cls):
        return MD.isValid

    @classmethod
    def convert(cls, markdown):
        if not MD.isValid:
            LOGGER.error("markdownConverter is called but not valid.")
        html = MD.markdown(markdown)
        return html
