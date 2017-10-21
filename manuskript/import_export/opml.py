#!/usr/bin/env python
# --!-- coding: utf8 --!--

# Import/export outline cards in OPML format

from manuskript.models.outlineModel import outlineItem
from manuskript.enums import Outline
import xmltodict
from manuskript.functions import mainWindow


def handleCard(_, card):
    print(card['title'])


def exportOpml():
    return True


def importOpml(opmlFilePath):
    with open(opmlFilePath, 'r') as opmlFile:
        opmlContent = saveNewlines(opmlFile.read())

    mw = mainWindow()
    mdl = mw.mdlOutline

    dict = xmltodict.parse(opmlContent, strip_whitespace=False)

    opmlNode = dict['opml']
    bodyNode = opmlNode['body']

    outline = bodyNode['outline']

    for element in outline:
        parseItems(underElement=element, parentItem=mdl.rootItem)

    return True

def parseItems(underElement, parentItem):
    if '@text' in underElement:
        card = outlineItem(parent=parentItem, title=underElement['@text'])

        text = ""
        summary = ""
        if '@_note' in underElement:
            text = restoreNewLines(underElement['@_note'])
            summary = text[0:128]

        card.setData(Outline.summaryFull.value, summary)

        if 'outline' in underElement:
            elements = underElement['outline']

            for el in elements:
                parseItems(el, card)
        else:
            card.setData(Outline.type.value, 'md')
            card.setData(Outline.text.value, text)

        # I assume I don't have to do the following
        # parentItem.appendChild(card)

    return

def saveNewlines(inString):
    inString = inString.replace("\r\n", "\n")
    inString = inString.replace("\n", "{{lf}}")

    return inString

def restoreNewLines(inString):
    return inString.replace("{{lf}}", "\n")

