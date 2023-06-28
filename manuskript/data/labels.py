#!/usr/bin/env python
# --!-- coding: utf8 --!--

import collections
import os

from manuskript.data.abstractData import AbstractData
from manuskript.data.color import Color
from manuskript.io.mmdFile import MmdFile


class Label:

    def __init__(self, host, index: int, name: str, color: Color):
        self.host = host
        self.ID = index

        self.name = name
        self.color = color

    def __str__(self):
        return self.name

    def load(self):
        self.host.load()

    def save(self):
        self.host.save()


class LabelHost(AbstractData):

    def __init__(self, path):
        AbstractData.__init__(self, os.path.join(path, "labels.txt"))
        self.file = MmdFile(self.dataPath, 21)
        self.labels = collections.OrderedDict()

    def changePath(self, path: str):
        AbstractData.changePath(self, os.path.join(path, "labels.txt"))
        self.file = MmdFile(self.dataPath, 21)

    def addLabel(self, name: str = None, color: Color = None) -> Label:
        if name is None:
            name = "New Label"

        label = Label(self, 1+len(self.labels), name, color)
        self.labels[name] = label
        return label

    def removeLabel(self, name: str) -> Label:
        return self.labels.pop(name)

    def renameLabel(self, oldName: str, newName: str):
        match = False
        drop = [oldName]

        for name, label in self.labels.items():
            if match:
                drop.append(name)
            elif name == oldName:
                label.name = newName
                match = True

        if not match:
            return

        labels = list()
        for name in drop:
            labels.append(self.labels.pop(name))

        for label in labels:
            self.labels[label.name] = label

    def getLabel(self, name: str) -> Label:
        return self.labels.get(name)

    def getLabelByID(self, ID: int | None) -> Label | None:
        if ID is None:
            return None

        index = 1
        for label in self.labels.values():
            if index == ID:
                assert label.ID == ID
                return label

            index += 1

        return None

    def __iter__(self):
        return self.labels.values().__iter__()

    def load(self):
        self.labels.clear()
        AbstractData.load(self)

        try:
            metadata, _ = self.file.loadMMD(True)
        except FileNotFoundError:
            self.complete(False)
            return

        for (name, value) in metadata.items():
            if value is None:
                continue

            self.addLabel(name, Color.parse(value))

        self.complete()

    def save(self):
        AbstractData.save(self)
        metadata = collections.OrderedDict()

        for (name, label) in self.labels.items():
            metadata[name] = label.color

        self.file.save((metadata, None))
        self.complete()
