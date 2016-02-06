#!/usr/bin/env python
# --!-- coding: utf8 --!--
from manuskript.exporter.basic import basicExporter
from manuskript.functions import mainWindow


class htmlExporter(basicExporter):
    requires = ["filename"]

    def __init__(self):
        pass

    def doCompile(self, filename):
        mw = mainWindow()
        root = mw.mdlOutline.rootItem

        html = ""

        def appendItem(item):
            if item.isFolder():
                html = ""
                title = "<h{l}>{t}</h{l}>\n".format(
                        l=str(item.level() + 1),
                        t=item.title())
                html += title

                for c in item.children():
                    html += appendItem(c)

                return html

            else:
                text = self.formatText(item.text(), item.type())
                return text

        for c in root.children():
            html += appendItem(c)

        template = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        "http://www.w3.org/TR/html4/loose.dtd">
<html>
    <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8">
        <title>{TITLE}</title>
    </head>
    <body>
    {BODY}
    </body>
</html>"""

        f = open(filename, "w")
        f.write(template.format(
                TITLE="FIXME",
                BODY=html))

    def formatText(self, text, _type):

        if not text:
            return text

        if _type == "t2t":
            text = self.runT2T(text)

        elif _type == "txt":
            text = text.replace("\n", "<br>")

        elif _type == "html":
            # keep only body
            text = self.htmlBody(text)

        return text + "<br>"
