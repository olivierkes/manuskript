#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os
from typing import Iterator

from lxml import etree

from manuskript.data.abstractData import AbstractData
from manuskript.io.xmlFile import XmlFile


class RevisionEntry:
    def __init__(self, outline: RevisionOutline, timestamp: int, text: str) -> None:
        self.outline = outline

        self.timestamp = timestamp
        self.text = text

    def load(self) -> None:
        self.outline.load()


class RevisionOutline:
    def __init__(self, revisions: Revisions, ID: int) -> None:
        self.revisions = revisions

        self.ID = ID
        self.entries: list[RevisionEntry] = list()

    def __iter__(self) -> Iterator[RevisionEntry]:
        return self.entries.__iter__()

    def load(self) -> None:
        self.revisions.load()


class Revisions(AbstractData):
    def __init__(self, path: str) -> None:
        AbstractData.__init__(self, os.path.join(path, "revisions.xml"))
        self.file = XmlFile(self.dataPath)
        self.outline: dict[int, RevisionOutline] = dict()

    def changePath(self, path: str) -> None:
        AbstractData.changePath(self, os.path.join(path, "revisions.xml"))
        self.file = XmlFile(self.dataPath)

    def __iter__(self) -> Iterator[RevisionOutline]:
        return self.outline.values().__iter__()

    @classmethod
    def loadRevisionEntry(cls, revisions: Revisions, ID: int, element: etree.Element) -> None:
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
    def loadRevisionOutline(
        cls, revisions: Revisions, element: etree.Element, parent: etree.Element
    ) -> None:
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

    def load(self) -> None:
        self.outline.clear()

        AbstractData.load(self)

        try:
            tree = self.file.load()

            Revisions.loadRevisionOutline(self, tree.getroot(), None)

            self.complete()
        except FileNotFoundError:
            self.complete(False)

    def save(self) -> None:
        AbstractData.save(self)

        # TODO

        self.complete()
