#!/usr/bin/env python
# --!-- coding: utf8 --!--

from lxml import etree
from manuskript.io.xmlFile import XmlFile


class OpmlOutlineItem:

    def __init__(self, tag="outline"):
        self.tag = tag
        self.attributes = dict()
        self.children = []

    def keys(self):
        return self.attributes.keys()

    def values(self):
        return self.attributes.values()


class OpmlFile(XmlFile):

    @classmethod
    def loadOutline(cls, element):
        outline = OpmlOutlineItem(element.tag)

        for key in element.keys():
            outline.attributes[key] = element.get(key)

        for child in element.getchildren():
            outline.children.append(cls.loadOutline(child))

        return outline

    def load(self):
        tree = XmlFile.load(self)
        root = tree.getroot()

        return OpmlFile.loadOutline(root)

    @classmethod
    def saveOutline(cls, outline, parent=None):
        if parent is None:
            element = etree.Element(outline.tag)
        else:
            element = etree.SubElement(parent, outline.tag)

        for key in outline.keys():
            element.attrib[key] = outline.attributes[key]

        for child in outline.children:
            cls.saveOutline(child, element)

        return element

    def save(self, content):
        root = OpmlFile.saveOutline(content)
        tree = etree.ElementTree(root)

        XmlFile.save(self, tree)
