#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os

from lxml import etree
from manuskript.data.characters import Characters, Character
from manuskript.data.importance import Importance
from manuskript.data.links import LinkAction, Links
from manuskript.data.unique_id import UniqueIDHost, UniqueID
from manuskript.io.xmlFile import XmlFile


class PlotStep:

    def __init__(self, plot, UID: UniqueID, name: str, meta: str = "", summary: str = ""):
        self.plot = plot

        self.UID = UID
        self.name = name
        self.meta = meta
        self.summary = summary

    def save(self):
        self.plot.save()


class PlotLine:

    def __init__(self, plots, UID: UniqueID, name: str = None, importance: Importance = Importance.MINOR):
        self.plots = plots
        self.host = UniqueIDHost()
        self.links = Links()

        if name is None:
            name = "New plot"

        self.UID = UID
        self.name = name
        self.importance = importance
        self.characters = list()
        self.description = ""
        self.result = ""
        self.steps = list()

    def __linkActionCharacter(self, action: LinkAction, UID: UniqueID, character):
        if action == LinkAction.DELETE:
            self.removeCharacter(character, False)

        self.links.call(LinkAction.UPDATE, self.UID, self)

    def addCharacter(self, character: Character):
        if character is None:
            return

        character.links.add(self.__linkActionCharacter)

        self.characters.append(character.UID.value)
        self.links.call(LinkAction.UPDATE, self.UID, self)

    def removeCharacter(self, character: Character, unlink: bool = True):
        if character is None:
            return

        if unlink:
            character.links.remove(self.__linkActionCharacter)

        self.characters.remove(character.UID.value)
        self.links.call(LinkAction.UPDATE, self.UID, self)

    def addStep(self, name: str, meta: str = "", summary: str = ""):
        step = PlotStep(self, self.host.newID(), name, meta, summary)
        self.steps.append(step)

        self.links.call(LinkAction.UPDATE, self.UID, self)
        return step

    def loadStep(self, ID: int, name: str, meta: str = "", summary: str = ""):
        step = PlotStep(self, self.host.loadID(ID), name, meta, summary)
        self.steps.append(step)

        self.links.call(LinkAction.UPDATE, self.UID, self)
        return step

    def removeStep(self, step: PlotStep):
        self.host.removeID(step.UID)
        self.steps.remove(step)

        self.links.call(LinkAction.UPDATE, self.UID, self)

    def __iter__(self):
        return self.steps.__iter__()

    def save(self):
        self.plots.save()


class Plots:

    def __init__(self, path, characters: Characters):
        self.file = XmlFile(os.path.join(path, "plots.xml"))
        self.host = UniqueIDHost()
        self.characters = characters
        self.lines = dict()

    def addLine(self, name: str = None, importance: Importance = Importance.MINOR):
        line = PlotLine(self, self.host.newID(), name, importance)
        self.lines[line.UID.value] = line
        return line

    def loadLine(self, ID: int, name: str = None, importance: Importance = Importance.MINOR):
        line = PlotLine(self, self.host.loadID(ID), name, importance)
        self.lines[line.UID.value] = line

        line.links.call(LinkAction.RELOAD, line.UID, line)
        return line

    def removeLine(self, line: PlotLine):
        line.links.call(LinkAction.DELETE, line.UID, line)

        self.host.removeID(line.UID)
        self.lines.pop(line.UID.value)

    def getLineByID(self, ID: int) -> PlotLine:
        return self.lines.get(ID, None)

    def __iter__(self):
        return self.lines.values().__iter__()

    @classmethod
    def loadPlotStep(cls, line: PlotLine, element: etree.Element):
        ID = element.get("ID")

        if ID is None:
            return

        line.loadStep(
            int(ID),
            element.get("name"),
            element.get("meta"),
            element.get("summary")
        )

    @classmethod
    def loadPlotLine(cls, plots, element: etree.Element):
        ID = element.get("ID")

        if ID is None:
            return

        importance = Importance.fromRawString(element.get("importance", None))
        line = plots.loadLine(int(ID), element.get("name"), importance)
        line.description = element.get("description")
        line.result = element.get("result")

        for characterID in element.get("characters", "").split(','):
            try:
                line.addCharacter(plots.characters.getByID(int(characterID)))
            except ValueError:
                continue

        for child in element.findall("step"):
            cls.loadPlotStep(line, child)

    @classmethod
    def loadPlots(cls, plots, root: etree.Element):
        plots.host.reset()
        plots.lines.clear()

        for element in root.findall("plot"):
            cls.loadPlotLine(plots, element)

    def load(self):
        try:
            tree = self.file.load()
            Plots.loadPlots(self, tree.getroot())
        except FileNotFoundError:
            self.host.reset()
            self.lines.clear()

    @classmethod
    def saveElementAttribute(cls, element: etree.Element, name: str, value):
        if value is None:
            return

        str_value = str(value)

        if len(str_value) > 0:
            element.set(name, str_value)

    @classmethod
    def savePlotStep(cls, step: PlotStep, parent: etree.Element):
        element = etree.SubElement(parent, "step")

        cls.saveElementAttribute(element, "name", step.name)
        cls.saveElementAttribute(element, "ID", step.UID.value)
        cls.saveElementAttribute(element, "meta", step.meta)
        cls.saveElementAttribute(element, "summary", step.summary)

    @classmethod
    def savePlotLine(cls, line: PlotLine, root: etree.Element):
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
    def savePlots(cls, plots):
        root = etree.Element("root")

        for line in plots.lines.values():
            cls.savePlotLine(line, root)

        return root

    def save(self):
        tree = etree.ElementTree(Plots.savePlots(self))
        self.file.save(tree)
