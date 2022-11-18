#!/usr/bin/env python
# --!-- coding: utf8 --!--

import collections
import os

from manuskript.data.color import Color
from manuskript.io.mmdFile import MmdFile


class Label:

    def __init__(self, host, name: str, color: Color):
        self.host = host

        self.name = name
        self.color = color

    def __str__(self):
        return self.name

    def load(self):
        self.host.load()

    def save(self):
        self.host.save()


class LabelHost:

    def __init__(self, path):
        self.file = MmdFile(os.path.join(path, "labels.txt"), 21)
        self.labels = collections.OrderedDict()

    def addLabel(self, name: str = None, color: Color = None):
        if name is None:
            name = "New Label"

        label = Label(self, name, color)
        self.labels[name] = label
        return label

    def removeLabel(self, name: str):
        self.labels.pop(name)

    def renameLabel(self, oldName: str, newName: str):
        label = self.labels.get(oldName)
        label.name = newName
        self.labels[newName] = label
        self.labels.pop(oldName)

    def getLabel(self, name: str):
        return self.labels.get(name)

    def __iter__(self):
        return self.labels.values().__iter__()

    def load(self):
        try:
            metadata, _ = self.file.loadMMD(True)
            self.labels.clear()
        except FileNotFoundError:
            self.labels.clear()
            return

        for (name, value) in metadata.items():
            if value is None:
                continue

            self.addLabel(name, Color.parse(value))

    def save(self):
        metadata = collections.OrderedDict()

        for (name, label) in self.labels.items():
            metadata[name] = label.color

        self.file.save((metadata, None))
