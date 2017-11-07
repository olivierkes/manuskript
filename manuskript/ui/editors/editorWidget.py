#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import pyqtSignal, QModelIndex
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QWidget, QFrame, QSpacerItem, QSizePolicy, QVBoxLayout

from manuskript import settings
from manuskript.functions import AUC, mainWindow
from manuskript.ui.editors.editorWidget_ui import Ui_editorWidget_ui
from manuskript.ui.views.textEditView import textEditView


class editorWidget(QWidget, Ui_editorWidget_ui):
    """
    `editorWidget` is a class responsible for displaying and editing one
    `outlineItem`. This item can be a folder or a text.

    It has four views (see `self.setView`)

      - For folders: "text", "outline" or "cork" (set in `self.folderView`)

        Text: displays a list of `textEditView` in a scroll area

        Outline: displays an outline, using an `outlineView`

        Cork: displays flash cards, using a `corkView`

      - For text: item is simply displayed in a `textEditView`

    All those views are contained in `editorWidget` single widget: `self.stack`.

    `editorWidget` are managed in `tabSplitted` (that allow to open several
    `outlineItem`s, either in Tabs or in split views.

    `tabSplitted` are in turn managed by the `mainEditor`, which is unique and
    gives UI buttons to manage all those views.
    """

    toggledSpellcheck = pyqtSignal(bool)
    dictChanged = pyqtSignal(str)

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.currentIndex = QModelIndex()
        self.currentID = None
        self.txtEdits = []
        self.scroll.setBackgroundRole(QPalette.Base)
        self.toggledSpellcheck.connect(self.txtRedacText.toggleSpellcheck, AUC)
        self.dictChanged.connect(self.txtRedacText.setDict, AUC)
        self.txtRedacText.setHighlighting(True)
        self.currentDict = ""
        self.spellcheck = True
        self.folderView = "cork"
        self.mw = mainWindow()
        self._tabWidget = None  # set by mainEditor on creation

        self._model = None

        # def setModel(self, model):
        # self._model = model
        # self.setView()

    def setFolderView(self, v):
        oldV = self.folderView
        if v == "cork":
            self.folderView = "cork"
        elif v == "outline":
            self.folderView = "outline"
        else:
            self.folderView = "text"

        # Saving value
        settings.folderView = self.folderView

        if oldV != self.folderView and self.currentIndex:
            self.setCurrentModelIndex(self.currentIndex)

    def setCorkSizeFactor(self, v):
        self.corkView.itemDelegate().setCorkSizeFactor(v)
        self.redrawCorkItems()

    def redrawCorkItems(self):
        r = self.corkView.rootIndex()

        if r.isValid():
            count = r.internalPointer().childCount()
        elif self._model:
            count = self._model.rootItem.childCount()
        else:
            count = 0

        for c in range(count):
            self.corkView.itemDelegate().sizeHintChanged.emit(r.child(c, 0))

    def updateTabTitle(self):
        """
        `editorWidget` belongs to a `QTabWidget` in a `tabSplitter`. We update
        the tab title to reflect that of current item.
        """
        # `self._tabWidget` is set by mainEditor when creating tab and `editorWidget`.
        # if `editorWidget` is ever used out of `mainEditor`, this could throw
        # an error.
        if not self._tabWidget:
            return

        if self.currentIndex.isValid():
            item = self.currentIndex.internalPointer()
        elif self._model:
            item = self._model.rootItem
        else:
            return

        i = self._tabWidget.indexOf(self)
        self._tabWidget.setTabText(i, item.title())

    def setView(self):
        # index = mainWindow().treeRedacOutline.currentIndex()

        # Couting the number of other selected items
        # sel = []
        # for i in mainWindow().treeRedacOutline.selectionModel().selection().indexes():
        # if i.column() != 0: continue
        # if i not in sel: sel.append(i)

        # if len(sel) != 0:
        # item = index.internalPointer()
        # else:
        # index = QModelIndex()
        # item = self.mw.mdlOutline.rootItem

        # self.currentIndex = index

        if self.currentIndex.isValid():
            item = self.currentIndex.internalPointer()
        else:
            item = self.mw.mdlOutline.rootItem

        self.updateTabTitle()

        def addTitle(itm):
            edt = textEditView(self, html="<h{l}>{t}</h{l}>".format(l=min(itm.level() + 1, 5), t=itm.title()),
                               autoResize=True)
            edt.setFrameShape(QFrame.NoFrame)
            self.txtEdits.append(edt)
            l.addWidget(edt)

        def addLine():
            line = QFrame(self.text)
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            l.addWidget(line)

        def addText(itm):
            edt = textEditView(self,
                               index=itm.index(),
                               spellcheck=self.spellcheck,
                               dict=settings.dict,
                               highlighting=True,
                               autoResize=True)
            edt.setFrameShape(QFrame.NoFrame)
            edt.setStatusTip("{}".format(itm.path()))
            self.toggledSpellcheck.connect(edt.toggleSpellcheck, AUC)
            self.dictChanged.connect(edt.setDict, AUC)
            # edt.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            self.txtEdits.append(edt)
            l.addWidget(edt)

        def addChildren(itm):
            for c in range(itm.childCount()):
                child = itm.child(c)

                if child.isFolder():
                    addTitle(child)
                    addChildren(child)

                else:
                    addText(child)
                    addLine()

        def addSpacer():
            l.addItem(QSpacerItem(10, 1000, QSizePolicy.Minimum, QSizePolicy.Expanding))

            # Display multiple selected items
            # if len(sel) > 1 and False:  # Buggy and not very useful, skip
            # self.stack.setCurrentIndex(1)
            # w = QWidget()
            # l = QVBoxLayout(w)
            # self.txtEdits = []
            # for idx in sel:
            # sItem = idx.internalPointer()
            # addTitle(sItem)
            # if sItem.isFolder():
            # addChildren(sItem)
            # else:
            # addText(sItem)
            # addLine()
            # addSpacer()
            # self.scroll.setWidget(w)

        if item and item.isFolder() and self.folderView == "text":
            self.stack.setCurrentIndex(1)
            w = QWidget()
            w.setObjectName("editorWidgetFolderText")
            l = QVBoxLayout(w)
            w.setStyleSheet("background: {};".format(settings.textEditor["background"]))
            # self.scroll.setWidgetResizable(False)

            self.txtEdits = []

            if item != self._model.rootItem:
                addTitle(item)

            addChildren(item)
            addSpacer()
            self.scroll.setWidget(w)

        elif item and item.isFolder() and self.folderView == "cork":
            self.stack.setCurrentIndex(2)
            self.corkView.setModel(self._model)
            self.corkView.setRootIndex(self.currentIndex)
            try:
                self.corkView.selectionModel().selectionChanged.connect(mainWindow().redacMetadata.selectionChanged, AUC)
                self.corkView.clicked.connect(mainWindow().redacMetadata.selectionChanged, AUC)
                self.corkView.clicked.connect(mainWindow().mainEditor.updateTargets, AUC)
            except TypeError:
                pass

        elif item and item.isFolder() and self.folderView == "outline":
            self.stack.setCurrentIndex(3)
            self.outlineView.setModelCharacters(mainWindow().mdlCharacter)
            self.outlineView.setModelLabels(mainWindow().mdlLabels)
            self.outlineView.setModelStatus(mainWindow().mdlStatus)
            self.outlineView.setModel(self._model)
            self.outlineView.setRootIndex(self.currentIndex)

            try:
                self.outlineView.selectionModel().selectionChanged.connect(mainWindow().redacMetadata.selectionChanged, AUC)
                self.outlineView.clicked.connect(mainWindow().redacMetadata.selectionChanged, AUC)
                self.outlineView.clicked.connect(mainWindow().mainEditor.updateTargets, AUC)
            except TypeError:
                pass

        if item and item.isText():
            self.txtRedacText.setCurrentModelIndex(self.currentIndex)
            self.stack.setCurrentIndex(0)  # Single text item
        else:
            self.txtRedacText.setCurrentModelIndex(QModelIndex())

        try:
            self._model.dataChanged.connect(self.modelDataChanged, AUC)
            self._model.rowsInserted.connect(self.updateIndexFromID, AUC)
            self._model.rowsRemoved.connect(self.updateIndexFromID, AUC)
            #self.mw.mdlOutline.rowsAboutToBeRemoved.connect(self.rowsAboutToBeRemoved, AUC)
        except TypeError:
            pass

        self.updateStatusBar()

    def setCurrentModelIndex(self, index=None):
        if index.isValid():
            self.currentIndex = index
            self._model = index.model()
            self.currentID = self._model.ID(index)
        else:
            self.currentIndex = QModelIndex()
            self.currentID = None

        self.setView()

    def updateIndexFromID(self):
        """
        Index might have changed (through drag an drop), so we keep current
        item's ID and update index. Item might have been deleted too.
        """
        idx = self._model.getIndexByID(self.currentID)

        # If we have an ID but the ID does not exist, it has been deleted
        if self.currentID and idx == QModelIndex():
            # Item has been deleted, we open the parent instead
            self.setCurrentModelIndex(self.currentIndex.parent())
            # FIXME: selection in self.mw.treeRedacOutline is not updated
            #        but we cannot simply setCurrentIndex through treeRedacOutline
            #        because this might be a tab in the background / out of focus
            #        Also the UI of mainEditor is not updated (so the folder icons
            #        are not display, button "up" doesn't work, etc.).

        # Item has been moved
        elif idx != self.currentIndex:
            # We update the index
            self.currentIndex = idx
            self.setView()

    def modelDataChanged(self, topLeft, bottomRight):
        # if self.currentID:
        # self.updateIndexFromID()
        if not self.currentIndex:
            return
        if topLeft.row() <= self.currentIndex.row() <= bottomRight.row():
            self.updateStatusBar()

    #def rowsAboutToBeRemoved(self, parent, first, last):
        #if self.currentIndex:
            #if self.currentIndex.parent() == parent and \
                                    #first <= self.currentIndex.row() <= last:
                ## Item deleted, close tab
                #self.mw.mainEditor.tab.removeTab(self.mw.mainEditor.tab.indexOf(self))

    def updateStatusBar(self):
        # Update progress
        # if self.currentIndex and self.currentIndex.isValid():
        # if self._model:
        mw = mainWindow()
        if not mw:
            return

        mw.mainEditor.updateStats()

    def toggleSpellcheck(self, v):
        self.spellcheck = v
        self.toggledSpellcheck.emit(v)

    def setDict(self, dct):
        self.currentDict = dct
        self.dictChanged.emit(dct)
