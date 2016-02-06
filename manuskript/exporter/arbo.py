#!/usr/bin/env python
# --!-- coding: utf8 --!--
import os

from manuskript.functions import mainWindow


class arboExporter():
    requires = ["path"]

    def __init__(self):
        pass

    def doCompile(self, path):
        # FIXME: overwrites when items have identical names
        mw = mainWindow()
        root = mw.mdlOutline.rootItem

        def writeItem(item, path):
            if item.isFolder():
                path2 = os.path.join(path, item.title())

                try:
                    os.mkdir(path2)
                except FileExistsError:
                    pass

                for c in item.children():
                    writeItem(c, path2)

            else:
                ext = ".t2t" if item.isT2T() else \
                    ".html" if item.isHTML() else \
                        ".txt"
                path2 = os.path.join(path, item.title() + ext)
                f = open(path2, "w")
                text = self.formatText(item.text(), item.type())
                f.write(text)

        for c in root.children():
            writeItem(c, path)

    def formatText(self, text, _type):
        if _type == "t2t":
            # Empty lines for headers
            text = "\n\n\n" + text

        return text
