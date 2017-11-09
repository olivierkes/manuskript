#!/usr/bin/env python
# --!-- coding: utf8 --!--

from PyQt5.QtWidgets import qApp, QMessageBox
from manuskript.models.outlineModel import outlineItem
from manuskript.enums import Outline
from lxml import etree as ET
from manuskript.functions import mainWindow
from manuskript.importer.abstractImporter import abstractImporter

class opmlImporter(abstractImporter):

    name = "OPML"
    description = ""
    fileFormat = "OPML Files (*.opml *.xml)"
    icon = "text-x-opml+xml"

    @classmethod
    def isValid(cls):
        return True

    @classmethod
    def startImport(cls, filePath, parentItem, settingsWidget, fromString=None):
        """
        Import/export outline cards in OPML format.
        """
        ret = False

        if filePath != "":
            # We have a filePath, so we read the file
            try:
                with open(filePath, 'rb') as opmlFile:
                    #opmlContent = cls.saveNewlines(opmlFile.read())
                    opmlContent = opmlFile.read()
            except:
                QMessageBox.critical(settingsWidget,
                                    qApp.translate("Import", "OPML Import"),
                                    qApp.translate("Import", "File open failed."))
                return None

        elif fromString == "":
            # We have neither filePath nor fromString, so we leave
            return None

        else:
            # We load from string
            opmlContent = bytes(fromString, "utf-8")

        parsed = ET.fromstring(opmlContent)

        opmlNode = parsed
        bodyNode = opmlNode.find("body")
        items = []

        if bodyNode is not None:
            outlineEls = bodyNode.findall("outline")

            if outlineEls is not None:
                for element in outlineEls:
                    items.extend(cls.parseItems(element, parentItem))
                ret = True

        if not ret:
            QMessageBox.critical(
                settingsWidget,
                qApp.translate("Import", "OPML Import"),
                qApp.translate("Import", "This does not appear to be a valid OPML file."))

            return None

        return items

    @classmethod
    def parseItems(cls, underElement, parentItem=None):
        items = []
        title = underElement.get('text')
        if title is not None:

            card = outlineItem(parent=parentItem, title=title)
            items.append(card)

            body = ""
            note = underElement.get('_note')
            if note is not None and not cls.isWhitespaceOnly(note):
                #body = cls.restoreNewLines(note)
                body = note

            children = underElement.findall('outline')
            if children is not None and len(children) > 0:
                for el in children:
                    items.extend(cls.parseItems(el, card))
            else:
                card.setData(Outline.type.value, 'md')
                card.setData(Outline.text.value, body)

        return items

    @classmethod
    def saveNewlines(cls, inString):
        """
        Since XML parsers are notorious for stripping out significant newlines,
        save them in a form we can restore after the parse.
        """
        inString = inString.replace("\r\n", "\n")
        inString = inString.replace("\n", "{{lf}}")

        return inString

    @classmethod
    def restoreNewLines(cls, inString):
        """
        Restore any significant newlines
        """
        return inString.replace("{{lf}}", "\n")

    @classmethod
    def isWhitespaceOnly(cls, inString):
        """
        Determine whether or not a string only contains whitespace.
        """
        s = cls.restoreNewLines(inString)
        s = ''.join(s.split())

        return len(s) is 0
