#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt, QModelIndex, QMimeData
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from lxml import etree as ET

from manuskript import settings
from manuskript.enums import Plot, Outline, PlotStep
from manuskript.models import references as Ref
from manuskript.ui import style as S


class plotTreeView(QTreeWidget):
    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)
        self._model = None
        self._catRow = [-1, -1, -1]
        self._filter = ""
        self._lastID = -1
        self._updating = False
        self._showSubPlot = False
        self.setRootIsDecorated(False)
        self.setIndentation(10)

        self.setColumnCount(1)
        self._rootItem = QTreeWidgetItem()
        self.insertTopLevelItem(0, self._rootItem)
        # self.currentItemChanged.connect(self._currentItemChanged)

    ###############################################################################
    # SETTERS
    ###############################################################################

    def setShowSubPlot(self, v):
        self._showSubPlot = v
        self.updateItems()

    def setPlotModel(self, model):
        self._model = model
        self._model.dataChanged.connect(self.updateMaybe)
        self._model.rowsInserted.connect(self.updateMaybe2)
        self._model.rowsRemoved.connect(self.updateMaybe2)
        self.updateItems()

    def setFilter(self, text):
        self._filter = text
        self.updateItems()

    ###############################################################################
    # GETTERS
    ###############################################################################

    def getItemByID(self, ID):
        "Recursively search items to find one whose data is ``ID``."

        def find(item, ID):
            if item.data(0, Qt.UserRole) == ID:
                return item
            for i in range(item.childCount()):
                r = find(item.child(i), ID)
                if r:
                    return r

        return find(self.invisibleRootItem(), ID)

    def currentPlotIndex(self):
        "Returns index of the current item in plot model."
        ID = None
        if self.currentItem():
            ID = self.currentItem().data(0, Qt.UserRole)

        return self._model.getIndexFromID(ID)

    ###############################################################################
    # UPDATES
    ###############################################################################

    def updateMaybe(self, topLeft, bottomRight):
        if topLeft.parent() != QModelIndex() and \
           topLeft.column() <= PlotStep.name.value <= bottomRight.column() and \
           self._showSubPlot:
            # Name's of Step has been updated, we update Items if showing
            # subplots.
            self.updateItems()
        elif topLeft.parent() != QModelIndex():
            return

        if topLeft.column() <= Plot.name.value <= bottomRight.column():
            # Update name
            self.updateNames()

        elif topLeft.column() <= Plot.importance.value <= bottomRight.column():
            # Importance changed
            self.updateItems()

    def updateMaybe2(self, parent, first, last):
        "Rows inserted or removed"
        if parent == QModelIndex():
            self.updateItems()

        elif self._showSubPlot:
            self.updateItems()

    def updateNames(self):
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)

            for c in range(item.childCount()):
                sub = item.child(c)
                ID = sub.data(0, Qt.UserRole)
                if ID:
                    name = self._model.getPlotNameByID(ID)
                    sub.setText(0, name)

    def updateItems(self):
        if not self._model:
            return

        if self.currentItem():
            self._lastID = self.currentItem().data(0, Qt.UserRole)

        self._updating = True
        self.clear()
        plots = self._model.getPlotsByImportance()

        h = [self.tr("Main"), self.tr("Secondary"), self.tr("Minor")]
        for i in range(3):
            cat = QTreeWidgetItem(self, [h[i]])
            cat.setBackground(0, QBrush(QColor(S.highlightLight)))
            cat.setForeground(0, QBrush(QColor(S.highlightedTextDark)))
            cat.setTextAlignment(0, Qt.AlignCenter)
            f = cat.font(0)
            f.setBold(True)
            cat.setFont(0, f)
            cat.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.addTopLevelItem(cat)
            # cat.setChildIndicatorPolicy(cat.DontShowIndicator)

            for ID in plots[i]:
                name = self._model.getPlotNameByID(ID)
                if not self._filter.lower() in name.lower():
                    continue
                item = QTreeWidgetItem(cat, [name])
                item.setData(0, Qt.UserRole, ID)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

                if self._showSubPlot:

                    f = item.font(0)
                    f.setBold(True)
                    item.setFont(0, f)

                    for subID, name, summary in self._model.getSubPlotsByID(ID):
                        sub = QTreeWidgetItem(item, [name])
                        # sub.setData(0, Qt.UserRole, "{}:{}".format(ID, subID))
                        sub.setData(0, Qt.UserRole, ID)

                if ID == self._lastID:
                    self.setCurrentItem(item)

        self.expandAll()
        self._updating = False

    ###############################################################################
    # DRAG N DROP
    ###############################################################################

    def mimeTypes(self):
        return ["application/xml"]

    def mimeData(self, items):
        mimeData = QMimeData()
        encodedData = ""

        root = ET.Element("outlineItems")

        for item in items:
            plotID = item.data(0, Qt.UserRole)
            subplotRaw = item.parent().indexOfChild(item)

            _id, name, summary = self._model.getSubPlotsByID(plotID)[subplotRaw]
            sub = ET.Element("outlineItem")
            sub.set(Outline.title.name, name)
            sub.set(Outline.type.name, settings.defaultTextType)
            sub.set(Outline.summaryFull.name, summary)
            sub.set(Outline.notes.name, self.tr("**Plot:** {}").format(
                    Ref.plotReference(plotID)))

            root.append(sub)

        encodedData = ET.tostring(root)

        mimeData.setData("application/xml", encodedData)
        return mimeData

    ###############################################################################
    # EVENTS
    ###############################################################################

    def mouseDoubleClickEvent(self, event):
        item = self.currentItem()
        # Catching double clicks to forbid collapsing of toplevel items
        if item.parent():
            QTreeWidget.mouseDoubleClickEvent(self, event)
