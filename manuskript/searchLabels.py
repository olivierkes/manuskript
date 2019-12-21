#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.enums import Outline, Character, FlatData, World, Plot, PlotStep

OutlineSearchLabels = {
    Outline.title: "Title",
    Outline.text: "Text",
    Outline.summarySentence: "One sentence summary",
    Outline.summaryFull: "Summary",
    Outline.POV: "POV",
    Outline.notes: "Notes",
    Outline.status: "Status",
    Outline.label: "Label"
}

CharacterSearchLabels = {
    Character.name: "Name",
    Character.motivation: "Motivation",
    Character.goal: "Goal",
    Character.conflict: "Conflict",
    Character.epiphany: "Epiphany",
    Character.summarySentence: "One sentence summary",
    Character.summaryPara: "One paragraph summary",
    Character.summaryFull: "Summary",
    Character.notes: "Notes",
    Character.infos: "Detailed info"
}

FlatDataSearchLabels = {
    FlatData.summarySituation: "Situation",
    FlatData.summarySentence: "One sentence summary",
    FlatData.summaryPara: "One paragraph summary",
    FlatData.summaryPage: "One page summary",
    FlatData.summaryFull: "Full summary"
}

WorldSearchLabels = {
    World.name: "Name",
    World.description: "Description",
    World.passion: "Passion",
    World.conflict: "Conflict"
}

# Search menu includes one single option for both plot and plotStep models. For plotStep related fields
# (like PlotStep.meta) we add an offset so it is not confused with the Plot enum value mapping to the same integer.
PLOT_STEP_COLUMNS_OFFSET = 30

PlotSearchLabels = {
    Plot.name: "Name",
    Plot.description: "Description",
    Plot.characters: "Characters",
    Plot.result: "Result",
    Plot.summary: "Summary",
    PLOT_STEP_COLUMNS_OFFSET + PlotStep.meta: "Meta"
}
