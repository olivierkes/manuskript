#!/usr/bin/env python
#--!-- coding: utf8 --!--


from enum import IntEnum

class Character(IntEnum):
    name = 0
    ID = 1
    importance = 2
    motivation = 3
    goal = 4
    conflict = 5
    epiphany = 6
    summarySentence = 7
    summaryPara = 8
    summaryFull = 9
    notes = 10

class Plot(IntEnum):
    name = 0
    ID = 1
    importance = 2
    characters = 3
    description = 4
    result = 5
    steps = 6
    summary = 7

class PlotStep(IntEnum):
    name = 0
    ID = 1
    meta = 2
    summary = 3

class World(IntEnum):
    name = 0
    ID = 1
    description = 2
    passion = 3
    conflict = 4

class Outline(IntEnum):
    title = 0
    ID = 1
    type = 2
    summarySentence = 3
    summaryFull = 4
    POV = 5
    notes = 6
    label = 7
    status = 8
    compile = 9
    text = 10
    wordCount = 11
    goal = 12
    goalPercentage = 13
    setGoal = 14 # The goal set by the user, if any. Can be different from goal which can be computed
                 # (sum of all sub-items' goals)
    textFormat = 15
    revisions = 16
    customIcon = 17

class Abstract(IntEnum):
    title = 0
    ID = 1
    type = 2
