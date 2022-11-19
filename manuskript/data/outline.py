#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os

from collections import OrderedDict
from enum import Enum, unique
from manuskript.data.goal import Goal
from manuskript.data.labels import LabelHost, Label
from manuskript.data.plots import Plots
from manuskript.data.status import StatusHost, Status
from manuskript.data.unique_id import UniqueIDHost
from manuskript.io.mmdFile import MmdFile
from manuskript.util import CounterKind, countText, safeInt


@unique
class OutlineState(Enum):
    UNDEFINED = 0,
    OPTIMIZED = 1,
    COMPLETE = 2


class OutlineItem:

    def __init__(self, path, outline):
        self.file = MmdFile(path)
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
        metadata["label"] = None if item is None else item.label.ID
        metadata["status"] = None if item is None else item.status.ID
        metadata["compile"] = item.compile
        metadata["setGoal"] = item.goal

        return metadata

    def textCount(self, counterKind: CounterKind = None) -> int:
        return 0

    def goalKind(self) -> CounterKind:
        return CounterKind.WORDS if self.goal is None else self.goal.kind

    def goalCount(self) -> int:
        return 0 if self.goal is None else self.goal.value

    def load(self, optimized: bool = True):
        raise IOError('Loading undefined!')

    def save(self):
        raise IOError('Saving undefined!')


class OutlineText(OutlineItem):

    def __init__(self, path, outline):
        OutlineItem.__init__(self, path, outline)

        self.text = ""

    def textCount(self, counterKind: CounterKind = None) -> int:
        if counterKind is None:
            counterKind = self.goalKind()

        return super().textCount(counterKind) + countText(self.text, counterKind)

    def load(self, optimized: bool = True):
        metadata, body = self.file.loadMMD(optimized)
        OutlineItem.loadMetadata(self, metadata)

        if not optimized:
            self.text = body
            self.state = OutlineState.COMPLETE
        elif self.state == OutlineState.UNDEFINED:
            self.state = OutlineState.OPTIMIZED

    def save(self):
        if self.state == OutlineState.OPTIMIZED:
            self.outline.host.removeID(self.UID)
            self.load(False)

        metadata = OutlineItem.saveMetadata(self)
        self.file.save((metadata, self.text))


class OutlineFolder(OutlineItem):

    def __init__(self, path, outline):
        self.dir_path = path
        self.items = list()

        OutlineItem.__init__(self, os.path.join(self.dir_path, "folder.txt"), outline)

    def __iter__(self):
        return self.items.__iter__()

    def contains(self, item):
        return item in self.items

    @classmethod
    def loadItems(cls, outline, folder, recursive: bool = True):
        folder.items.clear()

        names = os.listdir(folder.dir_path)
        names.remove("folder.txt")
        names.sort()

        for name in names:
            path = os.path.join(folder.dir_path, name)

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
            for item in folder.items:
                if type(item) is OutlineFolder:
                    cls.loadItems(outline, item, recursive)

    def textCount(self, counterKind: CounterKind = None) -> int:
        if counterKind is None:
            counterKind = self.goalKind()

        count = super().textCount(counterKind)

        for item in self.items:
            count += item.textCount(counterKind)

        return count

    def goalCount(self) -> int:
        count = super().goalCount()

        if self.goal is None:
            for item in self.items:
                count += item.goalCount()

        return count

    def load(self, _: bool = True):
        metadata, _ = self.file.loadMMD(True)
        OutlineItem.loadMetadata(self, metadata)
        self.state = OutlineState.COMPLETE

    @classmethod
    def saveItems(cls, folder, recursive: bool = True):
        for item in folder.items:
            item.save()

        if recursive:
            for item in folder.items:
                if type(item) is OutlineFolder:
                    cls.saveItems(item, recursive)

    def save(self):
        self.type = "folder"
        metadata = OutlineItem.saveMetadata(self)
        self.file.save((metadata, "\n"))


class Outline:

    def __init__(self, path, plots: Plots, labels: LabelHost, statuses: StatusHost):
        self.dir_path = os.path.join(path, "outline")
        self.host = UniqueIDHost()
        self.plots = plots
        self.labels = labels
        self.statuses = statuses
        self.items = list()

    def __iter__(self):
        return self.items.__iter__()

    def getItemByID(self, ID: int) -> OutlineItem | None:
        for item in self.all():
            if item.UID.value == ID:
                return item

        return None

    def all(self):
        result = list()
        queue = list(self.items)

        while len(queue) > 0:
            item = queue.pop()

            if type(item) is OutlineFolder:
                for child in item:
                    queue.append(child)

            result.append(item)

        return result

    def textCount(self, counterKind: CounterKind = None) -> int:
        if counterKind is None:
            counterKind = self.goalKind()

        count = 0
        for item in self.items:
            count += item.textCount(counterKind)

        return count

    def goalKind(self) -> CounterKind:
        if len(self.items) > 0:
            return self.items[0].goalKind()

        return CounterKind.WORDS

    def goalCount(self) -> int:
        count = 0
        for item in self.items:
            count += item.goalCount()

        return count

    def load(self):
        self.items.clear()

        names = os.listdir(self.dir_path)
        names.sort()

        for name in names:
            path = os.path.join(self.dir_path, name)

            if os.path.isdir(path):
                item = OutlineFolder(path, self)
            else:
                item = OutlineText(path, self)

            try:
                item.load()
            except FileNotFoundError:
                continue

            self.items.append(item)

        for item in self.items:
            if type(item) is OutlineFolder:
                OutlineFolder.loadItems(self, item, True)

    def save(self):
        for item in self.items:
            item.save()

        for item in self.items:
            if type(item) is OutlineFolder:
                OutlineFolder.saveItems(item, True)
