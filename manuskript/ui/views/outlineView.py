#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtWidgets import QTreeView, QHeaderView

from manuskript import settings
from manuskript.enums import Outline
from manuskript.ui.views.dndView import dndView
from manuskript.ui.views.outlineBasics import outlineBasics
from manuskript.ui.views.outlineDelegates import outlineTitleDelegate, outlineCharacterDelegate, outlineCompileDelegate, \
    outlineStatusDelegate, outlineGoalPercentageDelegate, outlineLabelDelegate


class outlineView(QTreeView, dndView, outlineBasics):
    def __init__(self, parent=None, modelCharacters=None, modelLabels=None, modelStatus=None):
        QTreeView.__init__(self, parent)
        dndView.__init__(self)
        outlineBasics.__init__(self, parent)

        self.modelCharacters = modelCharacters
        self.modelLabels = modelLabels
        self.modelStatus = modelStatus

        self.header().setStretchLastSection(False)

    def setModelCharacters(self, model):
        # This is used by outlineCharacterDelegate to select character
        self.modelCharacters = model

    def setModelLabels(self, model):
        # This is used by outlineLabelDelegate to display labels
        self.modelLabels = model

    def setModelStatus(self, model):
        # This is used by outlineStatusDelegate to display statuses
        self.modelStatus = model

    def setModel(self, model):
        QTreeView.setModel(self, model)

        # Setting delegates
        self.outlineTitleDelegate = outlineTitleDelegate(self)
        # self.outlineTitleDelegate.setView(self)
        self.setItemDelegateForColumn(Outline.title, self.outlineTitleDelegate)
        self.outlineCharacterDelegate = outlineCharacterDelegate(self.modelCharacters)
        self.setItemDelegateForColumn(Outline.POV, self.outlineCharacterDelegate)
        self.outlineCompileDelegate = outlineCompileDelegate()
        self.setItemDelegateForColumn(Outline.compile, self.outlineCompileDelegate)
        self.outlineStatusDelegate = outlineStatusDelegate(self.modelStatus)
        self.setItemDelegateForColumn(Outline.status, self.outlineStatusDelegate)
        self.outlineGoalPercentageDelegate = outlineGoalPercentageDelegate()
        self.setItemDelegateForColumn(Outline.goalPercentage, self.outlineGoalPercentageDelegate)
        self.outlineLabelDelegate = outlineLabelDelegate(self.modelLabels)
        self.setItemDelegateForColumn(Outline.label, self.outlineLabelDelegate)

        # Hiding columns
        self.hideColumns()

        self.header().setSectionResizeMode(Outline.title, QHeaderView.Stretch)
        self.header().setSectionResizeMode(Outline.POV, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(Outline.status, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(Outline.label, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(Outline.compile, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(Outline.wordCount, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(Outline.goal, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(Outline.goalPercentage, QHeaderView.ResizeToContents)

    def hideColumns(self):
        if not self.model():
            # outlineView is probably not initialized, because editorWidgets shows index cards or text.
            return

        for c in range(self.model().columnCount()):
            self.hideColumn(c)
        for c in settings.outlineViewColumns:
            self.showColumn(c)

    def setRootIndex(self, index):
        QTreeView.setRootIndex(self, index)
        self.outlineGoalPercentageDelegate = outlineGoalPercentageDelegate(index)
        self.setItemDelegateForColumn(Outline.goalPercentage, self.outlineGoalPercentageDelegate)

    def dragMoveEvent(self, event):
        dndView.dragMoveEvent(self, event)
        QTreeView.dragMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        QTreeView.mouseReleaseEvent(self, event)
        outlineBasics.mouseReleaseEvent(self, event)
