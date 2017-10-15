#!/usr/bin/env python
# --!-- coding: utf8 --!--

# Import/export outline cards in OPML format

from manuskript.models.outlineModel import outlineItem
from manuskript.enums import Outline
import xmltodict
from manuskript.functions import mainWindow
import xml.etree.ElementTree as ET


def handleCard(_, card):
    print(card['title'])


def exportOpml():
    return True


def importOpml(opmlFilePath):
    with open(opmlFilePath, 'r') as opmlFile:
        opmlContent = opmlFile.read()

    mw = mainWindow()
    mdl = mw.mdlOutline

    dict = xmltodict.parse(opmlContent, item_callback=handleCard)

    opmlNode = dict['opml']
    bodyNode = opmlNode['body']

    outline = bodyNode['outline']

    for element in outline:
        if '@text' in element:
            card = outlineItem(parent=mdl.rootItem)
            card.title = element['@text']
            card.ID = card.title
            card.path = ''
            if '@_note' in element:
                card.setData(Outline.text.value, element['@_note'])

    return True
