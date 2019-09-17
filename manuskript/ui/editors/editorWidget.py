#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import pyqtSignal, QModelIndex
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QWidget, QFrame, QSpacerItem, QSizePolicy
from PyQt5.QtWidgets import QVBoxLayout, qApp, QStyle

from manuskript import settings
from manuskript.functions import AUC, mainWindow
from manuskript.ui.editors.editorWidget_ui import Ui_editorWidget_ui
from manuskript.ui.views.MDEditView import MDEditView
from manuskript.ui.tools.splitDialog import splitDialog


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

    _maxTabTitleLength = 24

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
        self.spellcheck = settings.spellcheck
        self.folderView = "cork"
        self.mw = mainWindow()
        self._tabWidget = None  # set by mainEditor on creation

        self._model = None

        # Capture textEdit scrollbar, so that we can put it outside the margins.
        self.txtEditScrollBar = self.txtRedacText.verticalScrollBar()
        self.txtEditScrollBar.setParent(self)
        self.stack.currentChanged.connect(self.setScrollBarVisibility)

        # def setModel(self, model):
        # self._model = model
        # self.setView()

    def resizeEvent(self, event):
        """
        textEdit's scrollBar has been reparented to self. So we need to
        update it's geometry when self is resized, and put it where we want it
        to be.
        """
        # Update scrollbar geometry
        r = self.geometry()
        w = 10  # Cf. style.mainEditorTabSS
        r.setWidth(w)
        r.moveRight(self.geometry().width())
        self.txtEditScrollBar.setGeometry(r)

        QWidget.resizeEvent(self, event)

    def setScrollBarVisibility(self):
        """
        Since the texteEdit scrollBar has been reparented to self, it is not
        hidden when stack changes. We have to do it manually.
        """
        self.txtEditScrollBar.setVisible(self.stack.currentIndex() == 0)

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

        self._tabWidget.setTabText(i, self.ellidedTitle(item.title()))
        self._tabWidget.setTabToolTip(i, item.title())

    def ellidedTitle(self, title):
        if len(title) > self._maxTabTitleLength:
            return "{}…".format(title[:self._maxTabTitleLength])
        else:
            return title

    def setView(self):
        # index = mainWindow().treeRedacOutline.currentIndex()

        # Counting the number of other selected items
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
            edt = MDEditView(self, html="<h{l}>{t}</h{l}>".format(l=min(itm.level() + 1, 5), t=itm.title()),
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
            edt = MDEditView(self,
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
            opt = settings.textEditor
            background = (opt["background"] if not opt["backgroundTransparent"]
                          else "transparent")
            w.setStyleSheet("background: {};".format(background))
            self.stack.widget(1).setStyleSheet("background: {}"
                                               .format(background))
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
            self._model.rowsAboutToBeRemoved.connect(self.rowsAboutToBeRemoved, AUC)
        except TypeError:
            pass

        self.updateStatusBar()

    def setCurrentModelIndex(self, index=None):
        if index and index.isValid():
            self.currentIndex = index
            self._model = index.model()
            self.currentID = self._model.ID(index)
        else:
            self.currentIndex = QModelIndex()
            self.currentID = None

        if self._model:
            self.setView()

    def updateIndexFromID(self, fallback=None, ignore=None):
        """
        Index might have changed (through drag an drop), so we keep current
        item's ID and update index. Item might have been deleted too.

        It will ignore the passed model item to avoid ambiguity during times
        of inconsistent state.
        """
        idx = self._model.getIndexByID(self.currentID, ignore=ignore)

        # If we have an ID but the ID does not exist, it has been deleted.
        if self.currentID and idx == QModelIndex():
            # If we are given a fallback item to display, do so.
            if fallback:
                self.setCurrentModelIndex(fallback)
            else:
                # After tab closing is implemented, any calls to `updateIndexFromID`
                # should be re-evaluated to match the desired behaviour.
                raise NotImplementedError("implement tab closing")

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
        if not self.currentIndex.isValid():
            return  # Just to be safe.

        # We are only concerned with minor changes to the current index,
        # so there is no need to call updateIndexFromID() nor setView().
        if topLeft.row() <= self.currentIndex.row() <= bottomRight.row():
            self.updateTabTitle()
            self.updateStatusBar()

    def rowsAboutToBeRemoved(self, parent, first, last):
        if not self.currentIndex.isValid():
            return  # Just to be safe.

        # Look for a common ancestor to verify whether the deleted rows include our index in their hierarchy.
        childItem = self.currentIndex
        ancestorCandidate = childItem.parent()  # start at folder above current item
        while (ancestorCandidate != parent):
            childItem = ancestorCandidate
            ancestorCandidate = childItem.parent()

            if not ancestorCandidate.isValid():
                return  # we ran out of ancestors without finding the matching QModelIndex

        # My sanity advocates a healthy dose of paranoia. (Just to be safe.)
        if ancestorCandidate != parent:
            return  # we did not find our shared ancestor

        # Verify our origins come from the relevant first..last range.
        if first <= childItem.row() <= last:
            # If the row in question was actually moved, there is a duplicate item
            # already inserted elsewhere in the tree. Try to update this tab view,
            # but make sure we exclude ourselves from the search for a replacement.
            self.updateIndexFromID(fallback=parent, ignore=self.currentIndex.internalPointer())

    def updateStatusBar(self):
        # Update progress
        # if self.currentIndex and self.currentIndex.isValid():
        # if self._model:
        mw = mainWindow()
        if not mw:
            return

        mw.mainEditor.tabChanged()

    def toggleSpellcheck(self, v):
        self.spellcheck = v
        self.toggledSpellcheck.emit(v)

    def setDict(self, dct):
        self.currentDict = dct
        self.dictChanged.emit(dct)

    ###############################################################################
    # FUNCTIONS FOR MENU ACCESS
    ###############################################################################

    def getCurrentItemView(self):
        """
        Returns the current item view, between txtRedacText, outlineView and
        corkView. If folder/text view, returns None. (Because handled
        differently)
        """

        if self.stack.currentIndex() == 0:
            return self.txtRedacText
        elif self.folderView == "outline":
            return self.outlineView
        elif self.folderView == "cork":
            return self.corkView
        else:
            return None

    def copy(self):
        if self.getCurrentItemView(): self.getCurrentItemView().copy()
    def cut(self):
        if self.getCurrentItemView(): self.getCurrentItemView().cut()
    def paste(self):
        if self.getCurrentItemView(): self.getCurrentItemView().paste()
    def rename(self):
        if self.getCurrentItemView(): self.getCurrentItemView().rename()
    def duplicate(self):
        if self.getCurrentItemView(): self.getCurrentItemView().duplicate()
    def delete(self):
        if self.getCurrentItemView(): self.getCurrentItemView().delete()
    def moveUp(self):
        if self.getCurrentItemView(): self.getCurrentItemView().moveUp()
    def moveDown(self):
        if self.getCurrentItemView(): self.getCurrentItemView().moveDown()

    def splitDialog(self):
        """
        Opens a dialog to split selected items.
        """
        if self.getCurrentItemView() == self.txtRedacText:
            # Text editor
            if not self.currentIndex.isValid():
                return

            sel = self.txtRedacText.textCursor().selectedText()
            # selectedText uses \u2029 instead of \n, no idea why.
            sel = sel.replace("\u2029", "\n")
            splitDialog(self, [self.currentIndex], mark=sel)

        elif self.getCurrentItemView():
            # One of the views
            self.getCurrentItemView().splitDialog()

    def splitCursor(self):
        """
        Splits items at cursor position. If there is a selection, that selection
        becomes the new item's title.

        Call context: Only works when editing a file.
        """

        if not self.currentIndex.isValid():
            return

        if self.getCurrentItemView() == self.txtRedacText:
            c = self.txtRedacText.textCursor()

            title = c.selectedText()
            # selection can be backward
            pos = min(c.selectionStart(), c.selectionEnd())

            item = self.currentIndex.internalPointer()

            item.splitAt(pos, len(title))

    def merge(self):
        """
        Merges selected items together.

        Call context: Multiple selection, same parent.
        """
        if self.getCurrentItemView() == self.txtRedacText:
            # Text editor, nothing to merge
            pass

        elif self.getCurrentItemView():
            # One of the views
            self.getCurrentItemView().merge()
