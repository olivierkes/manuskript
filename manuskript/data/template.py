#!/usr/bin/env python
# --!-- coding: utf8 --!--

from enum import Enum, unique
from manuskript.data.goal import Goal


@unique
class TemplateKind(Enum):
    FICTION = 0
    NONFICTION = 1
    DEMO = 2

    @classmethod
    def fromValue(cls, value: int):
        return None if (value < 0) or (value > 2) else TemplateKind(value)

    @classmethod
    def asValue(cls, kind):
        return 0 if kind is None else kind.value


class TemplateLevel:

    def __init__(self, size: int = 1, name: str = None):
        self.size = max(size, 1)
        self.name = name


class Template:

    def __init__(self, name: str, kind: TemplateKind, goal: Goal = None, levels: list = None, levelNames: list = None):
        self.name = name
        self.kind = kind
        self.goal = goal

        if levels is None:
            levels = list()

        self.levels = levels

        if levelNames is None:
            levelNames = list()

        if not ("Text" in levelNames):
            levelNames.append("Text")

        self.levelNames = levelNames

    @classmethod
    def getDefaultTemplates(cls):
        templates = list()

        templates.append(Template("Empty fiction", TemplateKind.FICTION))

        templates.append(Template("Novel", TemplateKind.FICTION, Goal(500), [
            TemplateLevel(20, "Chapter"),
            TemplateLevel(5, "Scene")
        ]))

        templates.append(Template("Novella", TemplateKind.FICTION, Goal(500), [
            TemplateLevel(10, "Chapter"),
            TemplateLevel(5, "Scene")
        ]))

        templates.append(Template("Short Story", TemplateKind.FICTION, Goal(1000), [
            TemplateLevel(10, "Scene")
        ]))

        templates.append(Template("Trilogy", TemplateKind.FICTION, Goal(500), [
            TemplateLevel(3, "Book"),
            TemplateLevel(3, "Section"),
            TemplateLevel(10, "Chapter"),
            TemplateLevel(5, "Scene")
        ]))

        templates.append(Template("Empty non-fiction", TemplateKind.NONFICTION))

        templates.append(Template("Research paper", TemplateKind.NONFICTION, Goal(1000), [
            TemplateLevel(3, "Section")
        ]))

        return templates
