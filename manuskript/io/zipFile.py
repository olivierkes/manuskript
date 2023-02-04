#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os
import shutil
import tempfile

from zipfile import ZipFile as _ZipFile
from manuskript.io.abstractFile import AbstractFile


class ZipFile(AbstractFile):

    def __init__(self, path, directoryPath=None):
        AbstractFile.__init__(self, path)

        if directoryPath is None:
            self.tmp = tempfile.TemporaryDirectory()
            directoryPath = self.tmp.name
        else:
            self.tmp = None

        self.directoryPath = directoryPath

    def __del__(self):
        if not (self.tmp is None):
            self.tmp.cleanup()

    def load(self):
        if self.directoryPath is None:
            self.tmp = tempfile.TemporaryDirectory()
            self.directoryPath = self.tmp.name

        with _ZipFile(self.path) as archive:
            archive.extractall(self.directoryPath)

        return self.directoryPath

    def save(self, content=None):
        if not (content is None):
            if not (self.tmp is None):
                self.tmp.cleanup()

            self.tmp = None
            self.directoryPath = content
        elif self.directoryPath is None:
            if self.tmp is None:
                self.tmp = tempfile.TemporaryDirectory()

            self.directoryPath = self.tmp.name

        shutil.make_archive(self.path, 'zip', self.directoryPath)
        shutil.move(self.path + ".zip", self.path)

    def remove(self):
        if os.path.exists(self.path):
            os.remove(self.path)
