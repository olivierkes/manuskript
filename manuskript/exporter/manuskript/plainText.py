#!/usr/bin/env python
# --!-- coding: utf8 --!--
import re
from PyQt5.QtGui import QFont, QTextCharFormat
from PyQt5.QtWidgets import QPlainTextEdit, qApp, QFrame, QFileDialog, QMessageBox

from manuskript.exporter.basic import basicFormat
from manuskript.functions import mainWindow, getSaveFileNameWithSuffix
from manuskript.models import outlineItem
from manuskript.ui.exporters.manuskript.plainTextSettings import exporterSettings
import codecs

import logging
LOGGER = logging.getLogger(__name__)

class plainText(basicFormat):
    name = qApp.translate("Export", "Plain text")
    description = qApp.translate("Export", """Simplest export to plain text. Allows you to use your own markup not understood
                  by Manuskript, for example <a href='www.fountain.io'>Fountain</a>.""")
    implemented = True
    requires = {
        "Settings": True,
        "Preview": True,
    }
    icon = "text-plain"

    # Default settings used in self.getExportFilename. For easy subclassing when exporting plaintext.
    exportVarName = "lastPlainText"
    exportFilter = "Text files (*.txt);; Any files (*)"
    exportDefaultSuffix = ".txt"  # qt ignores the period, but it is clearer in our code to have it

    def __init__(self):
        pass

    def settingsWidget(self):
        w = exporterSettings(self)
        w.loadSettings()
        return w

    def previewWidget(self):
        w = QPlainTextEdit()
        w.setFrameShape(QFrame.NoFrame)
        w.setReadOnly(True)
        return w

    def output(self, settingsWidget):
        settings = settingsWidget.getSettings()
        try:
            return self.concatenate(mainWindow().mdlOutline.rootItem, settings)
        except re.error as e:
            QMessageBox.warning(mainWindow().dialog, qApp.translate("Export", "Error"),
                                qApp.translate("Export", "Could not process regular expression: \n{}").format(str(e)))
            return ""

    def getExportFilename(self, settingsWidget, varName=None, filter=None):

        if varName == None:
            varName = self.exportVarName

        if filter == None:
            filter = self.exportFilter

        settings = settingsWidget.getSettings()

        s = settings.get("Output", {})
        if varName in s:
            filename = s[varName]
        else:
            filename = ""

        filename, filter = getSaveFileNameWithSuffix(settingsWidget.parent(),
                                                     caption=qApp.translate("Export", "Choose output file…"),
                                                     filter=filter,
                                                     directory=filename,
                                                     defaultSuffix=self.exportDefaultSuffix)

        if filename:
            s[varName] = filename
            settingsWidget.settings["Output"] = s

            # Save settings
            settingsWidget.writeSettings()

        return filename

    def export(self, settingsWidget):
        settings = settingsWidget.getSettings()

        filename = self.getExportFilename(settingsWidget)

        if filename:
            settingsWidget.writeSettings()
            content = self.output(settingsWidget)

            if not content:
                LOGGER.error("No content. Nothing saved.")
                return

            with open(filename, "w", encoding='utf8') as f:
                f.write(content)

    def preview(self, settingsWidget, previewWidget):
        settings = settingsWidget.getSettings()

        # Save settings
        settingsWidget.writeSettings()

        r = self.output(settingsWidget)

        # Set preview font
        self.preparesTextEditView(previewWidget, settings["Preview"]["PreviewFont"])

        previewWidget.setPlainText(r)

    def preparesTextEditView(self, view, textFont):
        cf = QTextCharFormat()
        f = QFont()
        f.fromString(textFont)
        cf.setFont(f)
        view.setCurrentCharFormat(cf)

    def concatenate(self, item: outlineItem, settings) -> str:
        s = settings
        r = ""

        # Do we include item
        if not item.compile() or s["Content"]["IgnoreCompile"]:
            return ""

        # What do we include
        l = item.level()
        if l >= 0:  # item is not root

            if item.isFolder():
                if not s["Content"]["More"] and s["Content"]["FolderTitle"] or\
                       s["Content"]["More"] and s["Content"]["FolderTitle"][l]:

                    r += self.processTitle(item.title(), l, settings)

            elif item.isText():
                if not s["Content"]["More"] and s["Content"]["TextTitle"] or \
                       s["Content"]["More"] and s["Content"]["TextTitle"][l]:

                    r += self.processTitle(item.title(), l, settings)

                if not s["Content"]["More"] and s["Content"]["TextText"] or \
                       s["Content"]["More"] and s["Content"]["TextText"][l]:

                    r += self.processText(item.text(), settings)

        content = ""

        # Add item children
        last = None
        for c in item.children():

            # Separator
            if last:
                # Between folder
                if last == c.type() == "folder":
                    content += s["Separator"]["FF"]

                elif last == c.type() == "md":
                    content += s["Separator"]["TT"]

                elif last == "folder" and c.type() == "md":
                    content += s["Separator"]["FT"]

                elif last == "md" and c.type() == "folder":
                    content += s["Separator"]["TF"]

            content += self.concatenate(c, settings)

            last = c.type()

        # r += self.processContent(content, settings)
        r += content

        return r

    def processTitle(self, text, level, settings):
        return text + "\n"

    def processText(self, content, settings):
        s = settings["Transform"]

        if s["Dash"]:
            content = content.replace("---", "—")

        if s["Ellipse"]:
            content = content.replace("...", "…")

        if s["Spaces"]:
            o = ""
            while o != content:
                o = content
                content = content.replace("  ", " ")

        if s["DoubleQuotes"]:
            q = s["DoubleQuotes"].split("___")
            s["Custom"].append([True, '"(.*?)"', "{}\\1{}".format(q[0], q[1]), True])

        if s["SingleQuote"]:
            q = s["SingleQuote"].split("___")
            s["Custom"].append([True, "'(.*?)'", "{}\\1{}".format(q[0], q[1]), True])

        for enabled, A, B, reg in s["Custom"]:
            if not enabled:
                continue

            if not reg:
                content = content.replace(A, B)

            else:
                content = re.sub(A, B, content)

        content += "\n"

        return content

