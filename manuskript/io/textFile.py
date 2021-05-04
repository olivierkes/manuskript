#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.io.abstractFile import AbstractFile


class TextFile(AbstractFile):

    def load(self):
        with open(self.path, 'rb') as file:
            return file.read().decode('utf-8')

    def save(self, content):
        with open(self.path, 'wb') as file:
            file.write(content.encode('utf-8'))
