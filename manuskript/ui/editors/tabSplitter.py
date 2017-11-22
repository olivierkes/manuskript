#!/usr/bin/env python
# --!-- coding: utf8 --!--
import locale

from PyQt5.QtCore import QModelIndex, QRect, QPoint, Qt, QObject, QSize
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtWidgets import QWidget, QPushButton, qApp

from manuskript.functions import mainWindow, appPath
from manuskript.ui import style
from manuskript.ui.editors.tabSplitter_ui import Ui_tabSplitter


class tabSplitter(QWidget, Ui_tabSplitter):
    """
    `tabSplitter` is used to have mutliple `outlineItem`s open, either in tabs
    and/or in splitted views. Each tab contains an `editorWidget` which is responsible
    for showing one single `outlineItem` in several ways.

    `tabSplitter` is managed mainly through the `mainEditor` which is responsible
    for opening indexes and such.

    `tabSplitter` main widget is a `QSplitter` named `self.splitter`. It contains one
    `QTabWidget` called `self.tab`. A second `tabSplitter` can be loaded through
    `self.split` in `self.splitter`. That way, a single `tabSplitter` can split
    indefinitely.

    `tabSplitter` also has two buttons:

     1. `self.btnSplit`: used to split and unsplit
     2. `self.btnTarget`: toggles whether `self.tab` is a target to open any
        selected outlineItem in any other views.
    """

    def __init__(self, parent=None, mainEditor=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        # try:
        #     self.tab.setTabBarAutoHide(True)
        # except AttributeError:
        #     print("Info: install Qt 5.4 or higher to use tabbar auto-hide in editor.")

        # Button to split
        self.btnSplit = QPushButton(self)
        self.btnSplit.setGeometry(QRect(0, 0, 24, 24))
        self.btnSplit.setMinimumSize(QSize(24, 24))
        self.btnSplit.setMaximumSize(QSize(24, 24))
        # self.btnSplit.setCheckable(True)
        self.btnSplit.setFlat(True)
        self.btnSplit.setObjectName("btnSplit")
        self.btnSplit.installEventFilter(self)
        self.btnSplit.clicked.connect(self.split)

        # Button to set target
        self.isTarget = False
        self.btnTarget = QPushButton(QIcon.fromTheme("set-target"), "", self)
        self.btnTarget.setGeometry(QRect(25, 0, 24, 24))
        self.btnTarget.setMinimumSize(QSize(24, 24))
        self.btnTarget.setMaximumSize(QSize(24, 24))
        # self.btnTarget.setCheckable(True)
        self.btnTarget.setFlat(True)
        self.btnTarget.setObjectName("btnTarget")
        self.btnTarget.clicked.connect(self.setTarget)
        self.btnTarget.setToolTip(self.tr("Open selected items in that view."))
        self.updateTargetIcon(self.isTarget)

        self.mainEditor = mainEditor or parent

        self.secondTab = None
        self.splitState = 0
        self.focusTab = 1
        self.closeSplit()

        self.updateStyleSheet()

        self.tab.tabCloseRequested.connect(self.closeTab)
        self.tab.currentChanged.connect(self.mainEditor.tabChanged)
        qApp.focusChanged.connect(self.focusChanged)

    def updateStyleSheet(self):
        self.setStyleSheet(style.mainEditorTabSS())
        if self.secondTab:
            self.secondTab.updateStyleSheet()

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
            if openIndexes[1]:
                self.split(state=openIndexes[0])

            for i in openIndexes[1]:
                idx = mainWindow().mdlOutline.getIndexByID(i)
                self.mainEditor.setCurrentModelIndex(idx, newTab=True)

            if openIndexes[2]:
                self.focusTab = 2
                self.secondTab.restoreOpenIndexes(openIndexes[2])

        except:
            # Cannot load open indexes. Let's simply open root.
            self.mainEditor.setCurrentModelIndex(QModelIndex(), newTab=True)

    ###############################################################################
    # TARGET
    ###############################################################################

    def setTarget(self):
        self.isTarget = not self.isTarget
        self.updateTargetIcon(self.isTarget)

    def updateTargetIcon(self, val):
        icon = QIcon.fromTheme("set-target", QIcon(appPath("icons/NumixMsk/256x256/actions/set-target.svg")))
        if not val:
            icon = QIcon(icon.pixmap(128, 128, icon.Disabled))
        self.btnTarget.setIcon(icon)

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
        self.secondTab.splitter.setObjectName(self.splitter.objectName() + "_")

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

        if len(l):
            self.mainEditor.tabChanged()

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
            # self.setAutoFillBackground(True)
            # self.setBackgroundRole(QPalette.Highlight)

            # self.splitter.setAutoFillBackground(True)
            # self.splitter.setStyleSheet("""QSplitter#{}{{
            #     border:1px solid darkblue;
            #     }}""".format(self.splitter.objectName()))

            self.setStyleSheet(style.mainEditorTabSS() + """
                QSplitter#{name},
                QSplitter#{name} > QWidget > QSplitter{{
                    border:3px solid {color};
                }}""".format(
                    name=self.splitter.objectName(),
                    color=style.highlight))
        elif object == self.btnSplit and event.type() == event.HoverLeave:
            # self.setAutoFillBackground(False)
            # self.setBackgroundRole(QPalette.Window)

            # self.splitter.setStyleSheet("""QSplitter#{}{{
            #     border: 1px solid transparent;
            #     }}""".format(self.splitter.objectName()))

            self.setStyleSheet(style.mainEditorTabSS())
        return QWidget.eventFilter(self, object, event)
