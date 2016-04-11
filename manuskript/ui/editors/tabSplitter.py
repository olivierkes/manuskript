#!/usr/bin/env python
# --!-- coding: utf8 --!--
import locale

from PyQt5.QtCore import QModelIndex, QRect, QPoint, Qt, QObject, QSize
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtWidgets import QWidget, QPushButton, qApp

from manuskript.functions import mainWindow
from manuskript.ui import style
from manuskript.ui.editors.tabSplitter_ui import Ui_tabSplitter


class tabSplitter(QWidget, Ui_tabSplitter):
    def __init__(self, parent=None, mainEditor=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.setStyleSheet(style.mainEditorTabSS())

        try:
            self.tab.setTabBarAutoHide(True)
        except AttributeError:
            print("Info: install Qt 5.4 or higher to use tabbar auto-hide in editor.")

        #Remove empty widget
        # self.splitter.widget(1).setParent(None)

        self.btnSplit = QPushButton(self)
        self.btnSplit.setGeometry(QRect(0, 0, 24, 24))
        self.btnSplit.setMinimumSize(QSize(24, 24))
        self.btnSplit.setMaximumSize(QSize(24, 24))
        # self.btnSplit.setCheckable(True)
        self.btnSplit.setFlat(True)
        self.btnSplit.setObjectName("btnSplit")
        self.btnSplit.installEventFilter(self)

        self.mainEditor = mainEditor or parent

        self.btnSplit.clicked.connect(self.split)
        self.secondTab = None
        self.splitState = 0
        self.focusTab = 1
        self.closeSplit()

        self.tab.tabCloseRequested.connect(self.closeTab)
        self.tab.currentChanged.connect(self.mainEditor.tabChanged)

        qApp.focusChanged.connect(self.focusChanged)

    ###############################################################################
    # TABS
    ###############################################################################

    def closeTab(self, index):
        w = self.tab.widget(index)
        self.tab.removeTab(index)
        w.setCurrentModelIndex(QModelIndex())
        w.deleteLater()

    def tabOpenIndexes(self):
        sel = []
        for i in range(self.tab.count()):
            sel.append(mainWindow().mdlOutline.ID(self.tab.widget(i).currentIndex))
        return sel

    def openIndexes(self):
        r = [
            self.splitState,
            self.tabOpenIndexes(),
            self.secondTab.openIndexes() if self.secondTab else None,
        ]
        return r

    def restoreOpenIndexes(self, openIndexes):

        try:

            self.split(state=openIndexes[0])

            for i in openIndexes[1]:
                idx = mainWindow().mdlOutline.getIndexByID(i)
                self.mainEditor.setCurrentModelIndex(idx, newTab=True)

            if openIndexes[2]:
                self.focusTab = 2
                self.secondTab.restoreOpenIndexes(openIndexes[2])

        except:

            print("Failed to load indexes from settings...")
            print("Indexes:", openIndexes)

    ###############################################################################
    # SPLITTER
    ###############################################################################

    def split(self, toggled=None, state=None):

        if state is None and self.splitState == 0 or state == 1:
            if self.secondTab is None:
                self.addSecondTab()

            self.splitState = 1
            self.splitter.setOrientation(Qt.Horizontal)
            # self.btnSplit.setChecked(True)
            self.btnSplit.setIcon(QIcon.fromTheme("split-vertical"))
            self.btnSplit.setToolTip(self.tr("Split horizontally"))

        elif state is None and self.splitState == 1 or state == 2:
            if self.secondTab is None:
                self.addSecondTab()

            self.splitter.setOrientation(Qt.Vertical)
            self.splitState = 2
            # self.btnSplit.setChecked(True)
            self.btnSplit.setIcon(QIcon.fromTheme("split-horizontal"))
            self.btnSplit.setToolTip(self.tr("Close split"))

        else:
            self.closeSplit()

    def addSecondTab(self):
        self.secondTab = tabSplitter(mainEditor=self.mainEditor)
        self.secondTab.setObjectName(self.objectName() + "_")
        self.splitter.addWidget(self.secondTab)
        self.splitter.setStretchFactor(0, 10)
        self.splitter.setStretchFactor(1, 10)

        if self.mainEditor.currentEditor():
            idx = self.mainEditor.currentEditor().currentIndex
            self.focusTab = 2
            self.mainEditor.setCurrentModelIndex(idx)

    def closeSplit(self):
        st = self.secondTab
        l = []
        while st:
            l.append(st)
            st = st.secondTab

        for st in reversed(l):
            st.setParent(None)
            qApp.focusChanged.disconnect(st.focusChanged)
            st.deleteLater()

        self.focusTab = 1
        self.secondTab = None
        # self.btnSplit.setChecked(False)
        self.splitState = 0
        self.btnSplit.setIcon(QIcon.fromTheme("split-close"))
        self.btnSplit.setToolTip(self.tr("Split vertically"))

    # def resizeEvent(self, event):
    #     r = self.geometry()
    #     r.moveLeft(0)
    #     r.moveTop(0)
    #     self.splitter.setGeometry(r)
    #     self.btnSplit.setGeometry(QRect(0, 0, 24, 24))

    def focusChanged(self, old, new):
        if self.secondTab is None or new is None:
            return

        oldFT = self.focusTab
        while new:
            if new == self.tab:
                self.focusTab = 1
                new = None
            elif new == self.secondTab:
                self.focusTab = 2
                new = None
            else:
                new = new.parent()

        if self.focusTab != oldFT:
            self.mainEditor.tabChanged()

    def eventFilter(self, object, event):
        if object == self.btnSplit and event.type() == event.HoverEnter:
            self.setAutoFillBackground(True)
            self.setBackgroundRole(QPalette.Midlight)
        elif object == self.btnSplit and event.type() == event.HoverLeave:
            self.setAutoFillBackground(False)
            self.setBackgroundRole(QPalette.Window)
        return QWidget.eventFilter(self, object, event)