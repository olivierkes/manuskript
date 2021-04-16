#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.functions import mainWindow
from manuskript.enums import  FlatData
from PyQt5.QtWidgets import QTextEdit, QLineEdit
from manuskript.ui.highlighters.searchResultHighlighters.abstractSpecificSearchResultHighlighter import abstractSearchResultHighlighter


class flatDataSearchResultHighlighter(abstractSearchResultHighlighter):
    def __init__(self):
        super().__init__()

    def openView(self, searchResult):
        mainWindow().tabMain.setCurrentIndex(mainWindow().TabSummary)

    def retrieveWidget(self, searchResult):
        editors = {
            FlatData.summarySituation: (0, "txtSummarySituation", QLineEdit, mainWindow()),
            FlatData.summarySentence: (0, "txtSummarySentence", QTextEdit, mainWindow().tabSummary),
            FlatData.summaryPara: (1, "txtSummaryPara", QTextEdit, mainWindow().tabSummary),
            FlatData.summaryPage: (2, "txtSummaryPage", QTextEdit, mainWindow().tabSummary),
            FlatData.summaryFull: (3, "txtSummaryFull", QTextEdit, mainWindow().tabSummary)
        }

        stackIndex, editorName, editorClass, rootWidget = editors[searchResult.column()]

        mainWindow().tabSummary.setCurrentIndex(stackIndex)
        return rootWidget.findChild(editorClass, editorName)
