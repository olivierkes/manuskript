#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os

from collections import OrderedDict
from enum import Enum, unique

from manuskript.data.abstractData import AbstractData, DataStatus
from manuskript.data.goal import Goal
from manuskript.data.labels import LabelHost, Label
from manuskript.data.plots import Plots
from manuskript.data.status import StatusHost
from manuskript.data.unique_id import UniqueIDHost
from manuskript.io.mmdFile import MmdFile
from manuskript.util import CounterKind, countText, safeInt


@unique
class OutlineState(Enum):
    UNDEFINED = 0,
    OPTIMIZED = 1,
    COMPLETE = 2


class OutlineItem(AbstractData):

    def __init__(self, path, outline):
        AbstractData.__init__(self, path)
        self.file = MmdFile(self.dataPath)
        self.outline = outline
        self.state = OutlineState.UNDEFINED

        self.UID = None
        self.title = ""
        self.type = ""
        self.summarySentence = None
        self.summaryFull = None
        self.POV = None
        self.notes = None
        self.label = None
        self.status = None
        self.compile = True
        self.goal = None

    def parentItem(self):
        for item in self.outline.all():
            if item.contains(self):
                return item

        return None

    def contains(self, item):
        return False

    @classmethod
    def loadMetadata(cls, item, metadata: dict):
        ID = metadata.get("ID")

        if ID is None:
            return

        if (item.UID is None) or (item.UID.value != int(ID)):
            item.UID = item.outline.host.loadID(int(ID))

        def loadLabelByID(outline, labelID: str) -> Label:
            return outline.labels.getLabelByID(safeInt(labelID, 0))

        def loadStatusByID(outline, statusID: str) -> Label:
            return outline.statuses.getStatusByID(safeInt(statusID, 0))

        item.title = metadata.get("title", None)
        item.type = metadata.get("type", "md")
        item.summarySentence = metadata.get("summarySentence", None)
        item.summaryFull = metadata.get("summaryFull", None)
        item.POV = metadata.get("POV", None)
        item.notes = metadata.get("notes", None)
        item.label = loadLabelByID(item.outline, metadata.get("label", None))
        item.status = loadStatusByID(item.outline, metadata.get("status", None))
        item.compile = metadata.get("compile")
        item.goal = Goal.parse(metadata.get("setGoal", None))

    @classmethod
    def saveMetadata(cls, item):
        metadata = OrderedDict()

        if item.UID is None:
            return metadata

        metadata["title"] = item.title
        metadata["ID"] = str(item.UID.value)
        metadata["type"] = item.type
        metadata["summarySentence"] = item.summarySentence
        metadata["summaryFull"] = item.summaryFull
        metadata["POV"] = item.POV
        metadata["notes"] = item.notes
        metadata["label"] = None if item.label is None else item.label.ID
        metadata["status"] = None if item.status is None else item.status.ID
        metadata["compile"] = item.compile
        metadata["setGoal"] = item.goal

        return metadata

    def textCount(self, counterKind: CounterKind = None) -> int:
        return 0

    def goalKind(self) -> CounterKind:
        return CounterKind.WORDS if self.goal is None else self.goal.kind

    def goalCount(self) -> int:
        return 0 if self.goal is None else self.goal.value

    def complete(self, statusCompletion: bool = True, optimized: bool = True):
        AbstractData.complete(self, statusCompletion)

        if self.dataStatus != DataStatus.LOADED:
            return

        self.state = OutlineState.OPTIMIZED if optimized else OutlineState.COMPLETE

    def load(self, optimized: bool = True):
        AbstractData.load(self)

    def save(self):
        AbstractData.save(self)


class OutlineText(OutlineItem):

    def __init__(self, path, outline):
        OutlineItem.__init__(self, path, outline)

        self.text = ""
        self.cache = dict()

    def textCount(self, counterKind: CounterKind = None) -> int:
        if counterKind is None:
            counterKind = self.goalKind()

        textHash = hash(self.text)
        if textHash not in self.cache:
            self.cache.clear()
            self.cache[textHash] = True

        if counterKind.name not in self.cache:
            self.cache[counterKind.name] = super().textCount(counterKind) + countText(self.text, counterKind)
        return self.cache[counterKind.name]

    def load(self, optimized: bool = True):
        OutlineItem.load(self)

        metadata, body = self.file.loadMMD(optimized)
        OutlineItem.loadMetadata(self, metadata)

        if not optimized:
            self.text = body

        self.complete(optimized=optimized)

    def save(self):
        if self.state == OutlineState.OPTIMIZED:
            self.outline.host.removeID(self.UID)
            self.load(False)

        OutlineItem.save(self)

        metadata = OutlineItem.saveMetadata(self)
        self.file.save((metadata, self.text))
        self.complete()


class OutlineFolder(OutlineItem):

    def __init__(self, path, outline):
        OutlineItem.__init__(self, os.path.join(path, "folder.txt"), outline)

        self.folderPath = path
        self.items = list()

    def __iter__(self):
        return self.items.__iter__()

    def contains(self, item):
        return item in self.items

    @classmethod
    def loadItems(cls, outline, folder, recursive: bool = True):
        folder.items.clear()

        names = os.listdir(folder.folderPath)
        names.remove("folder.txt")
        names.sort()

        for name in names:
            path = os.path.join(folder.folderPath, name)

            if os.path.isdir(path):
                item = OutlineFolder(path, outline)
            else:
                item = OutlineText(path, outline)

            try:
                item.load()
            except FileNotFoundError:
                continue

            folder.items.append(item)

        if recursive:
            for item in filter(lambda outlineItem: type(outlineItem) is OutlineFolder, folder.items):
                cls.loadItems(outline, item, recursive)

    def textCount(self, counterKind: CounterKind = None) -> int:
        if counterKind is None:
            counterKind = self.goalKind()

        count = super().textCount(counterKind)
        count += sum(item.textCount(counterKind) for item in self.items)
        return count

    def goalCount(self) -> int:
        count = super().goalCount()

        if self.goal is None:
            count += sum(item.goalCount() for item in self.items)

        return count

    def load(self, optimized: bool = True):
        OutlineItem.load(self)

        metadata, _ = self.file.loadMMD(True)
        OutlineItem.loadMetadata(self, metadata)

        if not optimized:
            optimized = any(item.state != OutlineState.COMPLETE for item in self.items)

        self.complete(optimized=optimized)

    @classmethod
    def saveItems(cls, folder, recursive: bool = True):
        for item in folder.items:
            item.save()

        if recursive:
            for item in filter(lambda outlineItem: type(outlineItem) is OutlineFolder, folder.items):
                cls.saveItems(item, recursive)

    def save(self):
        self.type = "folder"

        OutlineItem.save(self)

        metadata = OutlineItem.saveMetadata(self)
        self.file.save((metadata, "\n"))
        self.complete()


class Outline(AbstractData):

    def __init__(self, path, plots: Plots, labels: LabelHost, statuses: StatusHost):
        AbstractData.__init__(self, os.path.join(path, "outline"))
        self.host = UniqueIDHost()
        self.plots = plots
        self.labels = labels
        self.statuses = statuses
        self.items = list()
        self.cache = dict()

    def __iter__(self):
        return self.items.__iter__()

    def getItemByID(self, ID: int) -> OutlineItem | None:
        if ID in self.cache:
            return self.cache.get(ID)

        for item in self.all():
            if item.UID.value == ID:
                return item

        return None

    def all(self):
        result = list()
        queue = list(self.items)

        while len(queue) > 0:
            item = queue.pop()
            self.cache[item.UID.value] = item

            if type(item) is OutlineFolder:
                for child in item:
                    queue.append(child)

            result.append(item)

        return result

    def textCount(self, counterKind: CounterKind = None) -> int:
        if counterKind is None:
            counterKind = self.goalKind()

        return sum(item.textCount(counterKind) for item in self.items)

    def goalKind(self) -> CounterKind:
        if len(self.items) > 0:
            return self.items[0].goalKind()

        return CounterKind.WORDS

    def goalCount(self) -> int:
        return sum(item.goalCount() for item in self.items)

    def load(self):
        self.items.clear()
        self.cache.clear()

        AbstractData.load(self)

        if not os.path.isdir(self.dataPath):
            self.complete(False)
            return

        names = os.listdir(self.dataPath)
        names.sort()

        for name in names:
            path = os.path.join(self.dataPath, name)

            if os.path.isdir(path):
                item = OutlineFolder(path, self)
            else:
                item = OutlineText(path, self)

            try:
                item.load()
            except FileNotFoundError:
                continue

            self.items.append(item)

        for item in filter(lambda outlineItem: type(outlineItem) is OutlineFolder, self.items):
            OutlineFolder.loadItems(self, item, True)

        self.complete()

    def save(self):
        AbstractData.save(self)

        if not self.items:
            self.complete()
            return

        os.makedirs(self.dataPath, exist_ok=True)
        for item in self.items:
            item.save()

        for item in filter(lambda outlineItem: type(outlineItem) is OutlineFolder, self.items):
            OutlineFolder.saveItems(item, True)

        self.complete()
