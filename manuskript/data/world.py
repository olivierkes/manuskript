#!/usr/bin/env python
# --!-- coding: utf8 --!--
from __future__ import annotations
import os

from manuskript.data.abstractData import AbstractData
from manuskript.data.unique_id import UniqueIDHost, UniqueID
from manuskript.io.opmlFile import OpmlFile, OpmlOutlineItem

from typing import Iterator

class WorldItem:

    def __init__(self, world: World, UID: UniqueID, name: str = None):
        self.world: World = world

        if name is None:
            name = "New item"

        self.UID: UniqueID = UID
        self.name: str = name
        self.description: str = None
        self.passion: str = None
        self.conflict: str = None
        self.children: list[WorldItem] = list()

    def remove(self):
        for child in self.children:
            child.remove()

        self.world.removeItem(self)

    def __iter__(self):
        return self.children.__iter__()

    def load(self):
        self.world.load()


class World(AbstractData):

    templates = [
        {
            "name": "Fantasy world building",
            "children": [
                {
                    "name": "Physical",
                    "children": [
                        "Climate",
                        "Topography",
                        "Astronomy",
                        "Natural resources",
                        "Wild life",
                        "Flora",
                        "History",
                        "Races",
                        "Diseases",
                    ]
                },
                {
                    "name": "Cultural",
                    "children": [
                        "Customs",
                        "Food",
                        "Languages",
                        "Education",
                        "Dresses",
                        "Science",
                        "Calendar",
                        "Bodily language",
                        "Ethics",
                        "Religion",
                        "Government",
                        "Politics",
                        "Gender roles",
                        "Music and arts",
                        "Architecture",
                        "Military",
                        "Technology",
                        "Courtship",
                        "Demography",
                        "Transportation",
                        "Medicine",
                    ]
                },
                {
                    "name": "Magic system",
                    "children": [
                        "Rules",
                        "Organization",
                        "Magical objects",
                        "Magical places",
                        "Magical races",
                    ]
                },
                "Important places",
                "Important objects",
            ]
        }
    ]

    def __init__(self, path: str):
        AbstractData.__init__(self, os.path.join(path, "world.opml"))

        host: UniqueIDHost
        items: dict[int, WorldItem]
        top = list[WorldItem]

        self.file: OpmlFile = OpmlFile(self.dataPath)
        self.host = UniqueIDHost()
        self.items: dict[int, WorldItem] = dict()
        self.top: list[WorldItem] = list()

    def changePath(self, path: str):
        AbstractData.changePath(self, os.path.join(path, "world.opml"))
        self.file = OpmlFile(self.dataPath)

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

    def moveItem(self, item: WorldItem, parent: WorldItem = None, index: int | None = None):
        if parent and self.contains(item, parent):
            return
                
        __parent = self.findParent(item)

        if __parent:
            __parent.children.remove(item)
        else:
            self.top.remove(item)

        if parent is None:
            if index is None:
                self.top.append(item)
            else:
                self.top.insert(index, item)
        else:
            if index is None:
                parent.children.append(item)
            else:
                parent.children.insert(index, item)

    def getItemByID(self, ID: int) -> WorldItem:
        return self.items.get(ID, None)

    def __iter__(self) -> Iterator[WorldItem]:
        return self.items.values().__iter__()

    @classmethod
    def loadWorldItem(cls, world: World, outline: OpmlOutlineItem) -> WorldItem:
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

    def fetchTemplateList(self):
        return [node["name"] if isinstance(node, dict) else node for node in self.templates]

    def _insertTemplate(self, node: str | dict, parent:WorldItem=None):
        if isinstance(node, str):
            self.addItem(name=node, parent=parent)
        elif isinstance(node, dict):
            worldItem = self.addItem(name=node["name"])

            for child in node.get("children", []):
                self._insertTemplate(child, parent=worldItem)

    def insertTemplate(self, templateName: str):
        root = next(
            (node for node in self.templates if isinstance(node, dict) and node["name"] == templateName),
            None
        )

        if root is not None:
            for node in root["children"]:
                self._insertTemplate(node)

    def contains(self, source: WorldItem, target: WorldItem | None) -> bool:
        if target is None:
            return False

        stack = list(source.children)
        while stack:
            node = stack.pop()
            if node is target:
                return True
            
            stack.extend(node.children)
        return False
    
    def findParent(self, item: WorldItem) -> WorldItem | None:
        stack = list(self.top)

        while stack:
            current = stack.pop()
            if item in current.children:
                return current

            stack.extend(current.children)
        return None
    
    