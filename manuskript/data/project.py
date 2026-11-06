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
from manuskript.util import profileTime, validVariantValue


class Project(AbstractData):
    def __init__(self, path: str) -> None:
        AbstractData.__init__(self, path)
        self.file: MskFile = MskFile(self.dataPath)

        self.version: Version = Version(self.file.directoryPath)
        self.info: Info = Info(self.file.directoryPath)
        self.summary: Summary = Summary(self.file.directoryPath)
        self.labels: LabelHost = LabelHost(self.file.directoryPath)
        self.statuses: StatusHost = StatusHost(self.file.directoryPath)
        self.settings: Settings = Settings(self.file.directoryPath)
        self.characters: Characters = Characters(self.file.directoryPath)
        self.plots: Plots = Plots(self.file.directoryPath, self.characters)
        self.world: World = World(self.file.directoryPath)
        self.outline: Outline = Outline(
            self.file.directoryPath, self.characters, self.plots, self.labels, self.statuses
        )
        self.revisions: Revisions = Revisions(self.file.directoryPath)

        self.version.value = self.file.getVersion()
        self.settings.set("saveToZip", self.file.isZipFile())

    def __del__(self) -> None:
        del self.file

    def getName(self) -> str:
        parts = os.path.split(self.file.path)
        name = parts[-1]

        if name.endswith(".msk"):
            name = name[:-4]

        return name

    def getVersion(self) -> int:
        return validVariantValue(self.version)

    def canUpgradeVersion(self) -> bool:
        return self.getVersion() < CURRENT_MSK_VERSION

    def upgradeVersion(self) -> None:
        self.version.value = CURRENT_MSK_VERSION

    def changePath(self, path: str) -> None:
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

    def load(self) -> None:
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

    def save(self) -> None:
        AbstractData.save(self)
        saveToZip = self.settings.isEnabled("saveToZip")

        self.file.setZipFile(saveToZip)
        self.file.setVersion(self.getVersion())

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
        # self.revisions.save()

        self.file.save(saveToZip)
        self.complete()
