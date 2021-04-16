#!/usr/bin/env python
# --!-- coding: utf8 --!--


from manuskript.models import references as Ref
from manuskript.functions import mainWindow
from manuskript.enums import  PlotStep
from PyQt5.QtWidgets import QTableView, QTextEdit
from manuskript.ui.highlighters.searchResultHighlighters.abstractSpecificSearchResultHighlighter import abstractSearchResultHighlighter


class plotStepSearchResultHighlighter(abstractSearchResultHighlighter):
    def __init__(self):
        super().__init__()

    def openView(self, searchResult):
        r = Ref.plotReference(searchResult.id())
        Ref.open(r)
        mainWindow().tabPlot.setEnabled(True)

    def retrieveWidget(self, searchResult):
        textEditMap = {
            PlotStep.name: [(1, "lstSubPlots", QTableView)],
            PlotStep.meta: [(1, "lstSubPlots", QTableView)],
            PlotStep.summary: [(1, "lstSubPlots", QTableView), (1, "txtSubPlotSummary", QTextEdit)]
        }

        map = textEditMap[searchResult.column()]
        widgets = []
        for tabIndex, widgetName, widgetClass in map:
            mainWindow().tabPlot.setCurrentIndex(tabIndex)

            widgets.append(mainWindow().tabPlot.findChild(widgetClass, widgetName))

        return widgets
