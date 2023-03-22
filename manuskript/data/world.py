#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os

from manuskript.data.abstractData import AbstractData
from manuskript.data.unique_id import UniqueIDHost, UniqueID
from manuskript.io.opmlFile import OpmlFile, OpmlOutlineItem


class WorldItem:

    def __init__(self, world, UID: UniqueID, name: str = None):
        self.world = world

        if name is None:
            name = "New item"

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


class World(AbstractData):

    def __init__(self, path):
        AbstractData.__init__(self, os.path.join(path, "world.opml"))
        self.file = OpmlFile(self.dataPath)
        self.host = UniqueIDHost()
        self.items = dict()
        self.top = list()

    def addItem(self, name: str = None, parent: WorldItem = None) -> WorldItem:
        item = WorldItem(self, self.host.newID(), name)

        if parent is None:
            self.top.append(item)
        else:
            parent.children.append(item)

        self.items[item.UID.value] = item
        return item

    def loadItem(self, ID: int, name: str = None) -> WorldItem:
        item = WorldItem(self, self.host.loadID(ID), name)
        self.items[item.UID.value] = item
        return item

    def removeItem(self, item: WorldItem):
        for __item in self.items.values():
            if item in __item.children:
                __item.children.remove(item)

        if item in self.top:
            self.top.remove(item)

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
        self.items.clear()
        self.top.clear()

        AbstractData.load(self)

        try:
            outlines = self.file.load()

            for outline in outlines:
                item = World.loadWorldItem(self, outline)

                if item is None:
                    continue

                self.top.append(item)

            self.complete()
        except FileNotFoundError:
            self.complete(False)

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
        AbstractData.save(self)
        outlines = list()

        for item in self.top:
            outlines.append(World.saveWorldItem(item))

        self.file.save(outlines)
        self.complete()
