#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.models import references as Ref
from manuskript.enums import Outline
from manuskript.ui.highlighters.searchResultHighlighters.abstractSpecificSearchResultHighlighter import abstractSearchResultHighlighter
from manuskript.functions import mainWindow
from PyQt5.QtWidgets import QTextEdit, QLineEdit, QLabel
from manuskript.ui.views.metadataView import metadataView
from manuskript.ui.collapsibleGroupBox2 import collapsibleGroupBox2


class outlineSearchResultHighlighter(abstractSearchResultHighlighter):
    def __init__(self):
        super().__init__()
        self.outline_index = None

    def openView(self, searchResult):
        r = Ref.textReference(searchResult.id())
        Ref.open(r)

    def retrieveWidget(self, searchResult):
        editors = {
            Outline.text: ("txtRedacText", QTextEdit, None),
            Outline.title: ("txtTitle", QLineEdit, "grpProperties"),
            Outline.summarySentence: ("txtSummarySentence", QLineEdit, "grpSummary"),
            Outline.summaryFull: ("txtSummaryFull", QTextEdit, "grpSummary"),
            Outline.notes: ("txtNotes", QTextEdit, "grpNotes"),

            # TODO: Tried to highlight the combo box themselves (ie. cmbPOV) but didn't succeed.
            Outline.POV: ("lblPOV", QLabel, "grpProperties"),
            Outline.status: ("lblStatus", QLabel, "grpProperties"),
            Outline.label: ("lblLabel", QLabel, "grpProperties")
        }

        editorName, editorClass, parentName = editors[searchResult.column()]

        # Metadata columns are inside a splitter widget that my be hidden, so we show them.
        if parentName:
            metadataViewWidget = mainWindow().findChild(metadataView, "redacMetadata")
            mainWindow().toolbar.switchActionByWidget(metadataViewWidget)
            widget = metadataViewWidget.findChild(editorClass, editorName)
        else:
            widget = mainWindow().mainEditor.currentEditor().findChild(editorClass, editorName)

        return widget
