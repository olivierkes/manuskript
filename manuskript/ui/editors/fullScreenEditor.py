#!/usr/bin/env python
# --!-- coding: utf8 --!--
import os

from PyQt5.QtCore import Qt, QSize, QPoint, QRect, QEvent, QTimer
from PyQt5.QtGui import QFontMetrics, QColor, QBrush, QPalette, QPainter, QPixmap
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QWidget, QPushButton, qApp, QStyle, QComboBox, QLabel, QScrollBar, \
    QStyleOptionSlider, QHBoxLayout, QVBoxLayout, QMenu, QAction

# Spell checker support
from manuskript import settings
from manuskript.enums import Outline
from manuskript.functions import allPaths, drawProgress
from manuskript.ui.editors.locker import locker
from manuskript.ui.editors.textFormat import textFormat
from manuskript.ui.editors.themes import findThemePath, generateTheme, setThemeEditorDatas
from manuskript.ui.editors.themes import loadThemeDatas
from manuskript.ui.views.textEditView import textEditView

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
        self.editor = textEditView(self,
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
            self.topPanel.layout().addWidget(self.btnSpellCheck)

        self.topPanel.layout().addStretch(1)

        # Formatting
        self.textFormat = textFormat(self)
        self.topPanel.layout().addWidget(self.textFormat)
        self.topPanel.layout().addStretch(1)

        self.btnClose = QPushButton(self)
        self.btnClose.setIcon(qApp.style().standardIcon(QStyle.SP_DialogCloseButton))
        self.btnClose.clicked.connect(self.close)
        self.btnClose.setFlat(True)
        self.topPanel.layout().addWidget(self.btnClose)

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
        self.bottomPanel.layout().addWidget(QLabel(self.tr("Theme:"), self))
        self.bottomPanel.layout().addWidget(self.lstThemes)
        self.bottomPanel.layout().addStretch(1)

        self.lblProgress = QLabel(self)
        self.lblProgress.setMaximumSize(QSize(200, 14))
        self.lblProgress.setMinimumSize(QSize(100, 14))
        self.lblWC = QLabel(self)
        self.bottomPanel.layout().addWidget(self.lblWC)
        self.bottomPanel.layout().addWidget(self.lblProgress)
        self.updateStatusBar()

        self.bottomPanel.layout().addSpacing(24)

        # Connection
        self._index.model().dataChanged.connect(self.dataChanged)

        # self.updateTheme()
        self.showFullScreen()
        # self.showMaximized()
        # self.show()

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
            self._bgcolor = QColor(self._themeDatas["Text/Color"])
            self._fgcolor = QColor(self._themeDatas["Background/Color"])
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

        for panel in (self.bottomPanel, self.topPanel):
            for i in range(panel.layout().count()):
                item = panel.layout().itemAt(i)
                if item.widget():
                    item.widget().setPalette(p)
        # self.lstThemes.setPalette(p)
        # self.lblWC.setPalette(p)

        self.update()

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
            self.close()
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

        # Hides wiget in the bottom right corner
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

    def updateStatusBar(self):
        if self._index:
            item = self._index.internalPointer()

        wc = item.data(Outline.wordCount.value)
        goal = item.data(Outline.goal.value)
        pg = item.data(Outline.goalPercentage.value)

        if goal:
            rect = self.lblProgress.geometry()
            rect = QRect(QPoint(0, 0), rect.size())
            self.px = QPixmap(rect.size())
            self.px.fill(Qt.transparent)
            p = QPainter(self.px)
            drawProgress(p, rect, pg, 2)
            p.end()
            self.lblProgress.setPixmap(self.px)
            self.lblWC.setText(self.tr("{} words / {}").format(wc, goal))
        else:
            self.lblProgress.hide()
            self.lblWC.setText(self.tr("{} words").format(wc))

        self.locker.setWordCount(wc)
        # If there's a goal, then we update the locker target's number of word accordingly
        # (also if there is a word count, we deduce it.
        if goal and not self.locker.isLocked():
            if wc and goal - wc > 0:
                self.locker.spnWordTarget.setValue(goal - wc)
            elif not wc:
                self.locker.spnWordTarget.setValue(goal)


class myScrollBar(QScrollBar):
    def __init__(self, color=Qt.white, parent=None):
        QScrollBar.__init__(self, parent)
        self._color = color
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(lambda: self.parent().hideWidget(self))
        self.valueChanged.connect(lambda v: self.timer.start())
        self.valueChanged.connect(lambda: self.parent().showWidget(self))

    def setColor(self, color):
        self._color = color

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

    def setAutoHide(self, value):
        self._autoHide = value

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            m = QMenu()
            a = QAction(self.tr("Auto-hide"), m)
            a.setCheckable(True)
            a.setChecked(self._autoHide)
            a.toggled.connect(self.setAutoHide)
            m.addAction(a)
            m.popup(self.mapToGlobal(event.pos()))
            self._m = m
