#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os

from manuskript.data.abstractData import AbstractData
from manuskript.io.mmdFile import MmdFile


class Summary(AbstractData):

    def __init__(self, path):
        AbstractData.__init__(self, os.path.join(path, "summary.txt"))
        self.file = MmdFile(self.dataPath, 13)

        self.situation = None
        self.sentence = None
        self.paragraph = None
        self.page = None
        self.full = None

    def changePath(self, path: str):
        AbstractData.changePath(self, os.path.join(path, "summary.txt"))
        self.file = MmdFile(self.dataPath, 13)

    def load(self):
        AbstractData.load(self)

        try:
            metadata, _ = self.file.loadMMD(True)
        except FileNotFoundError:
            metadata = dict()

        self.situation = metadata.get("Situation", None)
        self.sentence = metadata.get("Sentence", None)
        self.paragraph = metadata.get("Paragraph", None)
        self.page = metadata.get("Page", None)
        self.full = metadata.get("Full", None)
        self.complete()

    def save(self):
        AbstractData.save(self)
        metadata = dict()

        metadata["Situation"] = self.situation
        metadata["Sentence"] = self.sentence
        metadata["Paragraph"] = self.paragraph
        metadata["Page"] = self.page
        metadata["Full"] = self.full

        self.file.save((metadata, None))
        self.complete()
