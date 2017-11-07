#!/usr/bin/env python
# --!-- coding: utf8 --!--
import os
import shutil
import subprocess

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QWidget


class abstractImporter:
    """
    abstractImporter is used to import documents into manuskript.

    The startImport function must be subclassed. It takes a filePath (str to
    the document to import), and must return `outlineItem`s.
    """

    name = ""
    description = ""
    fileFormat = ""  # File format accepted. For example: "OPML Files (*.opml)"
                     # For folder, use "<<folder>>"
    icon = ""

    def startImport(self, filePath, settingsWidget):
        """
        Takes a str path to the file/folder to import, and the settingsWidget
        returnend by `self.settingsWidget()` containing the user set settings,
        and return `outlineItem`s.
        """
        pass

    @classmethod
    def settingsWidget(cls):
        """
        Returns a QWidget if needed for settings.
        """
        return None


