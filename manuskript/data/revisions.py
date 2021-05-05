#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os

from lxml import etree
from manuskript.io.xmlFile import XmlFile


class RevisionEntry:

    def __init__(self, outline, timestamp: int, text: str):
        self.outline = outline

        self.timestamp = timestamp
        self.text = text

    def load(self):
        self.outline.load()


class RevisionOutline:

    def __init__(self, revisions, ID: int):
        self.revisions = revisions

        self.ID = ID
        self.entries = list()

    def __iter__(self):
        return self.entries.__iter__()

    def load(self):
        self.revisions.load()


class Revisions:

    def __init__(self, path):
        self.file = XmlFile(os.path.join(path, "revisions.xml"))
        self.outline = dict()

    def __iter__(self):
        return self.outline.values().__iter__()

    @classmethod
    def loadRevisionEntry(cls, revisions, ID: int, element: etree.Element):
        timestamp = element.get("timestamp")
        text = element.get("text")

        if (timestamp is None) or (text is None):
            return

        revOutline = revisions.outline.get(ID, None)

        if revOutline is None:
            revOutline = RevisionOutline(revisions, ID)
            revisions.outline[ID] = revOutline

        revOutline.entries.append(RevisionEntry(revOutline, timestamp, text))

    @classmethod
    def loadRevisionOutline(cls, revisions, element: etree.Element, parent: etree.Element):
        if element.tag == "revision":
            if parent is None:
                return

            ID = int(parent.get("ID"))

            cls.loadRevisionEntry(revisions, ID, element)
        elif element.tag == "outlineItem":
            ID = element.get("ID")

            if ID is None:
                return

            for child in element:
                cls.loadRevisionOutline(revisions, child, element)

    def load(self):
        tree = self.file.load()
        Revisions.loadRevisionOutline(self, tree.getroot(), None)
