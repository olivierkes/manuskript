#!/usr/bin/env python
# --!-- coding: utf8 --!--

import collections
import os
from typing import Iterator

from manuskript.data.abstractData import AbstractData
from manuskript.data.color import Color
from manuskript.io.mmdFile import MmdFile


class Label:
    def __init__(self, host: LabelHost, index: int, name: str, color: Color) -> None:
        self.host = host
        self.ID = index

        self.name = name
        self.color = color

    def __str__(self) -> str:
        return self.name

    def load(self) -> None:
        self.host.load()

    def save(self) -> None:
        self.host.save()


class LabelHost(AbstractData):
    def __init__(self, path) -> None:
        AbstractData.__init__(self, os.path.join(path, "labels.txt"))
        self.file = MmdFile(self.dataPath, 21)
        self.labels: collections.OrderedDict[str, Label] = collections.OrderedDict()

    def changePath(self, path: str) -> None:
        AbstractData.changePath(self, os.path.join(path, "labels.txt"))
        self.file = MmdFile(self.dataPath, 21)

    def addLabel(self, name: str | None = None, color: Color | None = None) -> Label:
        if name is None:
            name = "New Label"

        if color is None:
            color = Color(0, 0, 0)

        label = Label(self, 1 + len(self.labels), name, color)
        self.labels[name] = label
        return label

    def removeLabel(self, name: str) -> Label:
        return self.labels.pop(name)

    def renameLabel(self, oldName: str, newName: str) -> None:
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

    def getLabel(self, name: str) -> Label | None:
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

    def __iter__(self) -> Iterator[Label]:
        return self.labels.values().__iter__()

    def load(self) -> None:
        self.labels.clear()
        AbstractData.load(self)

        try:
            metadata, _ = self.file.loadMMD(True)
        except FileNotFoundError:
            self.complete(False)
            return

        for name, value in metadata.items():
            if value is None:
                continue

            self.addLabel(name, Color.parse(value))

        self.complete()

    def save(self) -> None:
        AbstractData.save(self)
        metadata = collections.OrderedDict()

        for name, label in self.labels.items():
            metadata[name] = label.color

        self.file.save((metadata, None))
        self.complete()
