#!/usr/bin/env python
# --!-- coding: utf8 --!--

from lxml import etree
from manuskript.io.xmlFile import XmlFile


class OpmlOutlineItem:

    def __init__(self):
        self.attributes = dict()
        self.children = list()

    def __iter__(self):
        return self.children.__iter__()

    def keys(self):
        return self.attributes.keys()

    def values(self):
        return self.attributes.values()


class OpmlFile(XmlFile):

    @classmethod
    def loadOutline(cls, element):
        outline = OpmlOutlineItem()

        for key in element.keys():
            outline.attributes[key] = element.get(key)

        for child in element.getchildren():
            outline.children.append(cls.loadOutline(child))

        return outline

    def load(self):
        tree = XmlFile.load(self)
        root = tree.getroot()

        if root.tag != "opml":
            raise IOError("No valid OPML!")

        body = root.find("body")

        if body is None:
            return []

        return [OpmlFile.loadOutline(element) for element in body.getchildren()]

    @classmethod
    def saveOutline(cls, outline, parent):
        element = etree.SubElement(parent, "outline")

        for (key, value) in outline.attributes.items():
            if value is None:
                continue

            element.attrib[key] = value

        for child in outline.children:
            cls.saveOutline(child, element)

    def save(self, content):
        root = etree.Element("opml")
        root.set("version", "1.0")

        body = etree.SubElement(root, "body")

        for outline in content:
            OpmlFile.saveOutline(outline, body)

        tree = etree.ElementTree(root)
        XmlFile.save(self, tree)
