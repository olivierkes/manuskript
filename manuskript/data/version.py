#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os

from manuskript.data.abstractData import AbstractData
from manuskript.io.textFile import TextFile

LEGACY_MSK_VERSION = 0
CURRENT_MSK_VERSION = 1


class Version(AbstractData):

    def __init__(self, path):
        AbstractData.__init__(self, os.path.join(path, "MANUSKRIPT"))
        self.file = TextFile(self.dataPath)
        self.legacy_file = TextFile(os.path.join(path, "VERSION"))

        self.value = LEGACY_MSK_VERSION

    def changePath(self, path: str):
        AbstractData.changePath(self, os.path.join(path, "MANUSKRIPT"))
        self.file = TextFile(self.dataPath)
        self.legacy_file = TextFile(os.path.join(path, "VERSION"))

    def loadLegacy(self):
        try:
            return int(self.legacy_file.load())
        except FileNotFoundError or ValueError:
            return LEGACY_MSK_VERSION

    def load(self):
        AbstractData.load(self)

        try:
            self.value = int(self.file.load())
        except FileNotFoundError or ValueError:
            self.value = self.loadLegacy()

        self.complete()

    def save(self):
        AbstractData.save(self)

        self.file.save(str(self.value))
        self.complete()
