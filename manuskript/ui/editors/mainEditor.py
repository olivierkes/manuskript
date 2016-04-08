#!/usr/bin/env python
# --!-- coding: utf8 --!--
import locale

from PyQt5.QtCore import QModelIndex, QRect, QPoint
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import qApp

from manuskript import settings
from manuskript.enums import Outline
from manuskript.functions import AUC, mainWindow, drawProgress
from manuskript.ui.editors.editorWidget import editorWidget
from manuskript.ui.editors.fullScreenEditor import fullScreenEditor
from manuskript.ui.editors.mainEditor_ui import Ui_mainEditor

locale.setlocale(locale.LC_ALL, '')


class mainEditor(QWidget, Ui_mainEditor):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self._updating = False

        self.mw = mainWindow()
        self.tab.tabCloseRequested.connect(self.closeTab)
        self.tab.currentChanged.connect(self.tabChanged)

        # UI
        try:
            self.tab.setTabBarAutoHide(True)
        except AttributeError:
            print("Info: install Qt 5.4 or higher to use tabbar auto-hide in editor.")

        # Connections --------------------------------------------------------

        self.sldCorkSizeFactor.valueChanged.connect(
                self.setCorkSizeFactor, AUC)
        self.btnRedacFolderCork.toggled.connect(
                self.sldCorkSizeFactor.setVisible, AUC)
        self.btnRedacFolderText.clicked.connect(
                lambda v: self.setFolderView("text"), AUC)
        self.btnRedacFolderCork.clicked.connect(
                lambda v: self.setFolderView("cork"), AUC)
        self.btnRedacFolderOutline.clicked.connect(
                lambda v: self.setFolderView("outline"), AUC)

        self.btnRedacFullscreen.clicked.connect(
                self.showFullScreen, AUC)

        # FIXME: can we do something that looks good?
        #        How to remove the line under the tabs?
        # self.setStyleSheet("""
        #     QTabWidget::tab-bar{
        #         border:none;
        #     }
        #     QTabBar::tab{
        #         padding: 2px 10px;
        #         margin: 2px;
        #         border-top: none;
        #         border-radius: 1px;
        #         background: transparent;
        #     }
        #
        #     QTabBar::tab:selected{
        #         border-top: 3px solid orange;
        #         border-radius: 3px;
        #     }
        #     QTabBar::tab:hover{
        #         background: darkgray;
        #     }
        #     """)

    ###############################################################################
    # TABS
    ###############################################################################

    def currentEditor(self):
        return self.tab.currentWidget()

    def tabChanged(self, index):
        if self.currentEditor():
            index = self.currentEditor().currentIndex
            view = self.currentEditor().folderView
            self.updateFolderViewButtons(view)
            if index.isValid():
                hidden = not index.internalPointer().isFolder()
            else:
                hidden = False
        else:
            index = QModelIndex()
            hidden = False

        self._updating = True
        self.mw.treeRedacOutline.setCurrentIndex(index)
        self._updating = False

        self.updateStats()
        self.updateThingsVisible(index)

    def closeTab(self, index):
        w = self.tab.widget(index)
        self.tab.removeTab(index)
        w.setCurrentModelIndex(QModelIndex())
        w.deleteLater()

    def closeAllTabs(self):
        while(self.tab.count()):
            self.closeTab(0)

    def allTabs(self):
        return [self.tab.widget(i) for i in range(self.tab.count())]

    ###############################################################################
    # SELECTION AND UPDATES
    ###############################################################################

    def selectionChanged(self):
        if self._updating:
            return

        if len(self.mw.treeRedacOutline.selectionModel().
               selection().indexes()) == 0:
            idx = QModelIndex()
        else:
            idx = self.mw.treeRedacOutline.currentIndex()

        self.setCurrentModelIndex(idx)

        self.updateThingsVisible(idx)

    def openIndexes(self, indexes, newTab=False):
        for i in indexes:
            self.setCurrentModelIndex(i, newTab)

    def setCurrentModelIndex(self, index, newTab=False):

        if not index.isValid():
            title = self.tr("Root")
        else:
            title = index.internalPointer().title()

        # Checking if tab is already openned
        for w in self.allTabs():
            if w.currentIndex == index:
                self.tab.setCurrentWidget(w)
                return

        if qApp.keyboardModifiers() & Qt.ControlModifier:
            newTab = True

        if newTab or not self.tab.count():
            editor = editorWidget(self)
            editor.setCurrentModelIndex(index)
            self.tab.addTab(editor, title)
            self.tab.setCurrentIndex(self.tab.count() - 1)
        else:
            self.currentEditor().setCurrentModelIndex(index)
            self.tab.setTabText(self.tab.currentIndex(), title)

    ###############################################################################
    # UI
    ###############################################################################

    def updateThingsVisible(self, index):
        if index.isValid():
            visible = index.internalPointer().isFolder()
        else:
            visible = True

        # Hides / show textFormat
        self.textFormat.updateFromIndex(index)

        self.btnRedacFolderText.setVisible(visible)
        self.btnRedacFolderCork.setVisible(visible)
        self.btnRedacFolderOutline.setVisible(visible)
        self.sldCorkSizeFactor.setVisible(visible)
        self.btnRedacFullscreen.setVisible(not visible)

    def updateFolderViewButtons(self, view):
        if view == "text":
            self.btnRedacFolderText.setChecked(True)
        elif view == "cork":
            self.btnRedacFolderCork.setChecked(True)
        elif view == "outline":
            self.btnRedacFolderOutline.setChecked(True)

    def updateStats(self):

        if not self.currentEditor():
            return

        index = self.currentEditor().currentIndex
        if index.isValid():
            item = index.internalPointer()
        else:
            item = self.mw.mdlOutline.rootItem

        if not item:
            item = self.mw.mdlOutline.rootItem

        wc = item.data(Outline.wordCount.value)
        goal = item.data(Outline.goal.value)
        progress = item.data(Outline.goalPercentage.value)
        # mw = qApp.activeWindow()

        if not wc:
            wc = 0
        if goal:
            self.lblRedacProgress.show()
            rect = self.lblRedacProgress.geometry()
            rect = QRect(QPoint(0, 0), rect.size())
            self.px = QPixmap(rect.size())
            self.px.fill(Qt.transparent)
            p = QPainter(self.px)
            drawProgress(p, rect, progress, 2)
            del p
            self.lblRedacProgress.setPixmap(self.px)
            self.lblRedacWC.setText(self.tr("{} words / {}").format(
                    locale.format("%d", wc, grouping=True),
                    locale.format("%d", goal, grouping=True)))
        else:
            self.lblRedacProgress.hide()
            self.lblRedacWC.setText(self.tr("{} words").format(
                    locale.format("%d", wc, grouping=True)))

    ###############################################################################
    # VIEWS
    ###############################################################################

    def setFolderView(self, view):
        if self.currentEditor():
            self.currentEditor().setFolderView(view)

    def setCorkSizeFactor(self, val):
        for w in self.allTabs():
            w.setCorkSizeFactor(val)
        settings.corkSizeFactor = val

    def updateCorkView(self):
        for w in self.allTabs():
            w.corkView.viewport().update()

    def updateCorkBackground(self):
        for w in self.allTabs():
            w.corkView.updateBackground()

    def updateTreeView(self):
        for w in self.allTabs():
            w.outlineView.viewport().update()

    def showFullScreen(self):
        if self.currentEditor():
            self._fullScreen = fullScreenEditor(self.currentEditor().currentIndex)

    ###############################################################################
    # DICT AND STUFF LIKE THAT
    ###############################################################################

    def setDict(self, dict):
        print(dict)
        for w in self.allTabs():
            w.setDict(dict)

    def toggleSpellcheck(self, val):
        for w in self.allTabs():
            w.toggleSpellcheck(val)
