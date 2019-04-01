#!/usr/bin/env python
# --!-- coding: utf8 --!--
import os

from PyQt5.QtCore import Qt, QSize, QPoint, QRect, QEvent, QTime, QTimer
from PyQt5.QtGui import QFontMetrics, QColor, QBrush, QPalette, QPainter, QPixmap, QCursor
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QWidget, QPushButton, qApp, QStyle, QComboBox, QLabel, QScrollBar, \
    QStyleOptionSlider, QHBoxLayout, QVBoxLayout, QMenu, QAction

# Spell checker support
from manuskript import settings
from manuskript.enums import Outline
from manuskript.models import outlineItem
from manuskript.functions import allPaths, drawProgress
from manuskript.ui.editors.locker import locker
from manuskript.ui.editors.themes import findThemePath, generateTheme, setThemeEditorDatas
from manuskript.ui.editors.themes import loadThemeDatas
from manuskript.ui.views.MDEditView import MDEditView

try:
    import enchant
except ImportError:
    enchant = None


class fullScreenEditor(QWidget):
    def __init__(self, index, parent=None):
        QWidget.__init__(self, parent)
        self._background = None
        self._index = index
        self._theme = findThemePath(settings.fullScreenTheme)
        self._themeDatas = loadThemeDatas(self._theme)
        self.setMouseTracking(True)
        self._geometries = {}

        # Text editor
        self.editor = MDEditView(self,
                                index=index,
                                spellcheck=settings.spellcheck,
                                highlighting=True,
                                dict=settings.dict)
        self.editor.setFrameStyle(QFrame.NoFrame)
        self.editor.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.editor.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.editor.installEventFilter(self)
        self.editor.setMouseTracking(True)
        self.editor.setVerticalScrollBar(myScrollBar())
        self.scrollBar = self.editor.verticalScrollBar()
        self.scrollBar.setParent(self)

        # Top Panel
        self.topPanel = myPanel(parent=self)
        # self.topPanel.layout().addStretch(1)

        # Spell checking
        if enchant:
            self.btnSpellCheck = QPushButton(self)
            self.btnSpellCheck.setFlat(True)
            self.btnSpellCheck.setIcon(QIcon.fromTheme("tools-check-spelling"))
            self.btnSpellCheck.setCheckable(True)
            self.btnSpellCheck.setChecked(self.editor.spellcheck)
            self.btnSpellCheck.toggled.connect(self.editor.toggleSpellcheck)
        else:
            self.btnSpellCheck = None

        # Navigation Buttons
        self.btnPrevious = QPushButton(self)
        self.btnPrevious.setFlat(True)
        self.btnPrevious.setIcon(QIcon.fromTheme("arrow-left"))
        self.btnPrevious.clicked.connect(self.switchPreviousItem)
        self.btnNext = QPushButton(self)
        self.btnNext.setFlat(True)
        self.btnNext.setIcon(QIcon.fromTheme("arrow-right"))
        self.btnNext.clicked.connect(self.switchNextItem)
        self.btnNew = QPushButton(self)
        self.btnNew.setFlat(True)
        self.btnNew.setIcon(QIcon.fromTheme("document-new"))
        self.btnNew.clicked.connect(self.createNewText)

        # Path and New Text Buttons
        self.wPath = myPath(self)

        # Close
        self.btnClose = QPushButton(self)
        self.btnClose.setIcon(qApp.style().standardIcon(QStyle.SP_DialogCloseButton))
        self.btnClose.clicked.connect(self.close)
        self.btnClose.setFlat(True)

        # Top panel Layout
        if self.btnSpellCheck:
            self.topPanel.layout().addWidget(self.btnSpellCheck)
        self.topPanel.layout().addSpacing(15)
        self.topPanel.layout().addWidget(self.btnPrevious)
        self.topPanel.layout().addWidget(self.btnNext)
        self.topPanel.layout().addWidget(self.btnNew)

        self.topPanel.layout().addStretch(1)
        self.topPanel.layout().addWidget(self.wPath)
        self.topPanel.layout().addStretch(1)

        self.topPanel.layout().addWidget(self.btnClose)
        self.updateTopBar()

        # Left Panel
        self._locked = False
        self.leftPanel = myPanel(vertical=True, parent=self)
        self.locker = locker(self)
        self.locker.lockChanged.connect(self.setLocked)
        self.leftPanel.layout().addWidget(self.locker)

        # Bottom Panel
        self.bottomPanel = myPanel(parent=self)

        self.bottomPanel.layout().addSpacing(24)
        self.lstThemes = QComboBox(self)
        self.lstThemes.setAttribute(Qt.WA_TranslucentBackground)
        paths = allPaths("resources/themes")
        for p in paths:
            lst = [i for i in os.listdir(p) if os.path.splitext(i)[1] == ".theme"]
            for t in lst:
                themeIni = os.path.join(p, t)
                name = loadThemeDatas(themeIni)["Name"]
                # self.lstThemes.addItem(os.path.splitext(t)[0])
                self.lstThemes.addItem(name)
                self.lstThemes.setItemData(self.lstThemes.count()-1, os.path.splitext(t)[0])

        self.lstThemes.setCurrentIndex(self.lstThemes.findData(settings.fullScreenTheme))
        # self.lstThemes.setCurrentText(settings.fullScreenTheme)
        self.lstThemes.currentTextChanged.connect(self.setTheme)
        self.lstThemes.setMaximumSize(QSize(300, QFontMetrics(qApp.font()).height()))
        themeLabel = QLabel(self.tr("Theme:"), self)
        self.bottomPanel.layout().addWidget(themeLabel)
        self.bottomPanel.layout().addWidget(self.lstThemes)
        self.bottomPanel.layout().addStretch(1)

        self.lblProgress = QLabel(self)
        self.lblProgress.setMaximumSize(QSize(200, 14))
        self.lblProgress.setMinimumSize(QSize(100, 14))
        self.lblWC = QLabel(self)
        self.lblClock = myClockLabel(self)
        self.bottomPanel.layout().addWidget(self.lblWC)
        self.bottomPanel.layout().addWidget(self.lblProgress)
        self.bottomPanel.layout().addSpacing(15)
        self.bottomPanel.layout().addWidget(self.lblClock)
        self.updateStatusBar()

        self.bottomPanel.layout().addSpacing(24)

        # Add Widget Settings
        if self.btnSpellCheck:
            self.topPanel.addWidgetSetting(self.tr("Spellcheck"), 'top-spellcheck', (self.btnSpellCheck, ))
        self.topPanel.addWidgetSetting(self.tr("Navigation"), 'top-navigation', (self.btnPrevious, self.btnNext))
        self.topPanel.addWidgetSetting(self.tr("New Text"), 'top-new-doc', (self.btnNew, ))
        self.topPanel.addWidgetSetting(self.tr("Title"), 'top-title', (self.wPath, ))
        self.topPanel.addSetting(self.tr("Title: Show Full Path"), 'title-show-full-path', True)
        self.topPanel.setSettingCallback('title-show-full-path', lambda var, val: self.updateTopBar())
        self.bottomPanel.addWidgetSetting(self.tr("Theme selector"), 'bottom-theme', (self.lstThemes, themeLabel))
        self.bottomPanel.addWidgetSetting(self.tr("Word count"), 'bottom-wc', (self.lblWC, ))
        self.bottomPanel.addWidgetSetting(self.tr("Progress"), 'bottom-progress', (self.lblProgress, ))
        self.bottomPanel.addSetting(self.tr("Progress: Auto Show/Hide"), 'progress-auto-show', True)
        self.bottomPanel.addWidgetSetting(self.tr("Clock"), 'bottom-clock', (self.lblClock, ))
        self.bottomPanel.addSetting(self.tr("Clock: Show Seconds"), 'clock-show-seconds', True)
        self.bottomPanel.setAutoHideVariable('autohide-bottom')
        self.topPanel.setAutoHideVariable('autohide-top')
        self.leftPanel.setAutoHideVariable('autohide-left')

        # Connection
        self._index.model().dataChanged.connect(self.dataChanged)

        # self.updateTheme()
        self.showFullScreen()
        # self.showMaximized()
        # self.show()

    def __del__(self):
        # print("Leaving fullScreenEditor via Destructor event", flush=True)
        self.showNormal()
        self.close()

    def setLocked(self, val):
        self._locked = val
        self.btnClose.setVisible(not val)

    def setTheme(self, themeName):
        themeName = self.lstThemes.currentData()
        settings.fullScreenTheme = themeName
        self._theme = findThemePath(themeName)
        self._themeDatas = loadThemeDatas(self._theme)
        self.updateTheme()

    def updateTheme(self):
        # Reinit stored geometries for hiding widgets
        self._geometries = {}
        rect = self.geometry()
        self._background = generateTheme(self._themeDatas, rect)

        setThemeEditorDatas(self.editor, self._themeDatas, self._background, rect)

        # Colors
        if self._themeDatas["Foreground/Color"] == self._themeDatas["Background/Color"] or \
                        self._themeDatas["Foreground/Opacity"] < 5:
            self._fgcolor = QColor(self._themeDatas["Text/Color"])
            self._bgcolor = QColor(self._themeDatas["Background/Color"])
        else:
            self._bgcolor = QColor(self._themeDatas["Foreground/Color"])
            self._bgcolor.setAlpha(self._themeDatas["Foreground/Opacity"] * 255 / 100)
            self._fgcolor = QColor(self._themeDatas["Text/Color"])
            if self._themeDatas["Text/Color"] == self._themeDatas["Foreground/Color"]:
                self._fgcolor = QColor(self._themeDatas["Background/Color"])

        # ScrollBar
        r = self.editor.geometry()
        w = qApp.style().pixelMetric(QStyle.PM_ScrollBarExtent)
        r.setWidth(w)
        r.moveRight(rect.right() - rect.left())
        self.scrollBar.setGeometry(r)
        # self.scrollBar.setVisible(False)
        self.hideWidget(self.scrollBar)
        p = self.scrollBar.palette()
        b = QBrush(self._background.copy(self.scrollBar.geometry()))
        p.setBrush(QPalette.Base, b)
        self.scrollBar.setPalette(p)

        self.scrollBar.setColor(self._bgcolor)

        # Left Panel
        r = self.locker.geometry()
        r.moveTopLeft(QPoint(
                0,
                self.geometry().height() / 2 - r.height() / 2
        ))
        self.leftPanel.setGeometry(r)
        self.hideWidget(self.leftPanel)
        self.leftPanel.setColor(self._bgcolor)

        # Top / Bottom Panels
        r = QRect(0, 0, 0, 24)
        r.setWidth(rect.width())
        # r.moveLeft(rect.center().x() - r.width() / 2)
        self.topPanel.setGeometry(r)
        # self.topPanel.setVisible(False)
        self.hideWidget(self.topPanel)
        r.moveBottom(rect.bottom() - rect.top())
        self.bottomPanel.setGeometry(r)
        # self.bottomPanel.setVisible(False)
        self.hideWidget(self.bottomPanel)
        self.topPanel.setColor(self._bgcolor)
        self.bottomPanel.setColor(self._bgcolor)

        # Lst theme
        # p = self.lstThemes.palette()
        p = self.palette()
        p.setBrush(QPalette.Button, self._bgcolor)
        p.setBrush(QPalette.ButtonText, self._fgcolor)
        p.setBrush(QPalette.WindowText, self._fgcolor)

        for panel in (self.bottomPanel, self.topPanel, self.leftPanel):
            for i in range(panel.layout().count()):
                item = panel.layout().itemAt(i)
                if item.widget():
                    item.widget().setPalette(p)
        # self.lstThemes.setPalette(p)
        # self.lblWC.setPalette(p)

        self.update()
        self.editor.centerCursor()

    def paintEvent(self, event):
        if self._background:
            painter = QPainter(self)
            painter.setClipRegion(event.region())
            painter.drawPixmap(event.rect(), self._background, event.rect())
            painter.end()

    def resizeEvent(self, event):
        self.updateTheme()

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Escape, Qt.Key_F11] and \
                not self._locked:
            # print("Leaving fullScreenEditor via keyPressEvent", flush=True)
            self.showNormal()
            self.close()
        elif (event.modifiers() & Qt.AltModifier) and \
                event.key() in [Qt.Key_PageUp, Qt.Key_PageDown, Qt.Key_Left, Qt.Key_Right]:
            if event.key() in [Qt.Key_PageUp, Qt.Key_Left]:
                success = self.switchPreviousItem()
            if event.key() in [Qt.Key_PageDown, Qt.Key_Right]:
                success = self.switchNextItem()
            if not success:
                QWidget.keyPressEvent(self, event)
        else:
            QWidget.keyPressEvent(self, event)

    def mouseMoveEvent(self, event):
        r = self.geometry()

        for w in [self.scrollBar, self.topPanel,
                  self.bottomPanel, self.leftPanel]:
            # w.setVisible(w.geometry().contains(event.pos()))
            if self._geometries[w].contains(event.pos()):
                self.showWidget(w)
            else:
                self.hideWidget(w)

    def hideWidget(self, widget):
        if widget not in self._geometries:
            self._geometries[widget] = widget.geometry()

        if hasattr(widget, "_autoHide") and not widget._autoHide:
            return

        # Hides widget in the bottom right corner
        widget.move(self.geometry().bottomRight() + QPoint(1, 1))

    def showWidget(self, widget):
        if widget in self._geometries:
            widget.move(self._geometries[widget].topLeft())

    def eventFilter(self, obj, event):
        if obj == self.editor and event.type() == QEvent.Enter:
            for w in [self.scrollBar, self.topPanel,
                      self.bottomPanel, self.leftPanel]:
                # w.setVisible(False)
                self.hideWidget(w)
        return QWidget.eventFilter(self, obj, event)

    def dataChanged(self, topLeft, bottomRight):
        # This is called sometimes after self has been destroyed. Don't know why.
        if not self or not self._index:
            return
        if topLeft.row() <= self._index.row() <= bottomRight.row():
            self.updateStatusBar()

    def updateTopBar(self):
        item = self._index.internalPointer()
        previousItem = self.previousTextItem(item)
        nextItem = self.nextTextItem(item)
        self.btnPrevious.setEnabled(previousItem is not None)
        self.btnNext.setEnabled(nextItem is not None)
        self.wPath.setItem(item)

    def updateStatusBar(self):
        if self._index:
            item = self._index.internalPointer()

        wc = item.data(Outline.wordCount)
        goal = item.data(Outline.goal)
        pg = item.data(Outline.goalPercentage)

        if goal:
            if settings.fullscreenSettings.get("progress-auto-show", True):
                self.lblProgress.show()
            self.lblWC.setText(self.tr("{} words / {}").format(wc, goal))
        else:
            if settings.fullscreenSettings.get("progress-auto-show", True):
                self.lblProgress.hide()
            self.lblWC.setText(self.tr("{} words").format(wc))
            pg = 0
        rect = self.lblProgress.geometry()
        rect = QRect(QPoint(0, 0), rect.size())
        self.px = QPixmap(rect.size())
        self.px.fill(Qt.transparent)
        p = QPainter(self.px)
        drawProgress(p, rect, pg, 2)
        p.end()
        self.lblProgress.setPixmap(self.px)

        self.locker.setWordCount(wc)
        # If there's a goal, then we update the locker target's number of word accordingly
        # (also if there is a word count, we deduce it.
        if goal and not self.locker.isLocked():
            if wc and goal - wc > 0:
                self.locker.spnWordTarget.setValue(goal - wc)
            elif not wc:
                self.locker.spnWordTarget.setValue(goal)

    def setCurrentModelIndex(self, index):
        self._index = index
        self.editor.setCurrentModelIndex(index)
        self.updateTopBar()
        self.updateStatusBar()

    def switchPreviousItem(self):
        item = self._index.internalPointer()
        previousItem = self.previousTextItem(item)
        if previousItem:
            self.setCurrentModelIndex(previousItem.index())
            return True
        return False

    def switchNextItem(self):
        item = self._index.internalPointer()
        nextItem = self.nextTextItem(item)
        if nextItem:
            self.setCurrentModelIndex(nextItem.index())
            return True
        return False

    def switchToItem(self, item):
        item = self.firstTextItem(item)
        if item:
            self.setCurrentModelIndex(item.index())
        
    def createNewText(self):
        item = self._index.internalPointer()
        newItem = outlineItem(title=qApp.translate("outlineBasics", "New"), _type=settings.defaultTextType)
        self._index.model().insertItem(newItem, item.row() + 1, item.parent().index())
        self.setCurrentModelIndex(newItem.index())

    def previousModelItem(self, item):
        parent = item.parent()
        if not parent:
            # Root has no sibling
            return None

        row = parent.childItems.index(item)
        if row > 0:
            return parent.child(row - 1)
        return self.previousModelItem(parent)

    def nextModelItem(self, item):
        parent = item.parent()
        if not parent:
            # Root has no sibling
            return None

        row = parent.childItems.index(item)
        if row + 1 < parent.childCount():
            return parent.child(row + 1)
        return self.nextModelItem(parent)

    def previousTextItem(self, item):
        previous = self.previousModelItem(item)

        while previous:
            last = self.lastTextItem(previous)
            if last:
                return last
            previous = self.previousModelItem(previous)
        return None
        
    def nextTextItem(self, item):
        if item.isFolder() and item.childCount() > 0:
            next = item.child(0)
        else:
            next = self.nextModelItem(item)

        while next:
            first = self.firstTextItem(next)
            if first:
                return first
            next = self.nextModelItem(next)
        return None

    def firstTextItem(self, item):
        if item.isText():
            return item
        for child in item.children():
            first = self.firstTextItem(child)
            if first:
                return first
        return None

    def lastTextItem(self, item):
        if item.isText():
            return item
        for child in reversed(item.children()):
            last = self.lastTextItem(child)
            if last:
                return last
        return None
        

class myScrollBar(QScrollBar):
    def __init__(self, color=Qt.white, parent=None):
        QScrollBar.__init__(self, parent)
        self._color = color
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)
        self.valueChanged.connect(lambda v: self.timer.start())
        self.valueChanged.connect(lambda: self.parent().showWidget(self))
        self.rangeChanged.connect(self.rangeHasChanged)

    def hide(self):
        self.parent().hideWidget(self)

    def setColor(self, color):
        self._color = color

    def rangeHasChanged(self, min, max):
        """
        Adds viewport height to scrollbar max so that we can center cursor
        on screen.
        """
        if settings.textEditor["alwaysCenter"]:
            self.blockSignals(True)
            self.setMaximum(max + self.parent().height())
            self.blockSignals(False)

    def paintEvent(self, event):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        style = qApp.style()
        painter = QPainter(self)

        # Background (Necessary with Qt 5.2 it seems, not with 5.4)
        # painter.save()
        # painter.setPen(Qt.NoPen)
        # painter.setBrush(self.palette().brush(QPalette.Base))
        # painter.drawRect(event.rect())
        # painter.restore()

        # slider
        r = style.subControlRect(style.CC_ScrollBar, opt, style.SC_ScrollBarSlider)
        painter.fillRect(r, self._color)
        painter.end()


class myPanel(QWidget):
    def __init__(self, color=Qt.white, vertical=False, parent=None):
        QWidget.__init__(self, parent)
        self._color = color
        self.show()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._autoHide = True
        self._m = None
        self._autoHideVar = None
        self._settings = []
        self._callbacks = {}

        if not vertical:
            self.setLayout(QHBoxLayout())
        else:
            self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

    def setColor(self, color):
        self._color = color

    def paintEvent(self, event):
        r = event.rect()
        painter = QPainter(self)
        painter.fillRect(r, self._color)

    def _setConfig(self, config_name, value):
        settings.fullscreenSettings[config_name] = value
        if config_name in self._callbacks:
            self._callbacks[config_name](config_name, value)

    def _setSettingValue(self, setting, value):
        if setting[2]:
            for w in setting[2]:
                w.show() if value else w.hide()
        self._setConfig(setting[1], value)

    def setAutoHide(self, value):
        self._autoHide = value
        if self._autoHideVar:
            self._setConfig(self._autoHideVar, value)

    def setAutoHideVariable(self, name):
        if name:
            self.setAutoHide(settings.fullscreenSettings[name])
        self._autoHideVar = name

    def addWidgetSetting(self, label, config_name, widgets):
        setting = (label, config_name, widgets)
        self._settings.append(setting)
        if settings.fullscreenSettings.get(config_name, None) is not None:
            self._setSettingValue(setting, settings.fullscreenSettings[config_name])

    def addSetting(self, label, config_name, default=True):
        if settings.fullscreenSettings.get(config_name, None) is None:
            self._setConfig(config_name, default)
        self.addWidgetSetting(label, config_name, None)

    def setSettingCallback(self, config_name, callback):
        self._callbacks[config_name] = callback

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            if self._m:
                self._m.deleteLater()
            m = QMenu()
            a = QAction(self.tr("Auto-hide"), m)
            a.setCheckable(True)
            a.setChecked(self._autoHide)
            a.toggled.connect(self.setAutoHide)
            m.addAction(a)
            for item in self._settings:
                a = QAction(item[0], m)
                a.setCheckable(True)
                if item[2]:
                    a.setChecked(item[2][0].isVisible())
                else:
                    a.setChecked(settings.fullscreenSettings[item[1]])
                def gen_cb(setting):
                    return lambda v: self._setSettingValue(setting, v)
                a.toggled.connect(gen_cb(item))
                m.addAction(a)
            m.popup(self.mapToGlobal(event.pos()))
            self._m = m

class myPath(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.editor = parent
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

    def setItem(self, item):
        self._item = item
        path = self.getItemPath(item)
        layout = self.layout()
        while layout.count() > 0:
            li = layout.takeAt(0)
            w = li.widget()
            w.deleteLater()

        def gen_cb(i):
            return lambda: self.popupPath(i)
        # Skip Root
        for i in path[1:]:
            if not settings.fullscreenSettings.get("title-show-full-path", True) and \
                    i.isFolder():
                continue
            btn = QPushButton(i.title(), self)
            btn.setFlat(True)
            btn.clicked.connect(gen_cb(i))
            self.layout().addWidget(btn)
            if i.isFolder():
                lblSeparator = QLabel(" > ", self)
                #lblSeparator = QLabel(self)
                #lblSeparator.setPixmap(QIcon.fromTheme("view-list-tree").pixmap(24,24))
                self.layout().addWidget(lblSeparator)

    def popupPath(self, item):
        m = QMenu()
        def gen_cb(i):
            return lambda: self.editor.switchToItem(i)

        for i in item.siblings():
            a = QAction(i.title(), m)
            if i == item:
                a.setIcon(QIcon.fromTheme("stock_yes"))
                a.setEnabled(False)
            elif self.editor.firstTextItem(i) is None:
                a.setEnabled(False)
            else:
                a.triggered.connect(gen_cb(i))
            m.addAction(a)
        m.popup(QCursor.pos())
        self._m = m

    def getItemPath(self, item):
        path = [item]
        parent = item.parent()
        while parent:
            path.insert(0, parent)
            parent = parent.parent()
        return path
        

class myClockLabel(QLabel):
    

    def __init__(self, parent=None):
        QLabel.__init__(self, parent)
        
        self.updateClock()
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.updateClock)
        self.timer.start()


    def updateClock(self):
        time = QTime.currentTime()
        if settings.fullscreenSettings.get("clock-show-seconds", True):
            timeStr = time.toString("hh:mm:ss")
        else:
            timeStr = time.toString("hh:mm")

        self.setText(timeStr)
