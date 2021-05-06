#!/usr/bin/env python
# --!-- coding: utf8 --!--

import re

from manuskript.io.abstractFile import AbstractFile


class MmdFile(AbstractFile):

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
                    if not (metaKey is None):
                        metadata[metaKey] = metaValue

                    break

            if not ignoreBody:
                body = file.read()

        return metadata, body

    def load(self):
        return self.loadMMD(False)

    def save(self, content):
        metadata, body = content
        metaSpacing = 0

        for key in metadata.keys():
            metaSpacing = max(metaSpacing, len(key) + 2)

        with open(self.path, 'wt', encoding='utf-8') as file:
            for (key, value) in metadata.items():
                spacing = metaSpacing - (len(key) + 2)
                lines = value.split("\n")

                file.write(key + ": " + spacing * " " + lines[0] + "\n")

                for line in lines[1:]:
                    file.write(metaSpacing * " " + line + "\n")

            file.write("\n")
            if not (body is None):
                file.write(body)
