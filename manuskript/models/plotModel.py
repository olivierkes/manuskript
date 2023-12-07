#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QSignalMapper
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QStandardItem
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QAction, QMenu

from manuskript.enums import Plot, PlotStep, Model
from manuskript.functions import toInt, mainWindow
from manuskript.models.searchResultModel import searchResultModel
from manuskript.searchLabels import PlotSearchLabels, PLOT_STEP_COLUMNS_OFFSET
from manuskript.functions import search
from manuskript.models.searchableModel import searchableModel
from manuskript.models.searchableItem import searchableItem

class plotModel(QStandardItemModel, searchableModel):
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
        return "0"  # Default to "Minor"

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

    def addPlot(self, name=None):
        if not name:
            name = self.tr("New plot")

        p = QStandardItem(self.tr(name))
        _id = QStandardItem(self.getUniqueID())
        importance = QStandardItem(str(0))
        self.appendRow([p, _id, importance, QStandardItem("Characters"),
                        QStandardItem(), QStandardItem(), QStandardItem("Resolution steps")])
        return p, _id

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
            self.mw.lstSubPlots.setCurrentIndex(
                parent.child(self.rowCount(parent) - 1, 0))

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

    #######################################################################
    # Search
    #######################################################################
    def searchableItems(self):
        items = []

        for i in range(self.rowCount()):
            items.append(plotItemSearchWrapper(i, self.item, self.mw.mdlCharacter.getCharacterByID))

        return items


class plotItemSearchWrapper(searchableItem):
    def __init__(self, rowIndex, getItem, getCharacterByID):
        self.rowIndex = rowIndex
        self.getItem = getItem
        self.getCharacterByID = getCharacterByID
        super().__init__(PlotSearchLabels)

    def searchOccurrences(self, searchRegex, column):
        results = []

        plotName = self.getItem(self.rowIndex, Plot.name).text()
        if column >= PLOT_STEP_COLUMNS_OFFSET:
            results += self.searchInPlotSteps(self.rowIndex, plotName, column, column - PLOT_STEP_COLUMNS_OFFSET, searchRegex, False)
        else:
            item_name = self.getItem(self.rowIndex, Plot.name).text()
            if column == Plot.characters:
                charactersList = self.getItem(self.rowIndex, Plot.characters)

                for i in range(charactersList.rowCount()):
                    characterID = charactersList.child(i).text()

                    character = self.getCharacterByID(characterID)
                    if character:
                        columnText = character.name()

                        characterResults = search(searchRegex, columnText)
                        if len(characterResults):
                            # We will highlight the full character row in the plot characters list, so we
                            # return the row index instead of the match start and end positions.
                            results += [
                                searchResultModel(Model.Plot, self.getItem(self.rowIndex, Plot.ID).text(), column,
                                             self.translate(item_name),
                                             self.searchPath(column),
                                             [(i, 0)], context) for start, end, context in
                                search(searchRegex, columnText)]
            else:
                results += super().searchOccurrences(searchRegex, column)
                if column == Plot.name:
                    results += self.searchInPlotSteps(self.rowIndex, plotName, Plot.name, PlotStep.name,
                                                      searchRegex, False)
                elif column == Plot.summary:
                    results += self.searchInPlotSteps(self.rowIndex, plotName, Plot.summary, PlotStep.summary,
                                                      searchRegex, True)

        return results

    def searchModel(self):
        return Model.Plot

    def searchID(self):
        return self.getItem(self.rowIndex, Plot.ID).text()

    def searchTitle(self, column):
        return self.getItem(self.rowIndex, Plot.name).text()

    def searchPath(self, column):
        def _path(item):
            path = []

            if item.parent():
                path += _path(item.parent())
            path.append(item.text())

            return path

        return [self.translate("Plot")] + _path(self.getItem(self.rowIndex, Plot.name)) + [self.translate(self.searchColumnLabel(column))]

    def searchData(self, column):
        item = self.getItem(self.rowIndex, column)
        return item.text() if item else None

    def plotStepPath(self, plotName, plotStepName, column):
        return [self.translate("Plot"), plotName, plotStepName, self.translate(self.searchColumnLabel(column))]

    def searchInPlotSteps(self, plotIndex, plotName, plotColumn, plotStepColumn, searchRegex, searchInsidePlotStep):
        results = []

        # Plot step info can be found in two places: the own list of plot steps (this is the case for ie. name and meta
        # fields) and "inside" the plot step once it is selected in the list (as it's the case for the summary).
        if searchInsidePlotStep:
            # We are searching *inside* the plot step, so we return both the row index (for selecting the right plot
            # step in the list), and (start, end) positions of the match inside the text field for highlighting it.
            getSearchData = lambda rowIndex, start, end, context: ([(rowIndex, 0), (start, end)], context)
        else:
            # We are searching *in the plot step row*, so we only return the row index for selecting the right plot
            # step in the list when highlighting search results.
            getSearchData = lambda rowIndex, start, end, context: ([(rowIndex, 0)], context)

        item = self.getItem(plotIndex, Plot.steps)
        for i in range(item.rowCount()):
            if item.child(i, PlotStep.ID):
                plotStepName = item.child(i, PlotStep.name).text()
                plotStepText = item.child(i, plotStepColumn).text()

                # We will highlight the full plot step row in the plot steps list, so we
                # return the row index instead of the match start and end positions.
                results += [searchResultModel(Model.PlotStep, self.getItem(plotIndex, Plot.ID).text(), plotStepColumn,
                                         self.translate(plotStepName),
                                         self.plotStepPath(plotName, plotStepName, plotColumn),
                                         *getSearchData(i, start, end, context)) for start, end, context in
                            search(searchRegex, plotStepText)]

        return results