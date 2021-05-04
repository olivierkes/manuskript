#!/usr/bin/env python
# --!-- coding: utf8 --!--

from lxml import etree
from manuskript.io.xmlFile import XmlFile


class PlotStep:

    def __init__(self, name, ID, meta="", summary=""):
        self.name = name
        self.ID = ID
        self.meta = meta
        self.summary = summary


class PlotItem:

    def __init__(self, name, ID, importance, description, result):
        self.name = name
        self.ID = ID
        self.importance = importance
        self.characters = []
        self.description = description
        self.result = result
        self.steps = []


class PlotsFile(XmlFile):

    @classmethod
    def loadPlot(cls, element):
        plotID = element.get("ID")

        if plotID is None:
            return None

        plot = PlotItem(
            element.get("name"),
            int(plotID),
            int(element.get("importance", 0)),
            element.get("description"),
            element.get("result")
        )

        for characterID in element.get("characters", "").split(','):
            try:
                plot.characters.append(int(characterID))
            except ValueError:
                continue

        for child in element.findall("step"):
            stepID = child.get("ID")

            if stepID is None:
                continue

            step = PlotStep(
                child.get("name"),
                int(stepID),
                child.get("meta"),
                child.get("summary")
            )

            plot.steps.append(step)

        return plot

    def load(self):
        tree = XmlFile.load(self)
        root = tree.getroot()

        plots = []

        for element in root.findall("plot"):
            plots.append(PlotsFile.loadPlot(element))

        return plots

    @classmethod
    def saveElementAttribute(cls, element, name, value):
        if value is None:
            return

        element.set(name, str(value))

    @classmethod
    def savePlot(cls, parent, plot):
        element = etree.SubElement(parent, "plot")

        cls.saveElementAttribute(element, "name", plot.name)
        cls.saveElementAttribute(element, "ID", plot.ID)
        cls.saveElementAttribute(element, "importance", plot.importance)
        cls.saveElementAttribute(element, "characters", ",".join([str(characterID) for characterID in plot.characters]))
        cls.saveElementAttribute(element, "description", plot.description)
        cls.saveElementAttribute(element, "result", plot.result)

        for step in plot.steps:
            child = etree.SubElement(element, "step")

            cls.saveElementAttribute(child, "name", step.name)
            cls.saveElementAttribute(child, "ID", step.ID)
            cls.saveElementAttribute(child, "meta", step.meta)
            cls.saveElementAttribute(child, "summary", step.summary)

    def save(self, plots):
        root = etree.Element("root")

        for plot in plots:
            PlotsFile.savePlot(root, plot)

        tree = etree.ElementTree(root)

        XmlFile.save(self, tree)
