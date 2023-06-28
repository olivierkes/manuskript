#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os

from collections import OrderedDict

from manuskript.data.abstractData import AbstractData
from manuskript.data.color import Color
from manuskript.data.importance import Importance
from manuskript.data.links import LinkAction, Links
from manuskript.data.unique_id import UniqueIDHost
from manuskript.io.mmdFile import MmdFile
from manuskript.util import safeFilename


class Character(AbstractData):

    def __init__(self, path, characters):
        AbstractData.__init__(self, path)
        self.file = MmdFile(self.dataPath, 21)
        self.characters = characters
        self.links = Links()

        self.UID = None
        self.name = None
        self.importance = None
        self.POV = None
        self.motivation = None
        self.goal = None
        self.conflict = None
        self.epiphany = None
        self.summarySentence = None
        self.summaryParagraph = None
        self.summaryFull = None
        self.notes = None
        self.color = None
        self.details = dict()

    def changePath(self, path: str):
        AbstractData.changePath(self, path)
        self.file = MmdFile(self.dataPath, 21)

    def allowPOV(self) -> bool:
        return True if self.POV is None else self.POV

    def remove(self):
        self.links.call(LinkAction.DELETE, self.UID, self)
        self.characters.remove(self)

    @classmethod
    def loadAttribute(cls, metadata: dict, name: str, defaultValue=None):
        if name in metadata:
            return metadata.pop(name)
        else:
            return defaultValue

    def load(self):
        AbstractData.load(self)

        metadata, _ = self.file.loadMMD(True)

        ID = Character.loadAttribute(metadata, "ID")

        if ID is None:
            raise IOError("Character is missing ID!")

        importance = Character.loadAttribute(metadata, "Importance", None)

        self.UID = self.characters.host.loadID(int(ID))
        self.name = Character.loadAttribute(metadata, "Name", None)
        self.importance = Importance.fromRawString(importance)
        self.POV = Character.loadAttribute(metadata, "POV", None)
        self.motivation = Character.loadAttribute(metadata, "Motivation", None)
        self.goal = Character.loadAttribute(metadata, "Goal", None)
        self.conflict = Character.loadAttribute(metadata, "Conflict", None)
        self.epiphany = Character.loadAttribute(metadata, "Epiphany", None)
        self.summarySentence = Character.loadAttribute(metadata, "Phrase Summary", None)
        self.summaryParagraph = Character.loadAttribute(metadata, "Paragraph Summary", None)
        self.summaryFull = Character.loadAttribute(metadata, "Full Summary", None)
        self.notes = Character.loadAttribute(metadata, "Notes", None)
        self.color = Color.parse(Character.loadAttribute(metadata, "Color", None))

        self.details.clear()

        for (key, value) in metadata.items():
            self.details[key] = value

        self.links.call(LinkAction.RELOAD, self.UID, self)
        self.complete()

    def save(self):
        AbstractData.save(self)

        metadata = OrderedDict()

        metadata["Name"] = self.name
        metadata["ID"] = str(self.UID.value)
        metadata["Importance"] = Importance.toRawString(self.importance)
        metadata["POV"] = self.POV
        metadata["Motivation"] = self.motivation
        metadata["Goal"] = self.goal
        metadata["Conflict"] = self.conflict
        metadata["Epiphany"] = self.epiphany
        metadata["Phrase Summary"] = self.summarySentence
        metadata["Paragraph Summary"] = self.summaryParagraph
        metadata["Full Summary"] = self.summaryFull
        metadata["Notes"] = self.notes
        metadata["Color"] = self.color

        for (key, value) in self.details.items():
            if not (key in metadata):
                metadata[key] = value

        self.file.save((metadata, None))
        self.complete()


class Characters(AbstractData):

    def __init__(self, path):
        AbstractData.__init__(self, os.path.join(path, "characters"))
        self.host = UniqueIDHost()
        self.data = dict()

    def changePath(self, path: str):
        AbstractData.changePath(self, os.path.join(path, "characters"))

        for character in self.data.values():
            filename = safeFilename("%s-%s" % (str(character.UID), character.name), "txt")
            path_ = os.path.join(self.dataPath, filename)

            character.changePath(path_)

    def __iter__(self):
        return self.data.values().__iter__()

    def add(self, name: str = None) -> Character | None:
        if name is None:
            name = "New character"

        UID = self.host.newID()
        filename = safeFilename("%s-%s" % (str(UID), name), "txt")

        path = os.path.join(self.dataPath, filename)

        if os.path.exists(filename):
            return None

        character = Character(path, self)
        character.UID = UID
        character.name = name

        self.data[character.UID.value] = character

        return character

    def getByID(self, ID: int) -> Character:
        return self.data.get(ID, None)

    def remove(self, character: Character):
        self.host.removeID(character.UID)
        self.data.pop(character.UID.value)

    def load(self):
        self.data.clear()
        AbstractData.load(self)

        if not os.path.isdir(self.dataPath):
            self.complete(False)
            return

        for filename in os.listdir(self.dataPath):
            path = os.path.join(self.dataPath, filename)

            if not os.path.isfile(path):
                continue

            character = Character(path, self)

            try:
                character.load()
            except FileNotFoundError:
                continue

            self.data[character.UID.value] = character

        self.complete()

    def save(self):
        AbstractData.save(self)

        if not self.data:
            return

        os.makedirs(self.dataPath, exist_ok=True)
        for character in self.data.values():
            character.save()

        self.complete(False)
