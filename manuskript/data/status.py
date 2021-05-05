#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os

from manuskript.io.textFile import TextFile


class Status:

    def __init__(self, host, name: str):
        self.host = host

        self.name = name

    def __str__(self):
        return self.name

    def load(self):
        self.host.load()

    def save(self):
        self.host.save()


class StatusHost:

    def __init__(self, path):
        self.file = TextFile(os.path.join(path, "status.txt"))
        self.statuses = dict()

    def addStatus(self, name: str):
        self.statuses[name] = Status(self, name)

    def removeStatus(self, name: str):
        self.statuses.pop(name)

    def renameStatus(self, oldName: str, newName: str):
        status = self.statuses.get(oldName)
        status.name = newName
        self.statuses[newName] = status
        self.statuses.pop(oldName)

    def getStatus(self, name: str):
        return self.statuses.get(name)

    def __iter__(self):
        return self.statuses.values().__iter__()

    def load(self):
        text = self.file.load()
        self.statuses.clear()

        if len(text) <= 1:
            return

        text = text[:-1]

        if len(text) <= 0:
            return

        for name in text.split("\n"):
            self.addStatus(name)

    def save(self):
        self.file.save("\n".join(self.statuses.keys()) + "\n")
