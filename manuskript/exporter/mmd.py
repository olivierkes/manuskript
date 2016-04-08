#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtWidgets import qApp

from manuskript.exporter.basic import basicExporter, basicFormat


class mmdExporter(basicExporter):

    name = "MultiMarkdown"
    description = qApp.translate("Export", """<p>A superset of markdown.</p>
    <p>Website: <a href="http://fletcherpenney.net/multimarkdown/">http://fletcherpenney.net/multimarkdown/</a></p>
    """)
    exportTo = [
        basicFormat("HTML", "A little known format modestly used. You know, web sites for example.", "text-html"),
        basicFormat("latex", "", "text-x-tex"),
        basicFormat("Flat XML", "", "text-xml"),
        basicFormat("ePub", "Books that don't kill trees.", icon="application-epub+zip"),
    ]
    cmd = "mmd"

    @classmethod
    def version(cls):
        if cls.isValid():
            r = cls.run(["-v"])
            return r.split("\n")[1]
        else:
            return ""

