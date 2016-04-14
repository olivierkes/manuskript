#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtWidgets import qApp

from manuskript.exporter.basic import basicExporter, basicFormat
from manuskript.exporter.pandoc.markdown import markdown


class HTMLFormat(basicFormat):
    name = "HTML"
    description = qApp.translate("Export", "A little known format modestly used. You know, web sites for example.")
    implemented = False
    requires = {
        "Settings": True,
        "Preview": True,
    }
    icon="text-html"


class pandocExporter(basicExporter):

    name = "Pandoc"
    description = qApp.translate("Export", """<p>A universal document convertor. Can be used to convert markdown to a wide range of other
    formats.</p>
    <p>Website: <a href="http://www.pandoc.org">http://pandoc.org/</a></p>
    """)
    exportTo = [
        HTMLFormat,
        markdown,
        basicFormat("ePub", "Books that don't kill trees.", icon="application-epub+zip"),
        basicFormat("OpenDocument", "OpenDocument format. Used by LibreOffice for example.", icon="application-vnd.oasis.opendocument.text"),
        basicFormat("PDF", "Needs latex to be installed.", icon="application-pdf"),
        basicFormat("DocX", "Microsoft Office (.docx) document.", icon="application-vnd.openxmlformats-officedocument.wordprocessingml.document"),
        basicFormat("reST", icon="text-plain"),

    ]
    cmd = "pandoc"

    def __init__(self):
        basicExporter.__init__(self)

    def version(self):
        if self.isValid():
            r = self.run(["-v"])
            return r.split("\n")[0]
        else:
            return ""



