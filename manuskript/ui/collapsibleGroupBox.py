#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt, QRect, QRectF
from PyQt5.QtGui import QColor, QBrush, QRegion, QTextOption, QFont
from PyQt5.QtWidgets import QSizePolicy, QGroupBox, QWidget, QStylePainter, QStyleOptionGroupBox, qApp, QVBoxLayout, \
    QStyle, QStyleOptionFrame, QStyleOptionFocusRect
from manuskript.ui import style as S


class collapsibleGroupBox(QGroupBox):
    def __init__(self, parent=None):
        QGroupBox.__init__(self)

        self.toggled.connect(self.setExpanded)
        self.tempWidget = QWidget()

        self.customStyle = False

    def setExpanded(self, val):
        self.setCollapsed(not val)

    def setCollapsed(self, val):
        if val:
            # Save layout
            self.tempWidget.setLayout(self.layout())
            # Set empty layout
            l = QVBoxLayout()
            # print(l.contentsMargins().left(), l.contentsMargins().bottom(), l.contentsMargins().top(), )
            l.setContentsMargins(0, 0, 0, 0)
            self.setLayout(l)
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        else:
            # Delete layout
            QWidget().setLayout(self.layout())
            # Set saved layout
            self.setLayout(self.tempWidget.layout())
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    def paintEvent(self, event):

        if not self.customStyle:
            return QGroupBox.paintEvent(self, event)

        p = QStylePainter(self)
        opt = QStyleOptionGroupBox()
        self.initStyleOption(opt)

        style = qApp.style()
        groupBox = opt

        # // Draw frame
        textRect = style.subControlRect(style.CC_GroupBox, opt, style.SC_GroupBoxLabel)
        checkBoxRect = style.subControlRect(style.CC_GroupBox, opt, style.SC_GroupBoxCheckBox)

        p.save()
        titleRect = style.subControlRect(style.CC_GroupBox, opt, style.SC_GroupBoxFrame)
        # r.setBottom(style.subControlRect(style.CC_GroupBox, opt, style.SC_GroupBoxContents).top())
        titleRect.setHeight(textRect.height())
        titleRect.moveTop(textRect.top())

        p.setBrush(QBrush(QColor(S.highlightLight)))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(titleRect, 10, 10)
        p.restore()

        if groupBox.subControls & QStyle.SC_GroupBoxFrame:
            frame = QStyleOptionFrame()
            # frame.operator=(groupBox)
            frame.state = groupBox.state
            frame.features = groupBox.features
            frame.lineWidth = groupBox.lineWidth
            frame.midLineWidth = groupBox.midLineWidth
            frame.rect = style.subControlRect(style.CC_GroupBox, opt, style.SC_GroupBoxFrame)
            p.save()
            region = QRegion(groupBox.rect)
            if groupBox.text:
                ltr = groupBox.direction == Qt.LeftToRight
                finalRect = QRect()
                if groupBox.subControls & QStyle.SC_GroupBoxCheckBox:
                    finalRect = checkBoxRect.united(textRect)
                    finalRect.adjust(-4 if ltr else 0, 0, 0 if ltr else 4, 0)
                else:
                    finalRect = textRect

                region -= QRegion(finalRect)

            p.setClipRegion(region)
            style.drawPrimitive(style.PE_FrameGroupBox, frame, p)
            p.restore()

        # // Draw title
        if groupBox.subControls & QStyle.SC_GroupBoxLabel and groupBox.text:
            # textColor = QColor(groupBox.textColor)
            # if textColor.isValid():
            # p.setPen(textColor)
            # alignment = int(groupBox.textAlignment)
            # if not style.styleHint(QStyle.SH_UnderlineShortcut, opt):
            # alignment |= Qt.TextHideMnemonic

            # style.drawItemText(p, textRect,  Qt.TextShowMnemonic | Qt.AlignHCenter | alignment,
            # groupBox.palette, groupBox.state & style.State_Enabled, groupBox.text,
            # QPalette.NoRole if textColor.isValid() else QPalette.WindowText)

            p.save()
            topt = QTextOption(Qt.AlignHCenter | Qt.AlignVCenter)
            f = QFont()
            f.setBold(True)
            p.setFont(f)
            p.setPen(QColor(S.highlightedTextDark))
            p.drawText(QRectF(titleRect), groupBox.text.replace("&", ""), topt)
            p.restore()

            if groupBox.state & style.State_HasFocus:
                fropt = QStyleOptionFocusRect()
                # fropt.operator=(groupBox)
                fropt.state = groupBox.state
                fropt.rect = textRect
                style.drawPrimitive(style.PE_FrameFocusRect, fropt, p)

                # // Draw checkbox
                # if groupBox.subControls & style.SC_GroupBoxCheckBox:
                # box = QStyleOptionButton()
                # box.operator=(groupBox)
                # box.state = groupBox.state
                # box.rect = checkBoxRect
                # style.drawPrimitive(style.PE_IndicatorCheckBox, box, p)
