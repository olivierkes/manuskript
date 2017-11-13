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


class pandocConverter(abstractConverter):

    name = "pandoc"
    cmd = "pandoc"

    @classmethod
    def isValid(self):
        if self.path() != None:
            return 2
        elif self.customPath() and os.path.exists(self.customPath):
            return 1
        else:
            return 0

    @classmethod
    def customPath(self):
        settings = QSettings()
        return settings.value("Exporters/{}_customPath".format(self.name), "")

    @classmethod
    def path(self):
        return shutil.which(self.cmd)

    @classmethod
    def convert(self, src, _from="markdown", to="html", args=None, outputfile=None):
        if not self.isValid:
            print("ERROR: pandocConverter is called but not valid.")
            return ""

        cmd = [self.runCmd()]

        cmd += ["--from={}".format(_from)]
        cmd += ["--to={}".format(to)]

        if args:
            cmd += args

        if outputfile:
            cmd.append("--output={}".format(outputfile))

        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))

        p = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if not type(src) == bytes:
            src = src.encode("utf-8")  # assumes utf-8

        stdout, stderr = p.communicate(src)

        qApp.restoreOverrideCursor()

        if stderr:
            err = stderr.decode("utf-8")
            print(err)
            QMessageBox.critical(mainWindow().dialog,
                                 qApp.translate("Export", "Error"), err)
            return None

        return stdout.decode("utf-8")

    @classmethod
    def runCmd(self):
        if self.isValid() == 2:
            return self.cmd
        elif self.isValid() == 1:
            return self.customPath
