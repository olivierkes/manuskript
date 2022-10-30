#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os

from manuskript.data.unique_id import UniqueIDHost, UniqueID
from manuskript.io.opmlFile import OpmlFile, OpmlOutlineItem


class WorldItem:

    def __init__(self, world, UID: UniqueID, name: str):
        self.world = world

        self.UID = UID
        self.name = name
        self.description = None
        self.passion = None
        self.conflict = None
        self.children = list()

    def remove(self):
        for child in self.children:
            child.remove()

        self.world.removeItem(self)

    def __iter__(self):
        return self.children.__iter__()

    def load(self):
        self.world.load()


class World:

    def __init__(self, path):
        self.file = OpmlFile(os.path.join(path, "world.opml"))
        self.host = UniqueIDHost()
        self.items = dict()
        self.top = list()

    def addItem(self, name: str) -> WorldItem:
        item = WorldItem(self, self.host.newID(), name)
        self.items[item.UID.value] = item
        return item

    def loadItem(self, ID: int, name: str) -> WorldItem:
        item = WorldItem(self, self.host.loadID(ID), name)
        self.items[item.UID.value] = item
        return item

    def removeItem(self, item: WorldItem):
        self.host.removeID(item.UID)
        self.items.pop(item.UID.value)

    def getItemByID(self, ID: int) -> WorldItem:
        return self.items.get(ID, None)

    def __iter__(self):
        return self.items.values().__iter__()

    @classmethod
    def loadWorldItem(cls, world, outline: OpmlOutlineItem):
        ID = outline.attributes.get("ID", None)

        if ID is None:
            return None

        item = world.loadItem(int(ID), outline.attributes.get("name", None))

        item.description = outline.attributes.get("description", None)
        item.passion = outline.attributes.get("passion", None)
        item.conflict = outline.attributes.get("conflict", None)

        for child in outline.children:
            childItem = cls.loadWorldItem(world, child)

            if childItem is None:
                continue

            item.children.append(childItem)

        return item

    def load(self):
        try:
            outlines = self.file.load()

            self.items.clear()
            self.top.clear()

            for outline in outlines:
                item = World.loadWorldItem(self, outline)

                if item is None:
                    continue

                self.top.append(item)
        except FileNotFoundError:
            self.items.clear()
            self.top.clear()

    @classmethod
    def saveWorldItem(cls, item: WorldItem):
        outline = OpmlOutlineItem()

        outline.attributes["name"] = item.name
        outline.attributes["ID"] = str(item.UID.value)
        outline.attributes["description"] = item.description
        outline.attributes["passion"] = item.passion
        outline.attributes["conflict"] = item.conflict

        for childItem in item.children:
            outline.children.append(cls.saveWorldItem(childItem))

        return outline

    def save(self):
        outlines = list()

        for item in self.top:
            outlines.append(World.saveWorldItem(item))

        self.file.save(outlines)
