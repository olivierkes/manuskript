#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os

from manuskript.io.abstractFile import AbstractFile


class BinaryFile(AbstractFile):

    def load(self):
        with open(self.path, 'rb') as file:
            return file.read()

    def save(self, content):
        with open(self.path, 'wb') as file:
            file.write(content)

    def remove(self):
        if os.path.exists(self.path):
            os.remove(self.path)
