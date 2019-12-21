#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.ui.highlighters.searchResultHighlighters.abstractSearchResultHighlighter import abstractSearchResultHighlighter
from manuskript.ui.highlighters.searchResultHighlighters.characterSearchResultHighlighter import characterSearchResultHighlighter
from manuskript.ui.highlighters.searchResultHighlighters.flatDataSearchResultHighlighter import flatDataSearchResultHighlighter
from manuskript.ui.highlighters.searchResultHighlighters.outlineSearchResultHighlighter import outlineSearchResultHighlighter
from manuskript.ui.highlighters.searchResultHighlighters.worldSearchResultHighlighter import worldSearchResultHighlighter
from manuskript.ui.highlighters.searchResultHighlighters.plotSearchResultHighlighter import plotSearchResultHighlighter
from manuskript.ui.highlighters.searchResultHighlighters.plotStepSearchResultHighlighter import plotStepSearchResultHighlighter
from manuskript.enums import Model


class searchResultHighlighter(abstractSearchResultHighlighter):
    def __init__(self):
        super().__init__()

    def highlightSearchResult(self, searchResult):
        if searchResult.type() == Model.Character:
            highlighter = characterSearchResultHighlighter()
        elif searchResult.type() == Model.FlatData:
            highlighter = flatDataSearchResultHighlighter()
        elif searchResult.type() == Model.Outline:
            highlighter = outlineSearchResultHighlighter()
        elif searchResult.type() == Model.World:
            highlighter = worldSearchResultHighlighter()
        elif searchResult.type() == Model.Plot:
            highlighter = plotSearchResultHighlighter()
        elif searchResult.type() == Model.PlotStep:
            highlighter = plotStepSearchResultHighlighter()
        else:
            raise NotImplementedError

        highlighter.highlightSearchResult(searchResult)
