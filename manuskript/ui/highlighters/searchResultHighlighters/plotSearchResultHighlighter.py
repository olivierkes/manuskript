#!/usr/bin/env python
# --!-- coding: utf8 --!--


from manuskript.models import references as Ref
from manuskript.functions import mainWindow
from manuskript.enums import Plot
from PyQt5.QtWidgets import QTextEdit, QLineEdit, QListView
from manuskript.ui.highlighters.searchResultHighlighters.abstractSpecificSearchResultHighlighter import abstractSearchResultHighlighter


class plotSearchResultHighlighter(abstractSearchResultHighlighter):
    def __init__(self):
        super().__init__()

    def openView(self, searchResult):
        r = Ref.plotReference(searchResult.id())
        Ref.open(r)
        mainWindow().tabPlot.setEnabled(True)

    def retrieveWidget(self, searchResult):
        textEditMap = {
            Plot.name: (0, "txtPlotName", QLineEdit),
            Plot.description: (0, "txtPlotDescription", QTextEdit),
            Plot.characters: (0, "lstPlotPerso", QListView),
            Plot.result: (0, "txtPlotResult", QTextEdit)
        }

        tabIndex, widgetName, widgetClass = textEditMap[searchResult.column()]

        mainWindow().tabPlot.setCurrentIndex(tabIndex)
        return mainWindow().tabPlot.findChild(widgetClass, widgetName)
