#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os

from manuskript.data.abstractData import AbstractData
from manuskript.io.mmdFile import MmdFile


class Info(AbstractData):

    def __init__(self, path):
        AbstractData.__init__(self, os.path.join(path, "infos.txt"))
        self.file = MmdFile(self.dataPath, 16)

        self.title = None
        self.subtitle = None
        self.serie = None
        self.volume = None
        self.genre = None
        self.license = None
        self.author = None
        self.email = None

    def load(self):
        AbstractData.load(self)

        try:
            metadata, _ = self.file.loadMMD(True)
        except FileNotFoundError:
            metadata = dict()

        self.title = metadata.get("Title", None)
        self.subtitle = metadata.get("Subtitle", None)
        self.serie = metadata.get("Serie", None)
        self.volume = metadata.get("Volume", None)
        self.genre = metadata.get("Genre", None)
        self.license = metadata.get("License", None)
        self.author = metadata.get("Author", None)
        self.email = metadata.get("Email", None)
        self.complete()

    def save(self):
        AbstractData.save(self)
        metadata = dict()

        metadata["Title"] = self.title
        metadata["Subtitle"] = self.subtitle
        metadata["Serie"] = self.serie
        metadata["Volume"] = self.volume
        metadata["Genre"] = self.genre
        metadata["License"] = self.license
        metadata["Author"] = self.author
        metadata["Email"] = self.email

        self.file.save((metadata, None))
        self.complete()
