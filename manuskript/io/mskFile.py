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

    def __init__(self, path):
        try:
            _ZipFile(path)
            dir_path = None
        except BadZipFile:
            dir_path = os.path.splitext(path)[0]

            if not os.path.isdir(dir_path):
                dir_path = None

        self.zipFile = dir_path is None
        self.version = str(LEGACY_MSK_VERSION)

        ZipFile.__init__(self, path, dir_path)

    def __del__(self):
        ZipFile.__del__(self)

        if self.isZipFile() and (self.tmp is None) and not (self.dir_path is None):
            shutil.rmtree(self.dir_path)

    def isZipFile(self) -> bool:
        return self.zipFile

    def setZipFile(self, zipFile: bool):
        if zipFile is self.zipFile:
            return

        if not zipFile:
            self.dir_path = os.path.splitext(self.path)[0]

            if not os.path.isdir(self.dir_path):
                os.mkdir(self.dir_path)

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
        if os.path.isdir(self.dir_path):
            shutil.rmtree(self.dir_path)

        ZipFile.remove(self)
