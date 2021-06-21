#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os

from manuskript.io.textFile import TextFile

LEGACY_MSK_VERSION = 0
CURRENT_MSK_VERSION = 1


class Version:

    def __init__(self, path):
        self.file = TextFile(os.path.join(path, "MANUSKRIPT"))
        self.legacy_file = TextFile(os.path.join(path, "VERSION"))

        self.value = LEGACY_MSK_VERSION

    def loadLegacy(self):
        try:
            return int(self.legacy_file.load())
        except FileNotFoundError or ValueError:
            return LEGACY_MSK_VERSION

    def load(self):
        try:
            self.value = int(self.file.load())
        except FileNotFoundError or ValueError:
            self.value = self.loadLegacy()

    def save(self):
        self.file.save(str(self.value))
