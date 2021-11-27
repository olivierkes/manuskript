#!/usr/bin/env python
# --!-- coding: utf8 --!--
import subprocess

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import qApp, QMessageBox

from manuskript.exporter.basic import basicExporter, basicFormat
from manuskript.exporter.pandoc.HTML import HTML
from manuskript.exporter.pandoc.PDF import PDF
from manuskript.exporter.pandoc.outputFormats import ePub, OpenDocument, DocX
from manuskript.exporter.pandoc.plainText import reST, markdown, latex, OPML
from manuskript.functions import mainWindow

import logging
LOGGER = logging.getLogger(__name__)

class pandocExporter(basicExporter):

    name = "Pandoc"
    description = qApp.translate("Export", """<p>A universal document converter. Can be used to convert Markdown to a wide range of other
    formats.</p>
    <p>Website: <a href="http://www.pandoc.org">http://pandoc.org/</a></p>
    """)
    cmd = "pandoc"
    absentTip = "Install pandoc to benefit from a wide range of export formats (DocX, ePub, PDF, etc.)"
    absentURL = "http://pandoc.org/installing.html"

    def __init__(self):
        basicExporter.__init__(self)

        self.exportTo = [
            markdown(self),
            latex(self),
            HTML(self),
            ePub(self),
            OpenDocument(self),
            DocX(self),
            PDF(self),
            reST(self),
            OPML(self),
        ]

    def version(self):
        if self.isValid():
            r = self.run(["--version"])
            return r.split("\n")[0]
        else:
            return ""

    def convert(self, src, args, outputfile=None):
        if self.isValid() == 2:
            run = self.cmd
        elif self.isValid() == 1:
            run = self.customPath
        else:
            LOGGER.error("No command for pandoc.")
            return None
        args = [run] + args

        if outputfile:
            args.append("--output={}".format(outputfile))

        for name, col, var in [
            ("Title", 0, "title"),
            ("Subtitle", 1, "subtitle"),
            ("Serie", 2, ""),
            ("Volume", 3, ""),
            ("Genre", 4, ""),
            ("License", 5, ""),
            ("Author", 6, "author"),
            ("Email", 7, ""),
            ]:
            item = mainWindow().mdlFlatData.item(0, col)
            if var and item and item.text().strip():
                args.append("--variable={}:{}".format(var, item.text().strip()))

        # Add title metadata required for pandoc >= 2.x
        title = "Untitled"
        if mainWindow().mdlFlatData.item(0, 0):
            title = mainWindow().mdlFlatData.item(0, 0).text().strip()
        args.append("--metadata=title:{}".format(title))

        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))

        p = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if not type(src) == bytes:
            src = src.encode("utf-8")  # assumes utf-8

        stdout, stderr = p.communicate(src)

        qApp.restoreOverrideCursor()

        if stderr or p.returncode != 0:
            err_type = "ERROR" if p.returncode != 0 else "WARNING"
            err = "%s on export\n" % err_type \
                + "Return code: %d\n" % p.returncode \
                + "Command and parameters:\n%s\n" % p.args \
                + "Stderr content:\n" + stderr.decode("utf-8")
            if p.returncode != 0:
                LOGGER.error(err)
                QMessageBox.critical(mainWindow().dialog, qApp.translate("Export", "Error"), err)
            else:
                LOGGER.warning(err)
            return None

        return stdout.decode("utf-8")

