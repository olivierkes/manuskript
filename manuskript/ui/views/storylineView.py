#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QBrush, QPen, QFontMetrics, QFontMetricsF, QColor
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QGraphicsSimpleTextItem, QMenu, QAction, QGraphicsRectItem, \
    QGraphicsLineItem, QGraphicsEllipseItem

from manuskript.enums import Outline
from manuskript.models import references
import manuskript.functions as F
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

        self.actPlots = QAction(self.tr("Show Plots"), m)
        self.actPlots.setCheckable(True)
        self.actPlots.setChecked(True)
        self.actPlots.setIcon(F.themeIcon("plots"))
        self.actPlots.toggled.connect(self.reloadTimer.start)
        m.addAction(self.actPlots)

        self.actCharacters = QAction(self.tr("Show Characters"), m)
        self.actCharacters.setCheckable(True)
        self.actCharacters.setChecked(False)
        self.actCharacters.setIcon(F.themeIcon("characters"))
        self.actCharacters.toggled.connect(self.reloadTimer.start)
        m.addAction(self.actCharacters)

        self.btnSettings.setMenu(m)

    def setModels(self, mdlOutline, mdlCharacter, mdlPlots):
        self._mdlPlots = mdlPlots
        # self._mdlPlots.dataChanged.connect(self.refresh)
        # self._mdlPlots.rowsInserted.connect(self.refresh)

        self._mdlOutline = mdlOutline
        self._mdlOutline.dataChanged.connect(self.updateMaybe)

        self._mdlCharacter = mdlCharacter
        self._mdlCharacter.dataChanged.connect(self.reloadTimer.start)

    def updateMaybe(self, topLeft, bottomRight):
        if topLeft.column() <= Outline.notes.value <= bottomRight.column():
            self.reloadTimer.start

    def plotReferences(self):
        "Returns a list of plot references"
        if not self._mdlPlots:
            pass

        plotsID = self._mdlPlots.getPlotsByImportance()
        r = []
        for importance in plotsID:
            for ID in importance:
                ref = references.plotReference(ID)
                r.append(ref)

        return r

    def charactersReferences(self):
        "Returns a list of character references"
        if not self._mdlCharacter:
            pass

        chars = self._mdlCharacter.getCharactersByImportance()
        r = []
        for importance in chars:
            for c in importance:
                ref = references.characterReference(c.ID())
                r.append(ref)

        return r

    def refresh(self):
        if not self._mdlPlots or not self._mdlOutline or not self._mdlCharacter:
            return

        if not self.isVisible():
            return

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

        # Get the list of tracked items (array of references)
        trackedItems = []

        if self.actPlots.isChecked():
            trackedItems += self.plotReferences()

        if self.actCharacters.isChecked():
            trackedItems += self.charactersReferences()

        ROWS_HEIGHT = len(trackedItems) * (LINE_HEIGHT + SPACING )

        fm = QFontMetrics(s.font())
        max_name = 0
        for ref in trackedItems:
            name = references.title(ref)
            max_name = max(fm.width(name), max_name)

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
                    for ref in trackedItems:

                        result = []

                        # Tests if POV
                        scenePOV = False  # Will hold true of character is POV of the current text, not containing folder
                        if references.type(ref) == references.CharacterLetter:
                            ID = references.ID(ref)
                            c = child
                            while c:
                                if c.POV() == ID:
                                    result.append(c.ID())
                                    if c == child: scenePOV = True
                                c = c.parent()

                        # Search in notes/references
                        c = child
                        while c:
                            result += references.findReferencesTo(ref, c, recursive=False)
                            c = c.parent()

                        if result:
                            ref2 = result[0]
                            
                            # Create a RefCircle with the reference
                            c = RefCircle(TEXT_WIDTH / 2, - CIRCLE_WIDTH / 2, CIRCLE_WIDTH, ID=ref2, important=scenePOV)
                            
                            # Store it, with the position of that item, to display it on the line later on
                            refCircles.append((ref, c, rect.mapToItem(outline, rectChild.pos())))

                delta += w

        listItems(root, outline)

        OUTLINE_WIDTH = itemWidth(root)

        # Add Tracked items
        i = 0
        itemsRect = s.addRect(0, 0, 0, 0)
        itemsRect.setPos(0, MAX_LEVEL * LEVEL_HEIGHT + SPACING)

        # Set of colors for plots (as long as they don't have their own colors)
        colors = [
            "#D97777", "#AE5F8C", "#D9A377", "#FFC2C2", "#FFDEC2", "#D2A0BC",
            "#7B0F0F", "#7B400F", "#620C3D", "#AA3939", "#AA6C39", "#882D61",
            "#4C0000", "#4C2200", "#3D0022",
        ]

        for ref in trackedItems:
            if references.type(ref) == references.CharacterLetter:
                color = self._mdlCharacter.getCharacterByID(references.ID(ref)).color()
            else:
                color = QColor(colors[i % len(colors)])

            # Rect
            r = QGraphicsRectItem(0, 0, TITLE_WIDTH, LINE_HEIGHT, itemsRect)
            r.setPen(QPen(Qt.NoPen))
            r.setBrush(QBrush(color))
            r.setPos(0, i * LINE_HEIGHT + i * SPACING)
            r.setToolTip(references.tooltip(ref))
            i += 1

            # Text
            name = references.title(ref)
            txt = QGraphicsSimpleTextItem(name, r)
            txt.setPos(r.boundingRect().center() - txt.boundingRect().center())

            # Line
            line = PlotLine(0, 0,
                            OUTLINE_WIDTH + SPACING, 0)
            line.setPos(TITLE_WIDTH, r.mapToScene(r.rect().center()).y())
            s.addItem(line)
            line.setPen(QPen(color, 5))
            line.setToolTip(references.tooltip(ref))

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
    def __init__(self, x, y, diameter, parent=None, ID=None, important=False):
        QGraphicsEllipseItem.__init__(self, x, y, diameter, diameter, parent)
        self.setBrush(Qt.white)
        self._ref = references.textReference(ID)
        self.setToolTip(references.tooltip(self._ref))
        self.setPen(QPen(Qt.black, 2))
        self.setAcceptHoverEvents(True)
        if important:
            self.setBrush(Qt.black)

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
