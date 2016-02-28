#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QBrush, QPen, QFontMetrics, QFontMetricsF
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QGraphicsSimpleTextItem, QMenu, QAction, QGraphicsRectItem, \
    QGraphicsLineItem, QGraphicsEllipseItem

from manuskript.enums import Outline
from manuskript.functions import randomColor
from manuskript.models import references
from manuskript.ui.views.storylineView_ui import Ui_storylineView


class storylineView(QWidget, Ui_storylineView):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self._mdlPlots = None
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)

        self.reloadTimer = QTimer()
        self.reloadTimer.timeout.connect(self.refresh)
        self.reloadTimer.setSingleShot(True)
        self.reloadTimer.setInterval(500)

        self.btnRefresh.clicked.connect(self.refresh)
        self.sldTxtSize.sliderMoved.connect(self.reloadTimer.start)

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

        LINE_HEIGHT = 18
        SPACING = 3
        TEXT_WIDTH = self.sldTxtSize.value()
        CIRCLE_WIDTH = 10
        LEVEL_HEIGHT = 12

        s = self.scene
        s.clear()

        # Get Max Level (max depth)
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

        # Generate left entries
        # (As of now, plot only)
        plotsID = self._mdlPlots.getPlotsByImportance()
        trackedItems = []
        fm = QFontMetrics(s.font())
        max_name = 0

        for importance in plotsID:
            for ID in importance:
                name = self._mdlPlots.getPlotNameByID(ID)
                ref = references.plotReference(ID, searchable=True)

                trackedItems.append((ID, ref, name))
                max_name = max(fm.width(name), max_name)

        ROWS_HEIGHT = len(trackedItems) * (LINE_HEIGHT + SPACING )
        TITLE_WIDTH = max_name + 2 * SPACING


        # Add Folders and Texts
        outline = OutlineRect(0, 0, 0, ROWS_HEIGHT + SPACING + MAX_LEVEL * LEVEL_HEIGHT)
        s.addItem(outline)
        outline.setPos(TITLE_WIDTH + SPACING, 0)

        refCircles = [] # a list of all references, to be added later on the lines

        # A Function to add a rect with centered elided text
        def addRectText(x, w, parent, text="", level=0, tooltip=""):
            deltaH = LEVEL_HEIGHT if level else 0
            r = OutlineRect(0, 0, w, parent.rect().height()-deltaH, parent, title=text)
            r.setPos(x, deltaH)

            txt = QGraphicsSimpleTextItem(text, r)
            f = txt.font()
            f.setPointSize(8)
            fm = QFontMetricsF(f)
            elidedText = fm.elidedText(text, Qt.ElideMiddle, w)
            txt.setFont(f)
            txt.setText(elidedText)
            txt.setPos(r.boundingRect().center() - txt.boundingRect().center())
            txt.setY(0)
            return r

        # A function to returns an item's width, by counting its children
        def itemWidth(item):
            if item.isFolder():
                r = 0
                for c in item.children():
                    r += itemWidth(c)
                return r or TEXT_WIDTH
            else:
                return TEXT_WIDTH

        def listItems(item, rect, level=0):
            delta = 0
            for child in item.children():
                w = itemWidth(child)

                if child.isFolder():
                    parent = addRectText(delta, w, rect, child.title(), level, tooltip=child.title())
                    parent.setToolTip(references.tooltip(references.textReference(child.ID())))
                    listItems(child, parent, level + 1)

                else:
                    rectChild = addRectText(delta, TEXT_WIDTH, rect, "", level, tooltip=child.title())
                    rectChild.setToolTip(references.tooltip(references.textReference(child.ID())))
                    
                    # Find tracked references in that scene (or parent folders)
                    for ID, ref, name in trackedItems:

                        result = []
                        c = child
                        while c:
                            result += references.findReferencesTo(ref, c, recursive=False)
                            c = c.parent()

                        if result:
                            ref2 = result[0]
                            
                            # Create a RefCircle with the reference
                            c = RefCircle(TEXT_WIDTH / 2, - CIRCLE_WIDTH / 2, CIRCLE_WIDTH, ID=ref2)
                            
                            # Store it, with the position of that item, to display it on the line later on
                            refCircles.append((ref, c, rect.mapToItem(outline, rectChild.pos())))

                delta += w

        listItems(root, outline)

        OUTLINE_WIDTH = itemWidth(root)

        # Add Plots
        i = 0
        itemsRect = s.addRect(0, 0, 0, 0)
        itemsRect.setPos(0, MAX_LEVEL * LEVEL_HEIGHT + SPACING)

        for ID, ref, name in trackedItems:
            color = randomColor()

            # Rect
            r = QGraphicsRectItem(0, 0, TITLE_WIDTH, LINE_HEIGHT, itemsRect)
            r.setPen(QPen(Qt.NoPen))
            r.setBrush(QBrush(color))
            r.setPos(0, i * LINE_HEIGHT + i * SPACING)
            i += 1

            # Text
            txt = QGraphicsSimpleTextItem(name, r)
            txt.setPos(r.boundingRect().center() - txt.boundingRect().center())

            # Line
            line = PlotLine(0, 0,
                            OUTLINE_WIDTH + SPACING, 0)
            line.setPos(TITLE_WIDTH, r.mapToScene(r.rect().center()).y())
            s.addItem(line)
            line.setPen(QPen(color, 5))
            line.setToolTip(self.tr("Plot: ") + name)

            # We add the circles / references to text, on the line
            for ref2, circle, pos in refCircles:
                if ref2 == ref:
                    circle.setParentItem(line)
                    circle.setPos(pos.x(), 0)

        # self.view.fitInView(0, 0, TOTAL_WIDTH, i * LINE_HEIGHT, Qt.KeepAspectRatioByExpanding) # KeepAspectRatio
        self.view.setSceneRect(0, 0, 0, 0)


class OutlineRect(QGraphicsRectItem):
    def __init__(self, x, y, w, h, parent=None, title=None):
        QGraphicsRectItem.__init__(self, x, y, w, h, parent)
        self.setBrush(Qt.white)
        self.setAcceptHoverEvents(True)
        self._title = title

    def hoverEnterEvent(self, event):
        self.setBrush(Qt.lightGray)

    def hoverLeaveEvent(self, event):
        self.setBrush(Qt.white)


class RefCircle(QGraphicsEllipseItem):
    def __init__(self, x, y, diameter, parent=None, ID=None):
        QGraphicsEllipseItem.__init__(self, x, y, diameter, diameter, parent)
        self.setBrush(Qt.white)
        self._ref = references.textReference(ID)
        self.setToolTip(references.tooltip(self._ref))
        self.setPen(QPen(Qt.black, 2))
        self.setAcceptHoverEvents(True)

    def multiplyDiameter(self, factor):
        r1 = self.rect()
        r2 = QRectF(0, 0, r1.width() * factor, r1.height() * factor)
        self.setRect(r2)
        self.setPos(self.pos() + r1.center() - r2.center())

    def mouseDoubleClickEvent(self, event):
        references.open(self._ref)

    def hoverEnterEvent(self, event):
        self.multiplyDiameter(2)

    def hoverLeaveEvent(self, event):
        self.multiplyDiameter(.5)


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
