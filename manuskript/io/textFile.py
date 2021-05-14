#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os

from manuskript.io.abstractFile import AbstractFile


class TextFile(AbstractFile):

    def load(self):
        with open(self.path, 'rt', encoding='utf-8') as file:
            return file.read()

    def save(self, content):
        with open(self.path, 'wt', encoding='utf-8') as file:
            file.write(content)

    def remove(self):
        if os.path.exists(self.path):
            os.remove(self.path)
