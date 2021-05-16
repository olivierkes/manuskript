#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os

from collections import OrderedDict
from manuskript.data.color import Color
from manuskript.data.unique_id import UniqueIDHost
from manuskript.io.mmdFile import MmdFile


class Character:

    def __init__(self, path, characters):
        self.file = MmdFile(path, 21)
        self.characters = characters

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

    def allowPOV(self) -> bool:
        return True if self.POV is None else self.POV

    @classmethod
    def loadAttribute(cls, metadata: dict, name: str, defaultValue=None):
        if name in metadata:
            return metadata.pop(name)
        else:
            return defaultValue

    def load(self):
        metadata, _ = self.file.loadMMD(True)

        ID = Character.loadAttribute(metadata, "ID")

        if ID is None:
            raise IOError("Character is missing ID!")

        self.UID = self.characters.host.loadID(int(ID))
        self.name = Character.loadAttribute(metadata, "Name", None)
        self.importance = Character.loadAttribute(metadata, "Importance", None)
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

    def save(self):
        metadata = OrderedDict()

        metadata["Name"] = self.name
        metadata["ID"] = str(self.UID.value)
        metadata["Importance"] = self.importance
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


class Characters:

    def __init__(self, path):
        self.dir_path = os.path.join(path, "characters")
        self.host = UniqueIDHost()
        self.characters = list()

    def load(self):
        self.characters.clear()

        for name in os.listdir(self.dir_path):
            path = os.path.join(self.dir_path, name)

            if not os.path.isfile(path):
                continue

            character = Character(path, self)

            try:
                character.load()
            except FileNotFoundError:
                continue

            self.characters.append(character)

    def save(self):
        for character in self.characters:
            character.save()
