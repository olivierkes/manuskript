#!/usr/bin/env python
# --!-- coding: utf8 --!--

from typing import Iterator

from lxml import etree

from manuskript.io.xmlFile import XmlFile


class OpmlOutlineItem:
    def __init__(self) -> None:
        self.attributes: dict[str, str] = dict()
        self.children: list[OpmlOutlineItem] = list()

    def __iter__(self) -> Iterator[OpmlOutlineItem]:
        return self.children.__iter__()

    def keys(self) -> Iterator[str]:
        return self.attributes.keys().__iter__()

    def values(self) -> Iterator[str]:
        return self.attributes.values().__iter__()


class OpmlFile(XmlFile):
    @classmethod
    def loadOutline(cls, element: etree.SubElement) -> OpmlOutlineItem:
        outline = OpmlOutlineItem()

        for key in element.keys():
            outline.attributes[key] = element.get(key)

        for child in element.getchildren():
            outline.children.append(cls.loadOutline(child))

        return outline

    def load(self) -> list[OpmlOutlineItem]:
        tree = XmlFile.load(self)
        root = tree.getroot()

        if root.tag != "opml":
            raise IOError("No valid OPML!")

        body = root.find("body")

        if body is None:
            return []

        return [OpmlFile.loadOutline(element) for element in body.getchildren()]

    @classmethod
    def saveOutline(cls, outline: OpmlOutlineItem, parent: etree.SubElement) -> None:
        element = etree.SubElement(parent, "outline")

        for key, value in outline.attributes.items():
            if value is None:
                continue

            element.attrib[key] = value

        for child in outline.children:
            cls.saveOutline(child, element)

    def save(self, content: list[OpmlOutlineItem]) -> None:
        root = etree.Element("opml")
        root.set("version", "1.0")

        body = etree.SubElement(root, "body")

        for outline in content:
            OpmlFile.saveOutline(outline, body)

        tree = etree.ElementTree(root)
        XmlFile.save(self, tree)
