#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QSignalMapper
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QStandardItem
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QAction, QMenu

from manuskript.enums import Plot
from manuskript.enums import PlotStep
from manuskript.functions import toInt, mainWindow


class plotModel(QStandardItemModel):
    def __init__(self, parent):
        QStandardItemModel.__init__(self, 0, 3, parent)
        self.setHorizontalHeaderLabels([i.name for i in Plot])
        self.mw = mainWindow()

        self.updatePlotPersoButton()

    ###############################################################################
    # QUERIES
    ###############################################################################

    def getPlotsByImportance(self):
        plots = [[], [], []]
        for i in range(self.rowCount()):
            importance = self.item(i, Plot.importance).text()
            ID = self.item(i, Plot.ID).text()
            plots[2 - toInt(importance)].append(ID)
        return plots

    def getSubPlotsByID(self, ID):
        index = self.getIndexFromID(ID)
        if not index.isValid():
            return
        index = index.sibling(index.row(), Plot.steps)
        item = self.itemFromIndex(index)
        lst = []
        for i in range(item.rowCount()):
            if item.child(i, PlotStep.ID):
                _ID = item.child(i, PlotStep.ID).text()

                # Don't know why sometimes name is None (while drag'n'dropping
                # several items)
                if item.child(i, PlotStep.name):
                    name = item.child(i, PlotStep.name).text()
                else:
                    name = ""

                # Don't know why sometimes summary is None
                if item.child(i, PlotStep.summary):
                    summary = item.child(i, PlotStep.summary).text()
                else:
                    summary = ""

                lst.append((_ID, name, summary))
        return lst

    def getPlotNameByID(self, ID):
        for i in range(self.rowCount()):
            _ID = self.item(i, Plot.ID).text()
            if _ID == ID or toInt(_ID) == ID:
                name = self.item(i, Plot.name).text()
                return name
        return None

    def getPlotImportanceByRow(self, row):
        for i in range(self.rowCount()):
            if i == row:
                importance = self.item(i, Plot.importance).text()
                return importance
        return "0" # Default to "Minor"

    def getSubPlotTextsByID(self, plotID, subplotRaw):
        """Returns a tuple (name, summary) for the subplot whose raw in the model
        is ``subplotRaw``, of plot whose ID is ``plotID``.
        """
        plotIndex = self.getIndexFromID(plotID)
        name = plotIndex.child(subplotRaw, PlotStep.name).data()
        summary = plotIndex.child(subplotRaw, PlotStep.summary).data()
        return name, summary

    def getIndexFromID(self, ID):
        for i in range(self.rowCount()):
            _ID = self.item(i, Plot.ID).text()
            if _ID == ID or toInt(_ID) == ID:
                return self.index(i, 0)
        return QModelIndex()

    def currentIndex(self):
        i = self.mw.lstPlots.currentIndex()
        if i.isValid():
            return i
        else:
            return None

    ###############################################################################
    # ADDING / REMOVING
    ###############################################################################

    def addPlot(self):
        p = QStandardItem(self.tr("New plot"))
        _id = QStandardItem(self.getUniqueID())
        importance = QStandardItem(str(0))
        self.appendRow([p, _id, importance, QStandardItem("Characters"),
                        QStandardItem(), QStandardItem(), QStandardItem("Resolution steps")])

    def getUniqueID(self, parent=QModelIndex()):
        """Returns an unused ID"""
        parentItem = self.itemFromIndex(parent)
        vals = []
        for i in range(self.rowCount(parent)):
            index = self.index(i, Plot.ID, parent)
            # item = self.item(i, Plot.ID)
            if index.isValid() and index.data():
                vals.append(int(index.data()))

        k = 0
        while k in vals:
            k += 1
        return str(k)

    def removePlot(self, index):
        self.takeRow(index.row())

    ###############################################################################
    # SUBPLOTS
    ###############################################################################

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == PlotStep.name:
                    return self.tr("Name")
                elif section == PlotStep.meta:
                    return self.tr("Meta")
                else:
                    return ""
            else:
                return ""
        else:
            return QStandardItemModel.headerData(self, section, orientation, role)

    def data(self, index, role=Qt.DisplayRole):
        if index.parent().isValid() and \
                        index.parent().column() == Plot.steps and \
                        index.column() == PlotStep.meta:
            if role == Qt.TextAlignmentRole:
                return Qt.AlignRight | Qt.AlignVCenter
            elif role == Qt.ForegroundRole:
                return QBrush(Qt.gray)
            else:
                return QStandardItemModel.data(self, index, role)

        else:
            return QStandardItemModel.data(self, index, role)

    def addSubPlot(self):
        index = self.mw.lstPlots.currentPlotIndex()
        if not index.isValid():
            return

        parent = index.sibling(index.row(), Plot.steps)
        parentItem = self.item(index.row(), Plot.steps)

        if not parentItem:
            return

        p = QStandardItem(self.tr("New step"))
        _id = QStandardItem(self.getUniqueID(parent))
        summary = QStandardItem()

        currentIndex = self.mw.lstSubPlots.selectionModel().selectedIndexes()
        if currentIndex:
            # We use last item of selection in case of many
            currentIndex = currentIndex[-1]
            row = currentIndex.row() + 1
            parentItem.insertRow(row, [p, _id, QStandardItem(), summary])
            # Select last index
            self.mw.lstSubPlots.setCurrentIndex(currentIndex.sibling(row, 0))
        else:
            # Don't know why, if summary is in third position, then drag/drop deletes it...
            parentItem.appendRow([p, _id, QStandardItem(), summary])
            # Select last index
            self.mw.lstSubPlots.setCurrentIndex(parent.child(self.rowCount(parent) - 1, 0))

    def removeSubPlot(self):
        """
        Remove all selected subplots / plot steps, in mw.lstSubPlots.
        """
        parent = self.mw.lstSubPlots.rootIndex()
        if not parent.isValid():
            return
        parentItem = self.itemFromIndex(parent)

        while self.mw.lstSubPlots.selectionModel().selectedRows():
            i = self.mw.lstSubPlots.selectionModel().selectedRows()[0]
            parentItem.takeRow(i.row())

    def flags(self, index):
        parent = index.parent()
        if parent.isValid():  # this is a subitem
            return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
        else:
            return QStandardItemModel.flags(self, index)

    ###############################################################################
    # PLOT PERSOS
    ###############################################################################

    def addPlotPerso(self, v):
        index = self.mw.lstPlots.currentPlotIndex()
        if index.isValid():
            if not self.item(index.row(), Plot.characters):
                self.setItem(index.row(), Plot.characters, QStandardItem())

            item = self.item(index.row(), Plot.characters)

            # We check that the PersoID is not in the list yet
            for i in range(item.rowCount()):
                if item.child(i).text() == str(v):
                    return

            item.appendRow(QStandardItem(str(v)))

    def removePlotPerso(self):
        index = self.mw.lstPlotPerso.currentIndex()
        if not index.isValid():
            return
        parent = index.parent()
        parentItem = self.itemFromIndex(parent)
        parentItem.takeRow(index.row())

    def updatePlotPersoButton(self):
        menu = QMenu(self.mw)

        menus = []
        for i in [self.tr("Main"), self.tr("Secondary"), self.tr("Minor")]:
            m = QMenu(i, menu)
            menus.append(m)
            menu.addMenu(m)

        mpr = QSignalMapper(menu)
        for i in range(self.mw.mdlCharacter.rowCount()):
            a = QAction(self.mw.mdlCharacter.name(i), menu)
            a.setIcon(self.mw.mdlCharacter.icon(i))
            a.triggered.connect(mpr.map)
            mpr.setMapping(a, int(self.mw.mdlCharacter.ID(i)))

            imp = toInt(self.mw.mdlCharacter.importance(i))

            menus[2 - imp].addAction(a)

        # Disabling empty menus
        for m in menus:
            if not m.actions():
                m.setEnabled(False)

        mpr.mapped.connect(self.addPlotPerso)
        self.mw.btnAddPlotPerso.setMenu(menu)
