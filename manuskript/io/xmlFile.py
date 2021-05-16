#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os

from lxml import etree
from manuskript.io.abstractFile import AbstractFile


class XmlFile(AbstractFile):

    def load(self):
        with open(self.path, 'rb') as file:
            return etree.parse(file)

    def save(self, content):
        with open(self.path, 'wb') as file:
            content.write(file, encoding="utf-8", xml_declaration=True, pretty_print=True)

    def remove(self):
        if os.path.exists(self.path):
            os.remove(self.path)
