#!/usr/bin/env python
#--!-- coding: utf8 --!--

from qt import *
from enums import *
from functions import *
import settings

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
                col2 = QColor(Qt.white)
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
            if settings.viewSettings["Tree"]["Text"] != "Nothing":
                col = colors[settings.viewSettings["Tree"]["Text"]]
                if col == Qt.transparent:
                    col = Qt.black
                painter.setPen(col)
            f = QFont(opt.font)
            painter.setFont(f)
            fm = QFontMetrics(f)
            elidedText = fm.elidedText(opt.text, Qt.ElideRight, textRect.width())
            painter.drawText(textRect, Qt.AlignLeft, elidedText)
            
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
                
            if item.isText() and settings.viewSettings["Tree"]["InfoText"] != "Nothing":
                if settings.viewSettings["Tree"]["InfoText"] == "WC":
                    extraText = item.data(Outline.wordCount.value)
                    extraText = " ({})".format(extraText)
                elif settings.viewSettings["Tree"]["InfoText"] == "Progress":
                    extraText = int(toFloat(item.data(Outline.goalPercentage.value)) * 100)
                    if extraText:
                        extraText = " ({}%)".format(extraText)    
                
            if extraText:
                
                r = QRect(textRect)
                r.setLeft(r.left() + fm.width(opt.text + " "))
                
                painter.save()
                painter.setPen(Qt.darkGray)
                painter.drawText(r, Qt.AlignLeft | Qt.AlignBottom, extraText)
                painter.restore()
                
            
            painter.restore()
        
        #QStyledItemDelegate.paint(self, painter, option, index)