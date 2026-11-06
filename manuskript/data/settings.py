#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os
from typing import Iterator

from manuskript.data.abstractData import AbstractData
from manuskript.io.jsonFile import JsonFile


class Settings(AbstractData):
    def __init__(self, path: str, initDefault: bool = True) -> None:
        AbstractData.__init__(self, os.path.join(path, "settings.txt"))
        self.file = JsonFile(self.dataPath)
        self.properties: dict[str, any] = dict()

        if initDefault:
            Settings.loadDefaultSettings(self)

    def changePath(self, path: str) -> None:
        AbstractData.changePath(self, os.path.join(path, "settings.txt"))
        self.file = JsonFile(self.dataPath)

    def get(self, key: str) -> any | None:
        props = self.properties
        path = key.split(".")

        for part in path[:-1]:
            props = props.get(part)

        return props.get(path[-1:][0])

    def isEnabled(self, key: str) -> bool:
        return self.properties.get(key, False) is True

    def set(self, key: str, value: any | None) -> None:
        props = self.properties
        path = key.split(".")

        for part in path[:-1]:
            props = props.get(part)

        props[path[-1:][0]] = value

    def __iter__(self) -> Iterator[str]:
        return self.properties.__iter__()

    @classmethod
    def loadDefaultSettings(cls, settings: Settings) -> None:
        settings.properties = {
            "autoSave": False,
            "autoSaveDelay": 5,
            "autoSaveNoChanges": True,
            "autoSaveNoChangesDelay": 5,
            "corkBackground": {"color": "#926239", "image": "writingdesk.jpg"},
            "corkSizeFactor": 84,
            "corkStyle": "new",
            "defaultTextType": "md",
            "dict": "en_US",
            "dontShowDeleteWarning": False,
            "folderView": "cork",
            "frequencyAnalyzer": {
                "phraseMax": 5,
                "phraseMin": 2,
                "wordExclude": "a, and, or",
                "wordMin": 1,
            },
            "fullScreenTheme": "gentleblues",
            "lastTab": 6,
            "openIndexes": [None],
            "outlineViewColumns": [0, 8, 9, 11, 12, 13, 7],
            "revisions": {
                "keep": True,
                "rules": {"2592000": 86400, "3600": 600, "600": 60, "86400": 3600, "null": 604800},
                "smartremove": True,
            },
            "saveOnQuit": True,
            "saveToZip": False,
            "spellcheck": False,
            "textEditor": {
                "background": "#fff",
                "backgroundTransparent": False,
                "cursorNotBlinking": False,
                "cursorWidth": 1,
                "font": "DejaVu Sans,10,-1,5,50,0,0,0,0,0",
                "fontColor": "#000",
                "indent": True,
                "lineSpacing": 100,
                "marginsLR": 0,
                "marginsTB": 0,
                "maxWidth": 0,
                "misspelled": "#F00",
                "spacingAbove": 5,
                "spacingBelow": 5,
                "tabWidth": 20,
                "textAlignment": 0,
            },
            "viewMode": "fiction",
            "viewSettings": {
                "Cork": {
                    "Background": "Nothing",
                    "Border": "Nothing",
                    "Corner": "Label",
                    "Icon": "Nothing",
                    "Text": "Nothing",
                },
                "Outline": {"Background": "Nothing", "Icon": "Nothing", "Text": "Compile"},
                "Tree": {
                    "Background": "Nothing",
                    "Icon": "Nothing",
                    "InfoFolder": "Summary",
                    "InfoText": "Nothing",
                    "Text": "Compile",
                    "iconSize": 24,
                },
            },
        }

    def load(self) -> None:
        AbstractData.load(self)

        try:
            self.properties = self.file.load()
        except FileNotFoundError:
            Settings.loadDefaultSettings(self)

        self.complete()

    def save(self) -> None:
        AbstractData.save(self)

        self.file.save(self.properties)
        self.complete()
