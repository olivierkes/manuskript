#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os
import shutil
import tempfile

from zipfile import ZipFile as _ZipFile
from manuskript.io.abstractFile import AbstractFile


class ZipFile(AbstractFile):

    def __init__(self, path, dir_path=None):
        AbstractFile.__init__(self, path)

        if dir_path is None:
            self.tmp = tempfile.TemporaryDirectory()
            dir_path = self.tmp.name
        else:
            self.tmp = None

        self.dir_path = dir_path

    def __del__(self):
        if not (self.tmp is None):
            self.tmp.cleanup()

    def load(self):
        if self.dir_path is None:
            self.tmp = tempfile.TemporaryDirectory()
            self.dir_path = self.tmp.name

        archive = _ZipFile(self.path)
        archive.extractall(self.dir_path)
        return self.dir_path

    def save(self, content=None):
        if not (content is None):
            if not (self.tmp is None):
                self.tmp.cleanup()

            self.tmp = None
            self.dir_path = content
        elif self.dir_path is None:
            if self.tmp is None:
                self.tmp = tempfile.TemporaryDirectory()

            self.dir_path = self.tmp.name

        shutil.make_archive(self.path, 'zip', self.dir_path)
        shutil.move(self.path + ".zip", self.path)

    def remove(self):
        if os.path.exists(self.path):
            os.remove(self.path)
