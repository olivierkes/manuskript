#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtWidgets import qApp

from manuskript.exporter.basic import basicExporter, basicFormat

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
        basicFormat("ePub", "Books that don't kill trees.", icon="application-epub+zip"),
        basicFormat("OpenDocument", "OpenDocument format. Used by LibreOffice for example.", icon="application-vnd.oasis.opendocument.text"),
        basicFormat("PDF", "Needs latex to be installed.", icon="application-pdf"),
        basicFormat("DocX", "Microsoft Office (.docx) document.", icon="application-vnd.openxmlformats-officedocument.wordprocessingml.document"),
        basicFormat("reST", icon="text-plain"),

    ]
    cmd = "pandoc"

    @classmethod
    def version(cls):
        if cls.isValid():
            r = cls.run(["-v"])
            return r.split("\n")[0]
        else:
            return ""



