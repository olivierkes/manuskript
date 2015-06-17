#!/usr/bin/env python
#--!-- coding: utf8 --!--

from qt import *
from enums import *
from functions import *
import settings

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
        if opt.icon and settings.viewSettings["Outline"]["Icon"] != "Nothing":
            color = colors[settings.viewSettings["Outline"]["Icon"]]
            colorifyPixmap(icon, color)
        opt.icon = QIcon(icon)
        opt.icon.paint(painter, iconRect, opt.decorationAlignment, mode, state)
        
        # Text
        if opt.text:
            painter.save()
            if settings.viewSettings["Outline"]["Text"] != "Nothing":
                col = colors[settings.viewSettings["Outline"]["Text"]]
                if col == Qt.transparent:
                    col = Qt.black
                painter.setPen(col)
            f = QFont(opt.font)
            painter.setFont(f)
            fm = QFontMetrics(f)
            elidedText = fm.elidedText(opt.text, Qt.ElideRight, textRect.width())
            painter.drawText(textRect, Qt.AlignLeft, elidedText)
            
            painter.restore()
        
        #QStyledItemDelegate.paint(self, painter, option, index)

class outlinePersoDelegate(QStyledItemDelegate):
    
    def __init__(self, mdlPersos, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.mdlPersos = mdlPersos
        
    def sizeHint(self, option, index):
        s = QStyledItemDelegate.sizeHint(self, option, index)
        if s.width() > 200:
            s.setWidth(200)
        elif s.width() < 100:
            s.setWidth(100)
        return s + QSize(18, 0)
    
    def createEditor(self, parent, option, index):
        item = index.internalPointer()
        #if item.isFolder():  # No POV for folders
            #return
        
        editor = QComboBox(parent)
        editor.setAutoFillBackground(True)
        editor.setFrame(False)
        return editor
    
    def setEditorData(self, editor, index):
        #editor.addItem("")
        editor.addItem(QIcon.fromTheme("edit-delete"), self.tr("None"))
        #for i in range(self.mdlPersos.rowCount()):
            #editor.addItem(self.mdlPersos.item(i, Perso.name.value).text(), self.mdlPersos.item(i, Perso.ID.value).text())
            #editor.setItemData(i+1, self.mdlPersos.item(i, Perso.name.value).text(), Qt.ToolTipRole)
        
        l = [self.tr("Main"), self.tr("Secondary"), self.tr("Minor")]
        for importance in range(3):
            editor.addItem(l[importance])
            editor.setItemData(editor.count()-1, QBrush(Qt.darkBlue), Qt.ForegroundRole)
            editor.setItemData(editor.count()-1, QBrush(QColor(Qt.blue).lighter(190)), Qt.BackgroundRole)
            item = editor.model().item(editor.count()-1)
            item.setFlags(Qt.ItemIsEnabled)
            for i in range(self.mdlPersos.rowCount()):
                imp = self.mdlPersos.item(i, Perso.importance.value)
                if imp:
                    imp = toInt(imp.text())
                else:
                    imp = 0
                if not 2-imp == importance: continue
                
                try:
                    editor.addItem(self.mdlPersos.item(i, Perso.name.value).text(), self.mdlPersos.item(i, Perso.ID.value).text())
                    editor.setItemData(i+1, self.mdlPersos.item(i, Perso.name.value).text(), Qt.ToolTipRole)
                except:
                    pass
        
        editor.setCurrentIndex(editor.findData(index.data()))
        editor.showPopup()
    
    def setModelData(self, editor, model, index):
        val = editor.currentData()
        model.setData(index, val)
    
    def displayText(self, value, locale):
        for i in range(self.mdlPersos.rowCount()):
            if self.mdlPersos.item(i, Perso.ID.value).text() == value:
                return self.mdlPersos.item(i, Perso.name.value).text()
        return ""
    
    def paint(self, painter, option, index):
        #option.rect.setWidth(option.rect.width() - 18)
        QStyledItemDelegate.paint(self, painter, option, index)
        #option.rect.setWidth(option.rect.width() + 18)
        
        if index.isValid() and index.internalPointer().data(Outline.POV.value) not in ["", None]:
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
        #if sh.width() > 50:
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
        height = max(min(option.rect.height() - 2*margin, 12) - 2 * level, 6)
        
        painter.save()
        
        rect = option.rect.adjusted(margin, margin, -margin, -margin)
        
        # Move
        rect.translate(level * rect.width() / 10, 0)
        rect.setWidth(rect.width() - level * rect.width() / 10)
        
        rect.setHeight(height)
        rect.setTop(option.rect.top() + (option.rect.height() - height) / 2)
        
        drawProgress(painter, rect, p) # from functions
        
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
        
        if index.isValid() and index.internalPointer().data(Outline.status.value) not in ["", None, "0"]:
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
        #editor.setAutoFillBackground(True)
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
        if index.isValid() and index.internalPointer().data(Outline.label.value) not in ["", None, "0"]:
            opt = QStyleOptionComboBox()
            opt.rect = option.rect
            r = qApp.style().subControlRect(QStyle.CC_ComboBox, opt, QStyle.SC_ComboBoxArrow)
            option.rect = r
            qApp.style().drawPrimitive(QStyle.PE_IndicatorArrowDown, option, painter)
        