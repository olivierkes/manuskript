#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QColor, QPalette, QIcon, QFont, QFontMetrics
from PyQt5.QtWidgets import QStyledItemDelegate, qApp, QStyleOptionViewItem, QStyle

from manuskript import settings
from manuskript.enums import Outline
from manuskript.functions import mixColors, colorifyPixmap
from manuskript.functions import outlineItemColors
from manuskript.functions import toFloat
from manuskript.ui import style as S


class treeTitleDelegate(QStyledItemDelegate):
    """The main purpose of ``treeTitleDelegate`` is to paint outline items
    in the treeview with propers colors according to settings.
    """

    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self._view = None

    def setView(self, view):
        self._view = view

    def paint(self, painter, option, index):

        item = index.internalPointer()
        colors = outlineItemColors(item)

        style = qApp.style()

        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        iconRect = style.subElementRect(style.SE_ItemViewItemDecoration, opt)
        textRect = style.subElementRect(style.SE_ItemViewItemText, opt)

        # Background
        style.drawPrimitive(style.PE_PanelItemViewItem, opt, painter)

        if settings.viewSettings["Tree"]["Background"] != "Nothing" and not opt.state & QStyle.State_Selected:

            col = colors[settings.viewSettings["Tree"]["Background"]]

            if col != QColor(Qt.transparent):
                col2 = QColor(S.window)
                if opt.state & QStyle.State_Selected:
                    col2 = opt.palette.brush(QPalette.Normal, QPalette.Highlight).color()
                col = mixColors(col, col2, .2)

            painter.save()
            painter.setBrush(col)
            painter.setPen(Qt.NoPen)

            rect = opt.rect
            if self._view:
                r2 = self._view.visualRect(index)
                rect = self._view.viewport().rect()
                rect.setLeft(r2.left())
                rect.setTop(r2.top())
                rect.setBottom(r2.bottom())

            painter.drawRoundedRect(rect, 5, 5)
            painter.restore()

        # Icon
        mode = QIcon.Normal
        if not opt.state & QStyle.State_Enabled:
            mode = QIcon.Disabled
        elif opt.state & QStyle.State_Selected:
            mode = QIcon.Selected
        state = QIcon.On if opt.state & QStyle.State_Open else QIcon.Off
        icon = opt.icon.pixmap(iconRect.size(), mode=mode, state=state)
        if opt.icon and settings.viewSettings["Tree"]["Icon"] != "Nothing":
            color = colors[settings.viewSettings["Tree"]["Icon"]]
            colorifyPixmap(icon, color)
        opt.icon = QIcon(icon)
        opt.icon.paint(painter, iconRect, opt.decorationAlignment, mode, state)

        # Text
        if opt.text:
            painter.save()
            textColor = QColor(S.text)
            if option.state & QStyle.State_Selected:
                col = QColor(S.highlightedText)
                textColor = col
                painter.setPen(col)
            if settings.viewSettings["Tree"]["Text"] != "Nothing":
                col = colors[settings.viewSettings["Tree"]["Text"]]
                if col == Qt.transparent:
                    col = textColor
                # If text color is Compile and item is selected, we have
                # to change the color
                if settings.viewSettings["Outline"]["Text"] == "Compile" and \
                   item.compile() in [0, "0"]:
                    col = mixColors(textColor, QColor(S.window))
                painter.setPen(col)
            f = QFont(opt.font)
            painter.setFont(f)
            fm = QFontMetrics(f)
            elidedText = fm.elidedText(opt.text, Qt.ElideRight, textRect.width())
            painter.drawText(textRect, Qt.AlignLeft | Qt.AlignVCenter, elidedText)

            extraText = ""
            if item.isFolder() and settings.viewSettings["Tree"]["InfoFolder"] != "Nothing":
                if settings.viewSettings["Tree"]["InfoFolder"] == "Count":
                    extraText = item.childCount()
                    extraText = " [{}]".format(extraText)
                elif settings.viewSettings["Tree"]["InfoFolder"] == "WC":
                    extraText = item.data(Outline.wordCount.value)
                    extraText = " ({})".format(extraText)
                elif settings.viewSettings["Tree"]["InfoFolder"] == "Progress":
                    extraText = int(toFloat(item.data(Outline.goalPercentage.value)) * 100)
                    if extraText:
                        extraText = " ({}%)".format(extraText)
                elif settings.viewSettings["Tree"]["InfoFolder"] == "Summary":
                    extraText = item.data(Outline.summarySentence.value)
                    if extraText:
                        extraText = " - {}".format(extraText)

            if item.isText() and settings.viewSettings["Tree"]["InfoText"] != "Nothing":
                if settings.viewSettings["Tree"]["InfoText"] == "WC":
                    extraText = item.data(Outline.wordCount.value)
                    extraText = " ({})".format(extraText)
                elif settings.viewSettings["Tree"]["InfoText"] == "Progress":
                    extraText = int(toFloat(item.data(Outline.goalPercentage.value)) * 100)
                    if extraText:
                        extraText = " ({}%)".format(extraText)
                elif settings.viewSettings["Tree"]["InfoText"] == "Summary":
                    extraText = item.data(Outline.summarySentence.value)
                    if extraText:
                        extraText = " - {}".format(extraText)


            if extraText:
                r = QRect(textRect)
                r.setLeft(r.left() + fm.width(opt.text + " "))

                painter.save()
                f = painter.font()
                f.setWeight(QFont.Normal)
                painter.setFont(f)
                if option.state & QStyle.State_Selected:
                    col = QColor(S.highlightedTextLight)
                else:
                    col = QColor(S.textLight)
                painter.setPen(col)
                painter.drawText(r, Qt.AlignLeft | Qt.AlignVCenter, extraText)
                painter.restore()

            painter.restore()

            # QStyledItemDelegate.paint(self, painter, option, index)
