#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os
import shutil

from manuskript.io.textFile import TextFile
from manuskript.io.zipFile import ZipFile


class MskFile(TextFile, ZipFile):

    def __init__(self, path):
        dir_path = os.path.splitext(path)[0]

        if (not os.path.isdir(dir_path)) or (os.path.getsize(path) > 1):
            dir_path = None

        self.zipFile = dir_path is None
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

    def load(self):
        if self.zipFile:
            ZipFile.load(self)
        else:
            value = TextFile.load(self)

            if value == "1":
                self.setZipFile(False)

        return self.zipFile

    def save(self, content=None):
        if not (content is None):
            self.setZipFile(content)

        if self.zipFile:
            ZipFile.save(self)
        else:
            TextFile.save(self, "1")

    def remove(self):
        if os.path.isdir(self.dir_path):
            shutil.rmtree(self.dir_path)

        ZipFile.remove(self)
