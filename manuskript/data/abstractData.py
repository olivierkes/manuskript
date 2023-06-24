#!/usr/bin/env python
# --!-- coding: utf8 --!--

from enum import Enum, unique


@unique
class DataStatus(Enum):
    UNDEFINED = 0
    CHANGED = 1
    LOADING = 2
    LOADED = 3
    SAVING = 4
    SAVED = 5


class AbstractData:

    def __init__(self, path):
        self.dataPath = path
        self.dataStatus = DataStatus.UNDEFINED

    def changePath(self, path: str):
        print("{} -> {}".format(self.dataPath, path))

        self.dataPath = path

    def complete(self, statusCompletion: bool = True):
        if self.dataStatus == DataStatus.LOADING:
            self.dataStatus = DataStatus.LOADED if statusCompletion else DataStatus.UNDEFINED
        elif self.dataStatus == DataStatus.SAVING:
            self.dataStatus = DataStatus.SAVED

    def load(self):
        self.dataStatus = DataStatus.LOADING

    def save(self):
        self.dataStatus = DataStatus.SAVING
