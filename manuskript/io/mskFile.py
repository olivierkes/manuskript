#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os
import shutil

from zipfile import ZipFile as _ZipFile, BadZipFile
from manuskript.io.textFile import TextFile
from manuskript.io.zipFile import ZipFile
from manuskript.util import safeInt
from manuskript.data.version import LEGACY_MSK_VERSION


class MskFile(TextFile, ZipFile):

    def __init__(self, path, ignorePath: bool = False, forceZip: bool = False):
        try:
            if not forceZip:
                _ZipFile(path)

            directoryPath = None
        except (BadZipFile, FileNotFoundError):
            directoryPath = os.path.splitext(path)[0]

            if (not ignorePath) and (not os.path.isdir(directoryPath)):
                directoryPath = None

        self.zipFile = directoryPath is None
        self.version = str(LEGACY_MSK_VERSION)

        ZipFile.__init__(self, path, directoryPath)

    def __del__(self):
        ZipFile.__del__(self)

        if self.isZipFile() and (self.tmp is None) and not (self.directoryPath is None):
            shutil.rmtree(self.directoryPath)

    def isZipFile(self) -> bool:
        return self.zipFile

    def setZipFile(self, zipFile: bool):
        if zipFile is self.zipFile:
            return

        if not zipFile:
            self.directoryPath = os.path.splitext(self.path)[0]

            if not os.path.isdir(self.directoryPath):
                os.mkdir(self.directoryPath)

            if os.path.exists(self.path):
                ZipFile.load(self)

        self.zipFile = zipFile

    def getVersion(self) -> int:
        return safeInt(self.version, LEGACY_MSK_VERSION)

    def setVersion(self, version: int):
        self.version = str(version)

    def load(self):
        if self.zipFile:
            ZipFile.load(self)
        else:
            self.version = TextFile.load(self)

            if self.getVersion() > LEGACY_MSK_VERSION:
                self.setZipFile(False)

        return self.zipFile

    def save(self, content=None):
        if not (content is None):
            self.setZipFile(content)

        if self.zipFile:
            ZipFile.save(self)
        else:
            TextFile.save(self, self.version)

    def remove(self):
        if os.path.isdir(self.directoryPath):
            shutil.rmtree(self.directoryPath)

        ZipFile.remove(self)
