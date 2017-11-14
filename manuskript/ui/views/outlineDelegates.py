#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt, QSize, QModelIndex
from PyQt5.QtGui import QColor, QPalette, QIcon, QFont, QFontMetrics, QBrush
from PyQt5.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle, QComboBox, QStyleOptionComboBox
from PyQt5.QtWidgets import qApp

from manuskript import settings
from manuskript.enums import Character, Outline
from manuskript.functions import outlineItemColors, mixColors, colorifyPixmap, toInt, toFloat, drawProgress
from manuskript.ui import style as S


class outlineTitleDelegate(QStyledItemDelegate):
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

        if settings.viewSettings["Outline"]["Background"] != "Nothing" and not opt.state & QStyle.State_Selected:

            col = colors[settings.viewSettings["Outline"]["Background"]]

            if col != QColor(Qt.transparent):
                col2 = QColor(S.base)
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
        if opt.icon and settings.viewSettings["Outline"]["Icon"] != "Nothing":
            color = colors[settings.viewSettings["Outline"]["Icon"]]
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
            if settings.viewSettings["Outline"]["Text"] != "Nothing":
                col = colors[settings.viewSettings["Outline"]["Text"]]
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
            painter.drawText(textRect, Qt.AlignLeft, elidedText)

            painter.restore()

            # QStyledItemDelegate.paint(self, painter, option, index)


class outlineCharacterDelegate(QStyledItemDelegate):
    def __init__(self, mdlCharacter, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.mdlCharacter = mdlCharacter

    def sizeHint(self, option, index):
        # s = QStyledItemDelegate.sizeHint(self, option, index)

        item = QModelIndex()
        character = self.mdlCharacter.getCharacterByID(index.data())
        if character:
            item = character.index(Character.name.value)

        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, item)
        s = QStyledItemDelegate.sizeHint(self, opt, item)

        if s.width() > 200:
            s.setWidth(200)
        elif s.width() < 100:
            s.setWidth(100)
        return s + QSize(18, 0)

    def createEditor(self, parent, option, index):
        item = index.internalPointer()
        # if item.isFolder():  # No POV for folders
        # return

        editor = QComboBox(parent)
        editor.setAutoFillBackground(True)
        editor.setFrame(False)
        return editor

    def setEditorData(self, editor, index):
        # editor.addItem("")
        editor.addItem(QIcon.fromTheme("dialog-no"), self.tr("None"))

        l = [self.tr("Main"), self.tr("Secondary"), self.tr("Minor")]
        for importance in range(3):
            editor.addItem(l[importance])
            editor.setItemData(editor.count() - 1, QBrush(QColor(S.highlightedTextDark)), Qt.ForegroundRole)
            editor.setItemData(editor.count() - 1, QBrush(QColor(S.highlightLight)), Qt.BackgroundRole)
            item = editor.model().item(editor.count() - 1)
            item.setFlags(Qt.ItemIsEnabled)
            for i in range(self.mdlCharacter.rowCount()):
                imp = toInt(self.mdlCharacter.importance(i))
                if not 2 - imp == importance: continue

                # try:
                editor.addItem(self.mdlCharacter.icon(i), self.mdlCharacter.name(i), self.mdlCharacter.ID(i))
                editor.setItemData(editor.count() - 1, self.mdlCharacter.name(i), Qt.ToolTipRole)
                # except:
                # pass

        editor.setCurrentIndex(editor.findData(index.data()))
        editor.showPopup()

    def setModelData(self, editor, model, index):
        val = editor.currentData()
        model.setData(index, val)

    def paint(self, painter, option, index):
        ##option.rect.setWidth(option.rect.width() - 18)
        # QStyledItemDelegate.paint(self, painter, option, index)
        ##option.rect.setWidth(option.rect.width() + 18)

        itemIndex = QModelIndex()
        character = self.mdlCharacter.getCharacterByID(index.data())
        if character:
            itemIndex = character.index(Character.name.value)

        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, itemIndex)

        qApp.style().drawControl(QStyle.CE_ItemViewItem, opt, painter)

        # if index.isValid() and index.internalPointer().data(Outline.POV.value) not in ["", None]:
        if itemIndex.isValid() and self.mdlCharacter.data(itemIndex) not in ["", None]:
            opt = QStyleOptionComboBox()
            opt.rect = option.rect
            r = qApp.style().subControlRect(QStyle.CC_ComboBox, opt, QStyle.SC_ComboBoxArrow)
            option.rect = r
            qApp.style().drawPrimitive(QStyle.PE_IndicatorArrowDown, option, painter)


class outlineCompileDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)

    def displayText(self, value, locale):
        return ""


class outlineGoalPercentageDelegate(QStyledItemDelegate):
    def __init__(self, rootIndex=None, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.rootIndex = rootIndex

    def sizeHint(self, option, index):
        sh = QStyledItemDelegate.sizeHint(self, option, index)
        # if sh.width() > 50:
        sh.setWidth(100)
        return sh

    def paint(self, painter, option, index):
        if not index.isValid():
            return QStyledItemDelegate.paint(self, painter, option, index)

        QStyledItemDelegate.paint(self, painter, option, index)

        item = index.internalPointer()

        if not item.data(Outline.goal.value):
            return

        p = toFloat(item.data(Outline.goalPercentage.value))

        typ = item.data(Outline.type.value)

        level = item.level()
        if self.rootIndex and self.rootIndex.isValid():
            level -= self.rootIndex.internalPointer().level() + 1

        margin = 5
        height = max(min(option.rect.height() - 2 * margin, 12) - 2 * level, 6)

        painter.save()

        rect = option.rect.adjusted(margin, margin, -margin, -margin)

        # Move
        rect.translate(level * rect.width() / 10, 0)
        rect.setWidth(rect.width() - level * rect.width() / 10)

        rect.setHeight(height)
        rect.setTop(option.rect.top() + (option.rect.height() - height) / 2)

        drawProgress(painter, rect, p)  # from functions

        painter.restore()

    def displayText(self, value, locale):
        return ""


class outlineStatusDelegate(QStyledItemDelegate):
    def __init__(self, mdlStatus, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.mdlStatus = mdlStatus

    def sizeHint(self, option, index):
        s = QStyledItemDelegate.sizeHint(self, option, index)
        if s.width() > 150:
            s.setWidth(150)
        elif s.width() < 50:
            s.setWidth(50)
        return s + QSize(18, 0)

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.setAutoFillBackground(True)
        editor.setFrame(False)
        return editor

    def setEditorData(self, editor, index):
        for i in range(self.mdlStatus.rowCount()):
            editor.addItem(self.mdlStatus.item(i, 0).text())

        val = index.internalPointer().data(Outline.status.value)
        if not val: val = 0
        editor.setCurrentIndex(int(val))
        editor.showPopup()

    def setModelData(self, editor, model, index):
        val = editor.currentIndex()
        model.setData(index, val)

    def displayText(self, value, locale):
        try:
            return self.mdlStatus.item(int(value), 0).text()
        except:
            return ""

    def paint(self, painter, option, index):
        QStyledItemDelegate.paint(self, painter, option, index)

        if index.isValid() and index.internalPointer().data(Outline.status.value) not in ["", None, "0", 0]:
            opt = QStyleOptionComboBox()
            opt.rect = option.rect
            r = qApp.style().subControlRect(QStyle.CC_ComboBox, opt, QStyle.SC_ComboBoxArrow)
            option.rect = r
            qApp.style().drawPrimitive(QStyle.PE_IndicatorArrowDown, option, painter)


class outlineLabelDelegate(QStyledItemDelegate):
    def __init__(self, mdlLabels, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.mdlLabels = mdlLabels

    def sizeHint(self, option, index):
        d = index.internalPointer().data(index.column(), Qt.DisplayRole)
        if not d:
            d = 0
        item = self.mdlLabels.item(int(d), 0)
        idx = self.mdlLabels.indexFromItem(item)
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, idx)
        s = qApp.style().sizeFromContents(QStyle.CT_ItemViewItem, opt, QSize())
        if s.width() > 150:
            s.setWidth(150)
        elif s.width() < 50:
            s.setWidth(50)
        return s + QSize(18, 0)

    def createEditor(self, parent, option, index):
        item = index.internalPointer()
        editor = QComboBox(parent)
        # editor.setAutoFillBackground(True)
        editor.setFrame(False)
        return editor

    def setEditorData(self, editor, index):
        for i in range(self.mdlLabels.rowCount()):
            editor.addItem(self.mdlLabels.item(i, 0).icon(),
                           self.mdlLabels.item(i, 0).text())

        val = index.internalPointer().data(Outline.label.value)
        if not val: val = 0
        editor.setCurrentIndex(int(val))
        editor.showPopup()

    def setModelData(self, editor, model, index):
        val = editor.currentIndex()
        model.setData(index, val)

    def paint(self, painter, option, index):
        if not index.isValid():
            return QStyledItemDelegate.paint(self, painter, option, index)
        else:
            item = index.internalPointer()

        d = item.data(index.column(), Qt.DisplayRole)
        if not d:
            d = 0

        lbl = self.mdlLabels.item(int(d), 0)
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, self.mdlLabels.indexFromItem(lbl))

        qApp.style().drawControl(QStyle.CE_ItemViewItem, opt, painter)

        # Drop down indicator
        if index.isValid() and index.internalPointer().data(Outline.label.value) not in ["", None, "0", 0]:
            opt = QStyleOptionComboBox()
            opt.rect = option.rect
            r = qApp.style().subControlRect(QStyle.CC_ComboBox, opt, QStyle.SC_ComboBoxArrow)
            option.rect = r
            qApp.style().drawPrimitive(QStyle.PE_IndicatorArrowDown, option, painter)
