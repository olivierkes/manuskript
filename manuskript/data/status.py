#!/usr/bin/env python
# --!-- coding: utf8 --!--

import collections
import os
from typing import Iterator

from manuskript.data.abstractData import AbstractData
from manuskript.io.textFile import TextFile


class Status:
    def __init__(self, host: StatusHost, index: int, name: str) -> None:
        self.host = host
        self.ID = index

        self.name = name

    def __str__(self) -> str:
        return self.name

    def load(self) -> None:
        self.host.load()

    def save(self) -> None:
        self.host.save()


class StatusHost(AbstractData):
    def __init__(self, path: str) -> None:
        AbstractData.__init__(self, os.path.join(path, "status.txt"))
        self.file = TextFile(self.dataPath)
        self.statuses = collections.OrderedDict()

    def changePath(self, path: str) -> None:
        AbstractData.changePath(self, os.path.join(path, "status.txt"))
        self.file = TextFile(self.dataPath)

    def addStatus(self, name: str | None = None) -> Status:
        if name is None:
            name = "New Status"

        status = Status(self, 1 + len(self.statuses), name)
        self.statuses[name] = status
        return status

    def removeStatus(self, name: str) -> Status:
        return self.statuses.pop(name)

    def renameStatus(self, oldName: str, newName: str) -> None:
        match = False
        drop = [oldName]

        for name, status in self.statuses.items():
            if match:
                drop.append(name)
            elif name == oldName:
                status.name = newName
                match = True

        if not match:
            return

        statuses = list()
        for name in drop:
            statuses.append(self.statuses.pop(name))

        for status in statuses:
            self.statuses[status.name] = status

    def getStatus(self, name: str) -> Status | None:
        return self.statuses.get(name)

    def getStatusByID(self, ID: int | None) -> Status | None:
        if ID is None:
            return None

        index = 1
        for status in self.statuses.values():
            if index == ID:
                assert status.ID == ID
                return status

            index += 1

        return None

    def __iter__(self) -> Iterator[Status]:
        return self.statuses.values().__iter__()

    def load(self) -> None:
        self.statuses.clear()

        AbstractData.load(self)

        try:
            text = self.file.load()
        except FileNotFoundError:
            self.complete(False)
            return

        if (len(text) <= 1) or (text[len(text) - 1] != "\n"):
            self.complete(False)
            return

        text = text[:-1]
        if len(text) <= 0:
            self.complete(False)
            return

        for name in text.split("\n"):
            self.addStatus(name)

        self.complete()

    def save(self) -> None:
        AbstractData.save(self)

        self.file.save("\n".join(self.statuses.keys()) + "\n")
        self.complete()
