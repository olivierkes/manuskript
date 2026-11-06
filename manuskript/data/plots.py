#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os
from typing import Any, Iterator, Optional

from lxml import etree

from manuskript.data.abstractData import AbstractData
from manuskript.data.characters import Characters, Character
from manuskript.data.importance import Importance
from manuskript.data.links import LinkAction, Links
from manuskript.data.unique_id import UniqueIDHost, UniqueID
from manuskript.io.xmlFile import XmlFile


class PlotStep:
    def __init__(
        self, plot: PlotLine, UID: UniqueID, name: str, meta: Optional[str] = None, summary: Optional[str] = None
    ) -> None:
        self.plot = plot

        self.UID: UniqueID = UID
        self.name: Optional[str] = name
        self.meta: Optional[str] = meta
        self.summary: Optional[str] = summary

    def save(self) -> None:
        self.plot.save()


class PlotLine:
    def __init__(
        self,
        plots: Plots,
        UID: UniqueID,
        name: str | None = None,
        importance: Importance = Importance.MINOR,
    ) -> None:
        self.plots = plots
        self.host = UniqueIDHost()
        self.links = Links()

        if name is None:
            name = "New plot"

        self.UID: UniqueID = UID
        self.name: Optional[str] = name
        self.importance: Importance = importance
        self.characters: list[int] = list()
        self.description: Optional[str] = None
        self.result: Optional[str] = None
        self.steps: list[PlotStep] = list()

    def __linkActionCharacter(
        self, action: LinkAction, UID: UniqueID, character: Character
    ) -> None:
        if action == LinkAction.DELETE:
            self.removeCharacter(character, False)

        self.links.call(LinkAction.UPDATE, self.UID, self)

    def addCharacter(self, character: Character) -> None:
        if (character is None) or (character.UID is None):
            return

        character.links.add(self.__linkActionCharacter)

        self.characters.append(character.UID.value)
        self.links.call(LinkAction.UPDATE, self.UID, self)

    def removeCharacter(self, character: Character, unlink: bool = True) -> None:
        if (character is None) or (character.UID is None):
            return

        if unlink:
            character.links.remove(self.__linkActionCharacter)

        self.characters.remove(character.UID.value)
        self.links.call(LinkAction.UPDATE, self.UID, self)

    def addStep(self, name: str, meta: Optional[str] = None, summary: Optional[str] = None) -> PlotStep:
        step = PlotStep(self, self.host.newID(), name, meta, summary)
        self.steps.append(step)

        self.links.call(LinkAction.UPDATE, self.UID, self)
        return step

    def loadStep(self, ID: int, name: str, meta: Optional[str] = None, summary: Optional[str] = None) -> PlotStep:
        step = PlotStep(self, self.host.loadID(ID), name, meta, summary)
        self.steps.append(step)

        self.links.call(LinkAction.UPDATE, self.UID, self)
        return step

    def removeStep(self, step: PlotStep) -> None:
        self.host.removeID(step.UID)
        self.steps.remove(step)

        self.links.call(LinkAction.UPDATE, self.UID, self)

    def getStepByID(self, ID: int) -> PlotStep | None:
        for step in self.steps:
            if step.UID.value == ID:
                return step

        return None

    def __iter__(self) -> Iterator[PlotStep]:
        return self.steps.__iter__()

    def save(self) -> None:
        self.plots.save()


class Plots(AbstractData):
    def __init__(self, path: str, characters: Characters) -> None:
        AbstractData.__init__(self, os.path.join(path, "plots.xml"))
        self.file = XmlFile(self.dataPath)
        self.host = UniqueIDHost()
        self.characters = characters
        self.lines = dict()

    def changePath(self, path: str) -> None:
        AbstractData.changePath(self, os.path.join(path, "plots.xml"))
        self.file = XmlFile(self.dataPath)

    def addLine(
        self, name: str | None = None, importance: Importance = Importance.MINOR
    ) -> PlotLine:
        line = PlotLine(self, self.host.newID(), name, importance)
        self.lines[line.UID.value] = line
        return line

    def loadLine(
        self, ID: int, name: str | None = None, importance: Importance = Importance.MINOR
    ) -> PlotLine:
        line = PlotLine(self, self.host.loadID(ID), name, importance)
        self.lines[line.UID.value] = line

        line.links.call(LinkAction.RELOAD, line.UID, line)
        return line

    def removeLine(self, line: PlotLine) -> None:
        line.links.call(LinkAction.DELETE, line.UID, line)

        self.host.removeID(line.UID)
        self.lines.pop(line.UID.value)

    def getLineByID(self, ID: int) -> PlotLine | None:
        return self.lines.get(ID, None)

    def __iter__(self) -> Iterator[PlotLine]:
        return self.lines.values().__iter__()

    @classmethod
    def loadPlotStep(cls, line: PlotLine, element: etree.Element) -> None:
        ID = element.get("ID")

        if ID is None:
            return

        line.loadStep(int(ID), element.get("name"), element.get("meta"), element.get("summary"))

    @classmethod
    def loadPlotLine(cls, plots: Plots, element: etree.Element) -> None:
        ID = element.get("ID")

        if ID is None:
            return

        importance = Importance.fromRawString(element.get("importance", None))
        if importance is None:
            importance = Importance.MINOR

        line = plots.loadLine(int(ID), element.get("name"), importance)
        line.description = element.get("description")
        line.result = element.get("result")

        for characterID in element.get("characters", "").split(","):
            try:
                character = plots.characters.getByID(int(characterID))
                if character is None:
                    continue

                line.addCharacter(character)
            except ValueError:
                continue

        for child in element.findall("step"):
            cls.loadPlotStep(line, child)

    @classmethod
    def loadPlots(cls, plots: Plots, root: etree.Element) -> None:
        for element in root.findall("plot"):
            cls.loadPlotLine(plots, element)

    def load(self) -> None:
        self.host.reset()
        self.lines.clear()

        AbstractData.load(self)

        try:
            tree = self.file.load()
            Plots.loadPlots(self, tree.getroot())

            self.complete()
        except FileNotFoundError:
            self.complete(False)

    @classmethod
    def saveElementAttribute(cls, element: etree.Element, name: str, value: Any) -> None:
        if value is None:
            return

        str_value = str(value)

        if len(str_value) > 0:
            element.set(name, str_value)

    @classmethod
    def savePlotStep(cls, step: PlotStep, parent: etree.Element) -> None:
        element = etree.SubElement(parent, "step")

        cls.saveElementAttribute(element, "name", step.name)
        cls.saveElementAttribute(element, "ID", step.UID.value)
        cls.saveElementAttribute(element, "meta", step.meta)
        cls.saveElementAttribute(element, "summary", step.summary)

    @classmethod
    def savePlotLine(cls, line: PlotLine, root: etree.Element) -> None:
        element = etree.SubElement(root, "plot")

        characters = ",".join([str(characterID) for characterID in line.characters])

        cls.saveElementAttribute(element, "name", line.name)
        cls.saveElementAttribute(element, "ID", line.UID.value)
        cls.saveElementAttribute(element, "importance", Importance.toRawString(line.importance))
        cls.saveElementAttribute(element, "characters", characters)
        cls.saveElementAttribute(element, "description", line.description)
        cls.saveElementAttribute(element, "result", line.result)

        for step in line:
            cls.savePlotStep(step, element)

    @classmethod
    def savePlots(cls, plots: Plots) -> None:
        root = etree.Element("root")

        for line in plots.lines.values():
            cls.savePlotLine(line, root)

        return root

    def save(self) -> None:
        AbstractData.save(self)

        tree = etree.ElementTree(Plots.savePlots(self))
        self.file.save(tree)
        self.complete()
