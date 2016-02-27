#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QGraphicsSimpleTextItem, QMenu, QAction

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

    def setModel(self, mdlPlots):
        self._mdlPlots = mdlPlots
        self._mdlPlots.dataChanged.connect(self.refresh)
        self._mdlPlots.rowsInserted.connect(self.refresh)

    def refresh(self):
        if not self._mdlPlots:
            pass

        LINE_HEIGHT = 32
        LINE_SPACING = 6
        RECT_WIDTH = 200
        TOTAL_WIDTH = 4000

        s = self.scene
        s.clear()
        plotsID = self._mdlPlots.getPlotsByImportance()
        i = 0

        plots = []

        # Add Plots
        for importance in plotsID:
            for ID in importance:
                name = self._mdlPlots.getPlotNameByID(ID)
                print(ID, name)
                color = randomColor()

                # Rect
                r = s.addRect(0, 0, RECT_WIDTH, LINE_HEIGHT)
                r.setPen(QPen(Qt.NoPen))
                r.setBrush(QBrush(color))
                r.setPos(0, i * LINE_HEIGHT + i * LINE_SPACING)
                i += 1

                # Text
                txt = QGraphicsSimpleTextItem(name, r)
                txt.setPos(r.boundingRect().center() - txt.boundingRect().center())

                # Line
                line = s.addLine(10, LINE_HEIGHT / 2, TOTAL_WIDTH, LINE_HEIGHT / 2)
                line.setParentItem(r)
                line.setPen(QPen(color, 5))
                line.setZValue(-10)

                plots.append((ID, r))


        # Add Folders and Texts


        # self.view.fitInView(0, 0, TOTAL_WIDTH, i * LINE_HEIGHT, Qt.KeepAspectRatioByExpanding) # KeepAspectRatio
        self.view.setSceneRect()
