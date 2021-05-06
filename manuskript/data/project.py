#!/usr/bin/env python
# --!-- coding: utf8 --!--

from zipfile import BadZipFile
from manuskript.data.plots import Plots
from manuskript.data.revisions import Revisions
from manuskript.data.settings import Settings
from manuskript.data.status import StatusHost
from manuskript.io.mskFile import MskFile


class Project:

    def __init__(self, path):
        self.file = MskFile(path)

        self.statuses = StatusHost(self.file.dir_path)
        self.settings = Settings(self.file.dir_path)
        self.plots = Plots(self.file.dir_path)
        self.revisions = Revisions(self.file.dir_path)

    def __del__(self):
        del self.file

    def load(self):
        try:
            self.file.load()
        except BadZipFile:
            return
        except FileNotFoundError:
            return

        self.statuses.load()
        self.settings.load()
        self.plots.load()
        self.revisions.load()

        self.file.setZipFile(self.settings.isEnabled("saveToZip"))

    def save(self):
        print("Save project: " + str(self.file.path) + " " + str(self.file.dir_path))

        saveToZip = self.settings.isEnabled("saveToZip")
        self.file.setZipFile(saveToZip)

        self.statuses.save()
        self.settings.save()
        self.plots.save()
        #self.revisions.save()

        self.file.save(saveToZip)
