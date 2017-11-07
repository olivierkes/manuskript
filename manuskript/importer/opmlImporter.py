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
    fileFormat = "OPML Files (*.opml)"
    icon = "text-x-opml+xml"

    @classmethod
    def startImport(cls, filePath, parentItem, settingsWidget):
        """
        Import/export outline cards in OPML format.
        """
        ret = False

        try:
            with open(filePath, 'r') as opmlFile:
                opmlContent = cls.saveNewlines(opmlFile.read())
        except:
            QMessageBox.critical(settingsWidget,
                                 qApp.translate("Import", "OPML Import"),
                                 qApp.translate("Import", "File open failed."))
            return None

        parsed = ET.fromstring(bytes(opmlContent, 'utf-8'))

        opmlNode = parsed
        bodyNode = opmlNode.find("body")
        items = []

        if bodyNode is not None:
            outlineEls = bodyNode.findall("outline")

            if outlineEls is not None:
                for element in outlineEls:
                    items.append(cls.parseItems(element, parentItem))
                ret = True

        if ret:
            #QMessageBox.information(
                #settingsWidget,
                #qApp.translate("Import", "OPML Import"),
                #qApp.translate("Import", "Import Complete."))
            pass
        else:
            QMessageBox.critical(
                settingsWidget,
                qApp.translate("Import", "OPML Import"),
                qApp.translate("Import", "This does not appear to be a valid OPML file."))

            return None

        return items

    def importOpml(opmlFilePath, idx):
        """
        Import/export outline cards in OPML format.
        #FIXME: delete me when done with startImport
        """
        ret = False
        mw = mainWindow()

        try:
            with open(opmlFilePath, 'r') as opmlFile:
                opmlContent = saveNewlines(opmlFile.read())
        except:
            QMessageBox.critical(mw, mw.tr("OPML Import"),
                                mw.tr("File open failed."))
            return False

        mdl = mw.mdlOutline

        if idx.internalPointer() is not None:
            parentItem = idx.internalPointer()
        else:
            parentItem = mdl.rootItem

        try:
            parsed = ET.fromstring(bytes(opmlContent, 'utf-8'))

            opmlNode = parsed
            bodyNode = opmlNode.find("body")

            if bodyNode is not None:
                outlineEls = bodyNode.findall("outline")

                if outlineEls is not None:
                    for element in outlineEls:
                        parseItems(element, parentItem)

                    mdl.layoutChanged.emit()
                    mw.treeRedacOutline.viewport().update()
                    ret = True
        except:
            pass

        # TODO: Translation
        if ret:
            QMessageBox.information(mw, mw.tr("OPML Import"),
                                mw.tr("Import Complete."))
        else:
            QMessageBox.critical(mw, mw.tr("OPML Import"),
                                mw.tr("This does not appear to be a valid OPML file."))

        return ret

    @classmethod
    def parseItems(cls, underElement, parentItem=None):
        title = underElement.get('text')
        if title is not None:

            card = outlineItem(parent=parentItem, title=title)

            body = ""
            note = underElement.get('_note')
            if note is not None and not cls.isWhitespaceOnly(note):
                body = cls.restoreNewLines(note)

            children = underElement.findall('outline')
            if children is not None and len(children) > 0:
                for el in children:
                    cls.parseItems(el, card)
            else:
                card.setData(Outline.type.value, 'md')
                card.setData(Outline.text.value, body)

        return card

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
