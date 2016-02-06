#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import QSize, Qt, QRect, QPoint
from PyQt5.QtGui import QMouseEvent, QFont, QPalette, QRegion, QFontMetrics, QColor, QIcon
from PyQt5.QtWidgets import QStyledItemDelegate, QLineEdit, QPlainTextEdit, QFrame, qApp, QStyle

from manuskript import settings
from manuskript.enums import Outline
from manuskript.functions import colorifyPixmap
from manuskript.functions import mainWindow
from manuskript.functions import mixColors
from manuskript.functions import outlineItemColors


class corkDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.factor = settings.corkSizeFactor / 100.
        self.defaultSize = QSize(300, 200)
        self.lastPos = None
        self.editing = None
        self.margin = 5

    def setCorkSizeFactor(self, v):
        self.factor = v / 100.

    def sizeHint(self, option, index):
        return self.defaultSize * self.factor

    def editorEvent(self, event, model, option, index):
        # We catch the mouse position in the widget to know which part to edit
        if type(event) == QMouseEvent:
            self.lastPos = event.pos()  # - option.rect.topLeft()
        return QStyledItemDelegate.editorEvent(self, event, model, option, index)

    def createEditor(self, parent, option, index):
        self.updateRects(option, index)

        if self.mainLineRect.contains(self.lastPos):
            # One line summary
            self.editing = Outline.summarySentance
            edt = QLineEdit(parent)
            edt.setFocusPolicy(Qt.StrongFocus)
            edt.setFrame(False)
            edt.setAlignment(Qt.AlignCenter)
            edt.setPlaceholderText(self.tr("One line summary"))
            f = QFont(option.font)
            f.setItalic(True)
            edt.setFont(f)
            return edt

        elif self.titleRect.contains(self.lastPos):
            # Title
            self.editing = Outline.title
            edt = QLineEdit(parent)
            edt.setFocusPolicy(Qt.StrongFocus)
            edt.setFrame(False)
            f = QFont(option.font)
            # f.setPointSize(f.pointSize() + 1)
            f.setBold(True)
            edt.setFont(f)
            edt.setAlignment(Qt.AlignCenter)
            # edt.setGeometry(self.titleRect)
            return edt

        else:  # self.mainTextRect.contains(self.lastPos):
            # Summary
            self.editing = Outline.summaryFull
            edt = QPlainTextEdit(parent)
            edt.setFocusPolicy(Qt.StrongFocus)
            edt.setFrameShape(QFrame.NoFrame)
            edt.setPlaceholderText(self.tr("Full summary"))
            return edt

    def updateEditorGeometry(self, editor, option, index):

        if self.editing == Outline.summarySentance:
            # One line summary
            editor.setGeometry(self.mainLineRect)

        elif self.editing == Outline.title:
            # Title
            editor.setGeometry(self.titleRect)

        elif self.editing == Outline.summaryFull:
            # Summary
            editor.setGeometry(self.mainTextRect)

    def setEditorData(self, editor, index):
        item = index.internalPointer()

        if self.editing == Outline.summarySentance:
            # One line summary
            editor.setText(item.data(Outline.summarySentance.value))

        elif self.editing == Outline.title:
            # Title
            editor.setText(index.data())

        elif self.editing == Outline.summaryFull:
            # Summary
            editor.setPlainText(item.data(Outline.summaryFull.value))

    def setModelData(self, editor, model, index):

        if self.editing == Outline.summarySentance:
            # One line summary
            model.setData(index.sibling(index.row(), Outline.summarySentance.value), editor.text())

        elif self.editing == Outline.title:
            # Title
            model.setData(index, editor.text(), Outline.title.value)

        elif self.editing == Outline.summaryFull:
            # Summary
            model.setData(index.sibling(index.row(), Outline.summaryFull.value), editor.toPlainText())

    def updateRects(self, option, index):
        margin = self.margin
        iconSize = max(16 * self.factor, 12)
        item = index.internalPointer()
        self.itemRect = option.rect.adjusted(margin, margin, -margin, -margin)
        self.iconRect = QRect(self.itemRect.topLeft() + QPoint(margin, margin), QSize(iconSize, iconSize))
        self.labelRect = QRect(self.itemRect.topRight() - QPoint(iconSize + margin, 0),
                               self.itemRect.topRight() + QPoint(0, iconSize + 2 * margin))
        self.titleRect = QRect(self.iconRect.topRight() + QPoint(margin, 0),
                               self.labelRect.bottomLeft() - QPoint(margin, margin))
        self.bottomRect = QRect(QPoint(self.itemRect.x(), self.iconRect.bottom() + margin),
                                QPoint(self.itemRect.right(), self.itemRect.bottom()))
        self.topRect = QRect(self.itemRect.topLeft(), self.bottomRect.topRight())
        self.mainRect = self.bottomRect.adjusted(margin, margin, -margin, -margin)
        self.mainLineRect = QRect(self.mainRect.topLeft(),
                                  self.mainRect.topRight() + QPoint(0, iconSize))
        self.mainTextRect = QRect(self.mainLineRect.bottomLeft() + QPoint(0, margin),
                                  self.mainRect.bottomRight())
        if not item.data(Outline.summarySentance.value):
            self.mainTextRect.setTopLeft(self.mainLineRect.topLeft())
        if item.data(Outline.label.value) in ["", "0"]:
            self.titleRect.setBottomRight(self.labelRect.bottomRight() - QPoint(self.margin, self.margin))

    def paint(self, p, option, index):
        # QStyledItemDelegate.paint(self, p, option, index)
        if not index.isValid():
            return

        item = index.internalPointer()
        self.updateRects(option, index)
        colors = outlineItemColors(item)

        style = qApp.style()

        def _rotate(angle):
            p.translate(self.mainRect.center())
            p.rotate(angle)
            p.translate(-self.mainRect.center())

        # Draw background
        cg = QPalette.ColorGroup(QPalette.Normal if option.state & QStyle.State_Enabled else QPalette.Disabled)
        if cg == QPalette.Normal and not option.state & QStyle.State_Active:
            cg = QPalette.Inactive

            # Selection
        if option.state & QStyle.State_Selected:
            p.save()
            p.setBrush(option.palette.brush(cg, QPalette.Highlight))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(option.rect, 12, 12)
            p.restore()

            # Stack
        if item.isFolder() and item.childCount() > 0:
            p.save()
            p.setBrush(Qt.white)
            for i in reversed(range(3)):
                p.drawRoundedRect(self.itemRect.adjusted(2 * i, 2 * i, -2 * i, 2 * i), 10, 10)

            p.restore()

            # Background
        itemRect = self.itemRect
        p.save()
        if settings.viewSettings["Cork"]["Background"] != "Nothing":
            c = colors[settings.viewSettings["Cork"]["Background"]]
            col = mixColors(c, QColor(Qt.white), .2)
            p.setBrush(col)
        else:
            p.setBrush(Qt.white)
        pen = p.pen()
        pen.setWidth(2)
        p.setPen(pen)
        p.drawRoundedRect(itemRect, 10, 10)
        p.restore()

        # Title bar
        topRect = self.topRect
        p.save()
        if item.isFolder():
            color = QColor(Qt.darkGreen)
        else:
            color = QColor(Qt.blue).lighter(175)
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        p.setClipRegion(QRegion(topRect))
        p.drawRoundedRect(itemRect, 10, 10)
        # p.drawRect(topRect)
        p.restore()

        # Label color
        if settings.viewSettings["Cork"]["Corner"] != "Nothing":
            p.save()
            color = colors[settings.viewSettings["Cork"]["Corner"]]
            p.setPen(Qt.NoPen)
            p.setBrush(color)
            p.setClipRegion(QRegion(self.labelRect))
            p.drawRoundedRect(itemRect, 10, 10)
            # p.drawRect(topRect)
            p.restore()
            p.drawLine(self.labelRect.topLeft(), self.labelRect.bottomLeft())

            # One line summary background
        lineSummary = item.data(Outline.summarySentance.value)
        fullSummary = item.data(Outline.summaryFull.value)
        if lineSummary or not fullSummary:
            m = self.margin
            r = self.mainLineRect.adjusted(-m, -m, m, m / 2)
            p.save()
            p.setPen(Qt.NoPen)
            p.setBrush(QColor("#EEE"))
            p.drawRect(r)
            p.restore()

            # Border
        p.save()
        p.setBrush(Qt.NoBrush)
        pen = p.pen()
        pen.setWidth(2)
        if settings.viewSettings["Cork"]["Border"] != "Nothing":
            col = colors[settings.viewSettings["Cork"]["Border"]]
            if col == Qt.transparent:
                col = Qt.black
            pen.setColor(col)
        p.setPen(pen)
        p.drawRoundedRect(itemRect, 10, 10)
        p.restore()

        # Draw the icon
        iconRect = self.iconRect
        mode = QIcon.Normal
        if not option.state & style.State_Enabled:
            mode = QIcon.Disabled
        elif option.state & style.State_Selected:
            mode = QIcon.Selected
        # index.data(Qt.DecorationRole).paint(p, iconRect, option.decorationAlignment, mode)
        icon = index.data(Qt.DecorationRole).pixmap(iconRect.size())
        if settings.viewSettings["Cork"]["Icon"] != "Nothing":
            color = colors[settings.viewSettings["Cork"]["Icon"]]
            colorifyPixmap(icon, color)
        QIcon(icon).paint(p, iconRect, option.decorationAlignment, mode)

        # Draw title
        p.save()
        text = index.data()
        titleRect = self.titleRect
        if text:
            if settings.viewSettings["Cork"]["Text"] != "Nothing":
                col = colors[settings.viewSettings["Cork"]["Text"]]
                if col == Qt.transparent:
                    col = Qt.black
                p.setPen(col)
            f = QFont(option.font)
            # f.setPointSize(f.pointSize() + 1)
            f.setBold(True)
            p.setFont(f)
            fm = QFontMetrics(f)
            elidedText = fm.elidedText(text, Qt.ElideRight, titleRect.width())
            p.drawText(titleRect, Qt.AlignCenter, elidedText)
        p.restore()

        # Draw the line
        bottomRect = self.bottomRect
        p.save()
        # p.drawLine(itemRect.x(), iconRect.bottom() + margin,
        # itemRect.right(), iconRect.bottom() + margin)
        p.drawLine(bottomRect.topLeft(), bottomRect.topRight())
        p.restore()

        # Lines
        if True:
            p.save()
            p.setPen(QColor("#EEE"))
            fm = QFontMetrics(option.font)
            h = fm.lineSpacing()
            l = self.mainTextRect.topLeft() + QPoint(0, h)
            while self.mainTextRect.contains(l):
                p.drawLine(l, QPoint(self.mainTextRect.right(), l.y()))
                l.setY(l.y() + h)
            p.restore()

        # Draw status
        mainRect = self.mainRect
        status = item.data(Outline.status.value)
        if status:
            it = mainWindow().mdlStatus.item(int(status), 0)
            if it != None:
                p.save()
                p.setClipRegion(QRegion(mainRect))
                f = p.font()
                f.setPointSize(f.pointSize() + 12)
                f.setBold(True)
                p.setFont(f)
                p.setPen(QColor(Qt.red).lighter(175))
                _rotate(-35)
                p.drawText(mainRect, Qt.AlignCenter, it.text())
                p.restore()

                # Draw Summary
                # One line
        if lineSummary:
            p.save()
            f = QFont(option.font)
            f.setItalic(True)
            p.setFont(f)
            fm = QFontMetrics(f)
            elidedText = fm.elidedText(lineSummary, Qt.ElideRight, self.mainLineRect.width())
            p.drawText(self.mainLineRect, Qt.AlignCenter, elidedText)
            p.restore()

            # Full summary
        if fullSummary:
            p.setFont(option.font)
            p.drawText(self.mainTextRect, Qt.TextWordWrap, fullSummary)

            # Debug
            # for r in [self.itemRect, self.iconRect, self.titleRect, self.bottomRect, self.mainLineRect, self.mainTextRect]:
            # p.drawRect(r)
