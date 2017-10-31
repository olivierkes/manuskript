#!/usr/bin/env python
# --!-- coding: utf8 --!--
from manuskript.exporter.pandoc.abstractPlainText import abstractPlainText


class abstractOutput(abstractPlainText):
    name = "SUBCLASSME"
    description = "SUBCLASSME"
    exportVarName = "SUBCLASSME"
    toFormat = "SUBCLASSME"
    icon = "SUBCLASSME"
    exportFilter = "SUBCLASSME"
    requires = {
        "Settings": True,
        "Preview": False,
    }

    def export(self, settingsWidget):
        filename = self.getExportFilename(settingsWidget)
        settingsWidget.writeSettings()
        if filename:
            content = self.output(settingsWidget, outputfile=filename)

