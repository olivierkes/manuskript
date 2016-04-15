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
from manuskript.exporter.pandoc.plainText import reST, markdown, latex
from manuskript.functions import mainWindow


class pandocExporter(basicExporter):

    name = "Pandoc"
    description = qApp.translate("Export", """<p>A universal document convertor. Can be used to convert markdown to a wide range of other
    formats.</p>
    <p>Website: <a href="http://www.pandoc.org">http://pandoc.org/</a></p>
    """)
    cmd = "pandoc"

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

        ]

    def version(self):
        if self.isValid():
            r = self.run(["-v"])
            return r.split("\n")[0]
        else:
            return ""

    def convert(self, src, args, outputfile=None):
        args = [self.cmd] + args

        if outputfile:
            args.append("--output={}".format(outputfile))

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

        if stderr:
            err = stderr.decode("utf-8")
            print(err)
            QMessageBox.critical(mainWindow().dialog, qApp.translate("Export", "Error"), err)
            return None

        return stdout.decode("utf-8")

