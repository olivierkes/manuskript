#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os

from zipfile import BadZipFile

from manuskript.data.abstractData import AbstractData
from manuskript.data.version import Version, CURRENT_MSK_VERSION
from manuskript.data.info import Info
from manuskript.data.summary import Summary
from manuskript.data.labels import LabelHost
from manuskript.data.status import StatusHost
from manuskript.data.settings import Settings
from manuskript.data.characters import Characters
from manuskript.data.plots import Plots
from manuskript.data.world import World
from manuskript.data.outline import Outline
from manuskript.data.revisions import Revisions
from manuskript.io.mskFile import MskFile
from manuskript.util import profileTime


class Project(AbstractData):

    def __init__(self, path: str):
        AbstractData.__init__(self, path)
        self.file = MskFile(self.dataPath)

        self.version = Version(self.file.directoryPath)
        self.info = Info(self.file.directoryPath)
        self.summary = Summary(self.file.directoryPath)
        self.labels = LabelHost(self.file.directoryPath)
        self.statuses = StatusHost(self.file.directoryPath)
        self.settings = Settings(self.file.directoryPath)
        self.characters = Characters(self.file.directoryPath)
        self.plots = Plots(self.file.directoryPath, self.characters)
        self.world = World(self.file.directoryPath)
        self.outline = Outline(self.file.directoryPath, self.plots, self.labels, self.statuses)
        self.revisions = Revisions(self.file.directoryPath)

    def __del__(self):
        del self.file

    def getName(self):
        parts = os.path.split(self.file.path)
        name = parts[-1]

        if name.endswith('.msk'):
            name = name[:-4]

        return name

    def getVersion(self) -> int:
        return self.version.value

    def canUpgradeVersion(self) -> bool:
        return self.version.value < CURRENT_MSK_VERSION

    def upgradeVersion(self):
        self.version.value = CURRENT_MSK_VERSION

    def changePath(self, path: str):
        AbstractData.changePath(self, path)
        saveToZip = self.settings.isEnabled("saveToZip")

        self.file = MskFile(self.dataPath, ignorePath=True, forceZip=saveToZip)
        os.makedirs(self.file.directoryPath, exist_ok=True)

        self.version.changePath(self.file.directoryPath)
        self.info.changePath(self.file.directoryPath)
        self.summary.changePath(self.file.directoryPath)
        self.labels.changePath(self.file.directoryPath)
        self.statuses.changePath(self.file.directoryPath)
        self.settings.changePath(self.file.directoryPath)
        self.characters.changePath(self.file.directoryPath)
        self.plots.changePath(self.file.directoryPath)
        self.world.changePath(self.file.directoryPath)
        self.outline.changePath(self.file.directoryPath)
        self.revisions.changePath(self.file.directoryPath)

    def load(self):
        AbstractData.load(self)

        try:
            self.file.load()
        except BadZipFile or FileNotFoundError:
            self.complete(False)
            return

        profileTime(self.version.load)
        profileTime(self.info.load)
        profileTime(self.summary.load)
        profileTime(self.labels.load)
        profileTime(self.statuses.load)
        profileTime(self.settings.load)
        profileTime(self.characters.load)
        profileTime(self.plots.load)
        profileTime(self.world.load)
        profileTime(self.outline.load)
        profileTime(self.revisions.load)

        self.file.setZipFile(self.settings.isEnabled("saveToZip"))
        self.complete()

    def save(self):
        AbstractData.save(self)
        saveToZip = self.settings.isEnabled("saveToZip")

        self.file.setZipFile(saveToZip)
        self.file.setVersion(self.version.value)

        self.version.save()
        self.info.save()
        self.summary.save()
        self.labels.save()
        self.statuses.save()
        self.settings.save()
        self.characters.save()
        self.plots.save()
        self.world.save()
        self.outline.save()
        #self.revisions.save()

        self.file.save(saveToZip)
        self.complete()
