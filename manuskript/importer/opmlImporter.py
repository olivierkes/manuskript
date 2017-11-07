#!/usr/bin/env python
# --!-- coding: utf8 --!--

from PyQt5.QtWidgets import QMessageBox
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

    def importOpml(opmlFilePath, idx):
        """
        Import/export outline cards in OPML format.
        """
        ret = False
        mw = mainWindow()

        try:
            with open(opmlFilePath, 'r') as opmlFile:
                opmlContent = saveNewlines(opmlFile.read())
        except:
            # TODO: Translation
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


    def parseItems(underElement, parentItem):
        text = underElement.get('text')
        if text is not None:

            # In the case where the title is exceptionally long, trim it so it isn't
            # distracting in the tab label
            title = text[0:32]
            if len(title) < len(text):
                title += '...'

            card = outlineItem(parent=parentItem, title=title)

            body = ""
            summary = ""
            note = underElement.get('_note')
            if note is not None and not isWhitespaceOnly(note):
                body = restoreNewLines(note)
                summary = body[0:128]
            else:

                # There's no note (body), but there is a title.  Fill the
                # body with the title to support cards that consist only
                # of a title.
                body = text

            card.setData(Outline.summaryFull.value, summary)

            children = underElement.findall('outline')
            if children is not None and len(children) > 0:
                for el in children:
                    parseItems(el, card)
            else:
                card.setData(Outline.type.value, 'md')
                card.setData(Outline.text.value, body)

                # I assume I don't have to do the following
                # parentItem.appendChild(card)

        return

    def saveNewlines(inString):
        """
        Since XML parsers are notorious for stripping out significant newlines,
        save them in a form we can restore after the parse.
        """
        inString = inString.replace("\r\n", "\n")
        inString = inString.replace("\n", "{{lf}}")

        return inString

    def restoreNewLines(inString):
        """
        Restore any significant newlines
        """
        return inString.replace("{{lf}}", "\n")

    def isWhitespaceOnly(inString):
        """
        Determine whether or not a string only contains whitespace.
        """
        str = restoreNewLines(inString)
        str = ''.join(str.split())

        return len(str) is 0
