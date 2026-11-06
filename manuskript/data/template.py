#!/usr/bin/env python
# --!-- coding: utf8 --!--

from enum import Enum, unique
from typing import Optional

from manuskript.data.goal import Goal
from manuskript.util import validVariantValue


@unique
class TemplateKind(Enum):
    FICTION = 0
    NONFICTION = 1
    DEMO = 2

    @classmethod
    def fromValue(cls, value: int) -> TemplateKind | None:
        return None if (value < 0) or (value > 2) else TemplateKind(value)

    @classmethod
    def asValue(cls, kind: TemplateKind | None) -> int:
        return validVariantValue(kind)


class TemplateLevel:
    def __init__(self, size: int = 10, name: str | None = None) -> None:
        self.size = max(size, 1)
        self.name = name


class Template:
    def __init__(
        self,
        name: str,
        kind: TemplateKind,
        goal: Optional[Goal] = None,
        levels: list[TemplateLevel] = [],
        levelNames: list[str] = [],
    ) -> None:
        self.name = name
        self.kind = kind
        self.goal = goal
        self.levels = levels

        if not ("Text" in levelNames):
            levelNames.append("Text")

        self.levelNames = levelNames

    def addLevel(self) -> None:
        index = min(len(self.levels), len(self.levelNames) - 1)

        if index < 0:
            return

        self.levels.append(TemplateLevel(name=self.levelNames[index]))

    def addGoal(self, value: int = 500) -> None:
        if self.goal is not None:
            return

        self.goal = Goal(value)

    def getGoalString(self) -> str:
        if self.goal is None:
            return "?"

        value = validVariantValue(self.goal)
        for level in self.levels:
            value = value * level.size

        return Goal(value, self.goal.kind).prettyString()

    @classmethod
    def getDefaultTemplates(cls) -> list[Template]:
        templates: list[Template] = list()

        templates.append(Template("Empty fiction", TemplateKind.FICTION))

        templates.append(
            Template(
                "Novel",
                TemplateKind.FICTION,
                Goal(500),
                [TemplateLevel(20, "Chapter"), TemplateLevel(5, "Scene")],
            )
        )

        templates.append(
            Template(
                "Novella",
                TemplateKind.FICTION,
                Goal(500),
                [TemplateLevel(10, "Chapter"), TemplateLevel(5, "Scene")],
            )
        )

        templates.append(
            Template("Short Story", TemplateKind.FICTION, Goal(1000), [TemplateLevel(10, "Scene")])
        )

        templates.append(
            Template(
                "Trilogy",
                TemplateKind.FICTION,
                Goal(500),
                [
                    TemplateLevel(3, "Book"),
                    TemplateLevel(3, "Section"),
                    TemplateLevel(10, "Chapter"),
                    TemplateLevel(5, "Scene"),
                ],
            )
        )

        templates.append(Template("Empty non-fiction", TemplateKind.NONFICTION))

        templates.append(
            Template(
                "Research paper", TemplateKind.NONFICTION, Goal(1000), [TemplateLevel(3, "Section")]
            )
        )

        return templates
