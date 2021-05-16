#!/usr/bin/env python
# --!-- coding: utf8 --!--
import os
import re

from manuskript.io.abstractFile import AbstractFile


class MmdFile(AbstractFile):

    def __init__(self, path, metaSpacing=16):
        AbstractFile.__init__(self, path)

        self.metaSpacing = metaSpacing

    def loadMMD(self, ignoreBody: bool = True):
        metadata = dict()
        body = None

        metaPattern = re.compile(r"^([^\s].*?):\s*(.*)\n$")
        metaValuePattern = re.compile(r"^(\s+)(.*)\n$")
        metaKey = None
        metaValue = None

        with open(self.path, 'rt', encoding='utf-8') as file:
            for line in file:
                m = metaPattern.match(line)

                if not (m is None):
                    if not (metaKey is None):
                        metadata[metaKey] = metaValue

                    metaKey = m.group(1)
                    metaValue = m.group(2)
                    continue

                m = metaValuePattern.match(line)

                if not (m is None):
                    metaValue += "\n" + m.group(2)
                elif line == "\n":
                    break

            if not (metaKey is None):
                metadata[metaKey] = metaValue

            if not ignoreBody:
                body = file.read()

        return metadata, body

    def load(self):
        return self.loadMMD(False)

    def save(self, content):
        metadata, body = content
        metaSpacing = self.metaSpacing

        for (key, value) in metadata.items():
            if value is None:
                continue

            metaSpacing = max(metaSpacing, len(key) + 2)

        with open(self.path, 'wt', encoding='utf-8') as file:
            for (key, value) in metadata.items():
                if value is None:
                    continue

                spacing = metaSpacing - (len(key) + 2)
                lines = str(value).split("\n")

                file.write(key + ": " + spacing * " " + lines[0] + "\n")

                for line in lines[1:]:
                    file.write(metaSpacing * " " + line + "\n")

            if not (body is None):
                file.write("\n" + body)

    def remove(self):
        if os.path.exists(self.path):
            os.remove(self.path)
