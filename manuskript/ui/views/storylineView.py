#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QGraphicsSimpleTextItem, QMenu, QAction, QGraphicsRectItem, \
    QGraphicsLineItem

from manuskript.functions import randomColor
from manuskript.ui.views.storylineView_ui import Ui_storylineView


class storylineView(QWidget, Ui_storylineView):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self._mdlPlots = None
        self.btnRefresh.clicked.connect(self.refresh)
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)

        self.reloadTimer = QTimer()
        self.reloadTimer.timeout.connect(self.refresh)
        self.reloadTimer.setSingleShot(True)
        self.reloadTimer.setInterval(500)

        self.generateMenu()

    def generateMenu(self):
        m = QMenu()

        for i in [
            self.tr("Show Plots"),
            self.tr("Show Characters"),
            self.tr("Show Objects"),
        ]:
            a = QAction(i, m)
            a.setCheckable(True)
            a.setEnabled(False)
            m.addAction(a)

        self.btnSettings.setMenu(m)

    def setModels(self, mdlOutline, mdlPersos, mdlPlots):
        self._mdlPlots = mdlPlots
        # self._mdlPlots.dataChanged.connect(self.refresh)
        # self._mdlPlots.rowsInserted.connect(self.refresh)

        self._mdlOutline = mdlOutline
        self._mdlOutline.dataChanged.connect(self.reloadTimer.start)

        self._mdlPersos = mdlPersos
        self._mdlPersos.dataChanged.connect(self.reloadTimer.start)


    def refresh(self):
        if not self._mdlPlots or not self._mdlOutline or not self._mdlPersos:
            pass

        LINE_HEIGHT = 32
        SPACING = 6
        RECT_WIDTH = 200
        TEXT_WIDTH = 25
        LEVEL_HEIGHT = 12

        s = self.scene
        s.clear()

        # Get Max Level
        root = self._mdlOutline.rootItem
        def maxLevel(item, level=0, max=0):
            if level > max:
                max = level
            for c in item.children():
                m = maxLevel(c, level + 1)
                if m > max:
                    max = m
            return max

        MAX_LEVEL = maxLevel(root)

        # Get plots
        plotsID = self._mdlPlots.getPlotsByImportance()
        plots = []
        for importance in plotsID:
            for ID in importance:
                name = self._mdlPlots.getPlotNameByID(ID)
                plots.append((ID, name))

        ROWS_HEIGHT = len(plots) * (LINE_HEIGHT + SPACING )


        # Add Folders and Texts
        outline = OutlineRect(0, 0, 0, ROWS_HEIGHT + SPACING + MAX_LEVEL * LEVEL_HEIGHT)
        s.addItem(outline)
        outline.setPos(RECT_WIDTH + SPACING, 0)

        # A Function to add a rect with centered text
        def addRectText(x, w, parent, text="", level=0, tooltip=""):
            deltaH = LEVEL_HEIGHT if level else 0
            r = OutlineRect(0, 0, w, parent.rect().height()-deltaH, parent)
            r.setPos(x, deltaH)
            r.setToolTip(tooltip)

            txt = QGraphicsSimpleTextItem(text, r)
            f = txt.font()
            f.setPointSize(8)
            txt.setFont(f)
            txt.setPos(r.boundingRect().center() - txt.boundingRect().center())
            txt.setY(0)
            return r

        def itemWidth(item):
            if item.isFolder():
                r = 0
                for c in item.children():
                    r += itemWidth(c)
                return r
            else:
                return TEXT_WIDTH

        def listItems(item, rect, level=0):
            delta = 0
            for child in item.children():
                w = itemWidth(child)
                if child.isFolder():
                    parent = addRectText(delta, w, rect, child.title(), level, tooltip=child.title())
                    listItems(child, parent, level + 1)
                else:
                    addRectText(delta, TEXT_WIDTH, rect, "", level, tooltip=child.title())
                delta += w

        listItems(root, outline)

        OUTLINE_WIDTH = itemWidth(root)

        # Add Plots
        i = 0
        itemsRect = s.addRect(0, 0, 0, 0)
        itemsRect.setPos(0, MAX_LEVEL * LEVEL_HEIGHT + SPACING)

        for ID, name in plots:
            color = randomColor()

            # Rect
            r = QGraphicsRectItem(0, 0, RECT_WIDTH, LINE_HEIGHT, itemsRect)
            r.setPen(QPen(Qt.NoPen))
            r.setBrush(QBrush(color))
            r.setPos(0, i * LINE_HEIGHT + i * SPACING)
            i += 1

            # Text
            txt = QGraphicsSimpleTextItem(name, r)
            txt.setPos(r.boundingRect().center() - txt.boundingRect().center())

            # Line
            line = PlotLine(RECT_WIDTH,
                            r.mapToScene(r.rect().center()).y(),
                            OUTLINE_WIDTH + RECT_WIDTH + SPACING,
                            r.mapToScene(r.rect().center()).y())
            s.addItem(line)
            line.setPen(QPen(color, 5))
            line.setToolTip(self.tr("Plot: ") + name)

        # self.view.fitInView(0, 0, TOTAL_WIDTH, i * LINE_HEIGHT, Qt.KeepAspectRatioByExpanding) # KeepAspectRatio
        self.view.setSceneRect(0, 0, 0, 0)


class OutlineRect(QGraphicsRectItem):
    def __init__(self, x, y, w, h, parent=None):
        QGraphicsRectItem.__init__(self, x, y, w, h, parent)
        self.setBrush(Qt.white)
        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, QGraphicsSceneHoverEvent):
        self.setBrush(Qt.lightGray)

    def hoverLeaveEvent(self, QGraphicsSceneHoverEvent):
        self.setBrush(Qt.white)


class PlotLine(QGraphicsLineItem):
    def __init__(self, x1, y1, x2, y2, parent=None):
        QGraphicsLineItem.__init__(self, x1, y1, x2, y2, parent)
        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, QGraphicsSceneHoverEvent):
        p = self.pen()
        p.setWidth(10)
        self.setPen(p)

    def hoverLeaveEvent(self, QGraphicsSceneHoverEvent):
        p = self.pen()
        p.setWidth(5)
        self.setPen(p)
