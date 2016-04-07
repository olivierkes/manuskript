#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtWidgets import qApp

from manuskript.exporter.basic import basicExporter, basicFormat

class HTMLFormat(basicFormat):
    name = "HTML"
    description = qApp.tr("A little known format modestly used. You know, web sites for example.")
    implemented = False
    requires = {
        "Settings": True,
        "Preview": True,
    }


class pandocExporter(basicExporter):

    name = "Pandoc"
    description = qApp.tr("""<p>A universal document convertor. Can be used to convert markdown to a wide range of other
    formats.</p>
    <p>Website: <a href="http://www.pandoc.org">http://pandoc.org/</a></p>
    """)
    exportTo = [
        HTMLFormat,
        basicFormat("ePub", "Books that don't kill trees."),
        basicFormat("OpenDocument", "OpenDocument format. Used by LibreOffice for example."),
        basicFormat("PDF", "Needs latex to be installed."),
        basicFormat("DocX", "Microsoft Office (.docx) document."),
        basicFormat("reST"),

    ]
    cmd = "pandoc"

    @classmethod
    def version(cls):
        if cls.isValid():
            r = cls.run(["-v"])
            return r.split("\n")[0]
        else:
            return ""



