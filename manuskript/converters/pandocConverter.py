#!/usr/bin/env python
# --!-- coding: utf8 --!--
import os
import shutil
import subprocess

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import qApp, QMessageBox
from PyQt5.QtGui import QCursor

from manuskript.converters import abstractConverter
from manuskript.functions import mainWindow, safeTranslate

import logging
LOGGER = logging.getLogger(__name__)

class pandocConverter(abstractConverter):

    name = "pandoc"
    cmd = "pandoc"
    @classmethod
    def isValid(cls):
        if cls.path() != None:
            return 2
        elif (path:= cls.customPath()) and os.path.exists(path):
            return 1
        else:
            return 0

    @classmethod
    def customPath(cls)->str:
        settings = QSettings()
        return settings.value("Exporters/{}_customPath".format(cls.name), "")

    @classmethod
    def path(cls):
        return shutil.which(cls.cmd)

    @classmethod
    def convert(cls, src, _from="markdown", to="html", args=None, outputfile=None):
        if not cls.isValid():
            LOGGER.error("pandocConverter is called but not valid.")
            return ""

        cmd:list[str] = [cls.runCmd()]

        cmd += ["--from={}".format(_from)]
        cmd += ["--to={}".format(to)]

        if args is not None:
            cmd += args

        if outputfile is not None:
            cmd.append("--output={}".format(outputfile))

        qApp.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))

        p = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        p.returncode

        if not type(src) == bytes:
            src = src.encode("utf-8")  # assumes utf-8

        stdout, stderr = p.communicate(src)

        qApp.restoreOverrideCursor()

        if stderr:
            err = stderr.decode("utf-8")
            LOGGER.error(err)
            QMessageBox.critical(mainWindow().dialog, safeTranslate(qApp, "Export", "Error"), err)
            return None

        return stdout.decode("utf-8")

    @classmethod
    def runCmd(cls):
        if cls.isValid() == 2:
            return cls.cmd
        elif cls.isValid() == 1:
            return cls.customPath()
        return ''
