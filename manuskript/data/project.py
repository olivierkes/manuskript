#!/usr/bin/env python
# --!-- coding: utf8 --!--

# Imports
# Python bundled modules
import os

from zipfile import BadZipFile
# Manuskript modules
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
# This is for the charecter template
from manuskript.data.characters_templates import CharacterDetailTemplates

from manuskript.io.mskFile import MskFile
from manuskript.util import profileTime


class Project:

    def __init__(self, path):
        self.file = MskFile(path)

        self.version = Version(self.file.dir_path)
        self.info = Info(self.file.dir_path)
        self.summary = Summary(self.file.dir_path)
        self.labels = LabelHost(self.file.dir_path)
        self.statuses = StatusHost(self.file.dir_path)
        self.settings = Settings(self.file.dir_path)
        self.characters = Characters(self.file.dir_path)
        self.plots = Plots(self.file.dir_path, self.characters)
        self.world = World(self.file.dir_path)
        self.outline = Outline(self.file.dir_path, self.plots, self.labels, self.statuses)
        self.revisions = Revisions(self.file.dir_path)
        self.character_templates = CharacterDetailTemplates() # TODO: RENAME PROPERALLY

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

    def load(self):
        try:
            self.file.load()
        except BadZipFile or FileNotFoundError:
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

    def save(self):
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
