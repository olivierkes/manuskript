#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt, QSignalMapper, QSize
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtWidgets import QAbstractItemView, qApp, QMenu, QAction, \
                            QListWidget, QWidgetAction, QListWidgetItem, \
                            QLineEdit, QInputDialog, QMessageBox, QCheckBox

from manuskript import settings
from manuskript.enums import Outline
from manuskript.functions import mainWindow, statusMessage
from manuskript.functions import toInt, customIcons
from manuskript.models import outlineItem
from manuskript.ui.tools.splitDialog import splitDialog


class outlineBasics(QAbstractItemView):
    def __init__(self, parent=None):
        self._indexesToOpen = None
        self.menuCustomIcons = None

    def getSelection(self):
        sel = []
        for i in self.selectedIndexes():
            if i.column() != 0:
                continue
            if not i in sel:
                sel.append(i)
        return sel

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.menu = self.makePopupMenu()
            self.menu.popup(event.globalPos())
        # We don't call QAbstractItemView.mouseReleaseEvent because
        # outlineBasics is never subclassed alone. So the others views
        # (outlineView, corkView, treeView) that subclass outlineBasics
        # call their respective mother class.

    def makePopupMenu(self):
        index = self.currentIndex()
        sel = self.getSelection()
        clipboard = qApp.clipboard()

        menu = QMenu(self)

        # Get index under cursor
        pos = self.viewport().mapFromGlobal(QCursor.pos())
        mouseIndex = self.indexAt(pos)

        # Get index's title
        if mouseIndex.isValid():
            title = mouseIndex.internalPointer().title()

        elif self.rootIndex().parent().isValid():
            # mouseIndex is the background of an item, so we check the parent
            mouseIndex = self.rootIndex().parent()
            title = mouseIndex.internalPointer().title()

        else:
            title = qApp.translate("outlineBasics", "Root")

        if len(title) > 25:
            title = title[:25] + "…"

        # Open Item action
        self.actOpen = QAction(QIcon.fromTheme("go-right"),
                               qApp.translate("outlineBasics", "Open {}".format(title)),
                               menu)
        self.actOpen.triggered.connect(self.openItem)
        menu.addAction(self.actOpen)

        # Open item(s) in new tab
        if mouseIndex in sel and len(sel) > 1:
            actionTitle = qApp.translate("outlineBasics", "Open {} items in new tabs").format(len(sel))
            self._indexesToOpen = sel
        else:
            actionTitle = qApp.translate("outlineBasics", "Open {} in a new tab").format(title)
            self._indexesToOpen = [mouseIndex]

        self.actNewTab = QAction(QIcon.fromTheme("go-right"), actionTitle, menu)
        self.actNewTab.triggered.connect(self.openItemsInNewTabs)
        menu.addAction(self.actNewTab)

        menu.addSeparator()

        # Add text / folder
        self.actAddFolder = QAction(QIcon.fromTheme("folder-new"),
                                    qApp.translate("outlineBasics", "New &Folder"),
                                    menu)
        self.actAddFolder.triggered.connect(self.addFolder)
        menu.addAction(self.actAddFolder)

        self.actAddText = QAction(QIcon.fromTheme("document-new"),
                                  qApp.translate("outlineBasics", "New &Text"),
                                  menu)
        self.actAddText.triggered.connect(self.addText)
        menu.addAction(self.actAddText)

        menu.addSeparator()

        # Copy, cut, paste, duplicate
        self.actCut = QAction(QIcon.fromTheme("edit-cut"),
                              qApp.translate("outlineBasics", "C&ut"), menu)
        self.actCut.triggered.connect(self.cut)
        menu.addAction(self.actCut)

        self.actCopy = QAction(QIcon.fromTheme("edit-copy"),
                               qApp.translate("outlineBasics", "&Copy"), menu)
        self.actCopy.triggered.connect(self.copy)
        menu.addAction(self.actCopy)

        self.actPaste = QAction(QIcon.fromTheme("edit-paste"),
                                qApp.translate("outlineBasics", "&Paste"), menu)
        self.actPaste.triggered.connect(self.paste)
        menu.addAction(self.actPaste)

        # Rename / duplicate / remove items
        self.actDelete = QAction(QIcon.fromTheme("edit-delete"),
                                 qApp.translate("outlineBasics", "&Delete"),
                                 menu)
        self.actDelete.triggered.connect(self.delete)
        menu.addAction(self.actDelete)

        self.actRename = QAction(QIcon.fromTheme("edit-rename"),
                                 qApp.translate("outlineBasics", "&Rename"),
                                 menu)
        self.actRename.triggered.connect(self.rename)
        menu.addAction(self.actRename)

        menu.addSeparator()

        # POV
        self.menuPOV = QMenu(qApp.translate("outlineBasics", "Set POV"), menu)
        mw = mainWindow()
        a = QAction(QIcon.fromTheme("dialog-no"), qApp.translate("outlineBasics", "None"), self.menuPOV)
        a.triggered.connect(lambda: self.setPOV(""))
        self.menuPOV.addAction(a)
        self.menuPOV.addSeparator()

        menus = []
        for i in [qApp.translate("outlineBasics", "Main"),
                  qApp.translate("outlineBasics", "Secondary"),
                  qApp.translate("outlineBasics", "Minor")]:
            m = QMenu(i, self.menuPOV)
            menus.append(m)
            self.menuPOV.addMenu(m)

        mpr = QSignalMapper(self.menuPOV)
        for i in range(mw.mdlCharacter.rowCount()):
            a = QAction(mw.mdlCharacter.icon(i), mw.mdlCharacter.name(i), self.menuPOV)
            a.triggered.connect(mpr.map)
            mpr.setMapping(a, int(mw.mdlCharacter.ID(i)))

            imp = toInt(mw.mdlCharacter.importance(i))

            menus[2 - imp].addAction(a)

        mpr.mapped.connect(self.setPOV)
        menu.addMenu(self.menuPOV)

        # Status
        self.menuStatus = QMenu(qApp.translate("outlineBasics", "Set Status"), menu)
        # a = QAction(QIcon.fromTheme("dialog-no"), qApp.translate("outlineBasics", "None"), self.menuStatus)
        # a.triggered.connect(lambda: self.setStatus(""))
        # self.menuStatus.addAction(a)
        # self.menuStatus.addSeparator()

        mpr = QSignalMapper(self.menuStatus)
        for i in range(mw.mdlStatus.rowCount()):
            a = QAction(mw.mdlStatus.item(i, 0).text(), self.menuStatus)
            a.triggered.connect(mpr.map)
            mpr.setMapping(a, i)
            self.menuStatus.addAction(a)
        mpr.mapped.connect(self.setStatus)
        menu.addMenu(self.menuStatus)

        # Labels
        self.menuLabel = QMenu(qApp.translate("outlineBasics", "Set Label"), menu)
        mpr = QSignalMapper(self.menuLabel)
        for i in range(mw.mdlLabels.rowCount()):
            a = QAction(mw.mdlLabels.item(i, 0).icon(),
                        mw.mdlLabels.item(i, 0).text(),
                        self.menuLabel)
            a.triggered.connect(mpr.map)
            mpr.setMapping(a, i)
            self.menuLabel.addAction(a)
        mpr.mapped.connect(self.setLabel)
        menu.addMenu(self.menuLabel)

        menu.addSeparator()

        # Custom icons
        if self.menuCustomIcons:
            menu.addMenu(self.menuCustomIcons)
        else:
            self.menuCustomIcons = QMenu(qApp.translate("outlineBasics", "Set Custom Icon"), menu)
            a = QAction(qApp.translate("outlineBasics", "Restore to default"), self.menuCustomIcons)
            a.triggered.connect(lambda: self.setCustomIcon(""))
            self.menuCustomIcons.addAction(a)
            self.menuCustomIcons.addSeparator()

            txt = QLineEdit()
            txt.textChanged.connect(self.filterLstIcons)
            txt.setPlaceholderText("Filter icons")
            txt.setStyleSheet("QLineEdit { background: transparent; border: none; }")
            act = QWidgetAction(self.menuCustomIcons)
            act.setDefaultWidget(txt)
            self.menuCustomIcons.addAction(act)

            self.lstIcons = QListWidget()
            for i in customIcons():
                item = QListWidgetItem()
                item.setIcon(QIcon.fromTheme(i))
                item.setData(Qt.UserRole, i)
                item.setToolTip(i)
                self.lstIcons.addItem(item)
            self.lstIcons.itemClicked.connect(self.setCustomIconFromItem)
            self.lstIcons.setViewMode(self.lstIcons.IconMode)
            self.lstIcons.setUniformItemSizes(True)
            self.lstIcons.setResizeMode(self.lstIcons.Adjust)
            self.lstIcons.setMovement(self.lstIcons.Static)
            self.lstIcons.setStyleSheet("background: transparent; background: none;")
            self.filterLstIcons("")
            act = QWidgetAction(self.menuCustomIcons)
            act.setDefaultWidget(self.lstIcons)
            self.menuCustomIcons.addAction(act)

            menu.addMenu(self.menuCustomIcons)

        # Disabling stuff
        if not clipboard.mimeData().hasFormat("application/xml"):
            self.actPaste.setEnabled(False)

        if len(sel) == 0:
            self.actCopy.setEnabled(False)
            self.actCut.setEnabled(False)
            self.actRename.setEnabled(False)
            self.actDelete.setEnabled(False)
            self.menuPOV.setEnabled(False)
            self.menuStatus.setEnabled(False)
            self.menuLabel.setEnabled(False)
            self.menuCustomIcons.setEnabled(False)

        if len(sel) > 1:
            self.actRename.setEnabled(False)

        return menu

    def openItem(self):
        #idx = self.currentIndex()
        idx = self._indexesToOpen[0]
        from manuskript.functions import MW
        MW.openIndex(idx)

    def openItemsInNewTabs(self):
        from manuskript.functions import MW
        MW.openIndexes(self._indexesToOpen)

    def rename(self):
        if len(self.getSelection()) == 1:
            index = self.currentIndex()
            self.edit(index)
        elif len(self.getSelection()) > 1:
            # FIXME: add smart rename
            pass

    def addFolder(self):
        self.addItem("folder")

    def addText(self):
        self.addItem("text")

    def addItem(self, _type="folder"):
        if len(self.selectedIndexes()) == 0:
            parent = self.rootIndex()
        else:
            parent = self.currentIndex()

        if _type == "text":
            _type = settings.defaultTextType

        item = outlineItem(title=qApp.translate("outlineBasics", "New"), _type=_type)
        self.model().appendItem(item, parent)

    def copy(self):
        mimeData = self.model().mimeData(self.selectionModel().selectedIndexes())
        qApp.clipboard().setMimeData(mimeData)

    def paste(self, mimeData=None):
        """
        Paste item from mimeData to selected item. If mimeData is not given,
        it is taken from clipboard. If not item selected, paste into root.
        """
        index = self.currentIndex()
        if len(self.getSelection()) == 0:
            index = self.rootIndex()

        if not mimeData:
            mimeData = qApp.clipboard().mimeData()

        self.model().dropMimeData(mimeData, Qt.CopyAction, -1, 0, index)

    def cut(self):
        self.copy()
        self.delete()

    def delete(self):
        """
        Shows a warning, and then deletes currently selected indexes.
        """
        selection = self.getSelection()

        if not settings.dontShowDeleteWarning:
            titlesList = "".join(["<li>{}</li>".format(s.internalPointer().title())
                                  for s in selection])
            msg = QMessageBox(QMessageBox.Warning,
                qApp.translate("outlineBasics", "About to remove"),
                qApp.translate("outlineBasics",
                    "<p><b>You're about to delete {} item(s).</b></p><p>Are you sure?</p>"
                    ).format(len(selection)) +
                    "<ul>{}</ul>".format(titlesList),
                QMessageBox.Yes | QMessageBox.Cancel)

            chk = QCheckBox("&Don't show this warning in the future.")
            msg.setCheckBox(chk)
            ret = msg.exec()

            if ret == QMessageBox.Cancel:
                return

            if chk.isChecked():
                settings.dontShowDeleteWarning = True

        self.model().removeIndexes(selection)

    def duplicate(self):
        """
        Duplicates item(s), while preserving clipboard content.
        """
        mimeData = self.model().mimeData(self.selectionModel().selectedIndexes())
        self.paste(mimeData)

    def move(self, delta=1):
        """
        Move selected items up or down.
        """

        # we store selected indexes
        currentID = self.model().ID(self.currentIndex())
        selIDs = [self.model().ID(i) for i in self.selectedIndexes()]

        # Block signals
        self.blockSignals(True)
        self.selectionModel().blockSignals(True)

        # Move each index individually
        for idx in self.selectedIndexes():
            self.moveIndex(idx, delta)

        # Done the hardcore way, so inform views
        self.model().layoutChanged.emit()

        # restore selection
        selIdx = [self.model().getIndexByID(ID) for ID in selIDs]
        sm = self.selectionModel()
        sm.clear()
        [sm.select(idx, sm.Select) for idx in selIdx]
        sm.setCurrentIndex(self.model().getIndexByID(currentID), sm.Select)
        #self.setSmsgBoxelectionModel(sm)

        # Unblock signals
        self.blockSignals(False)
        self.selectionModel().blockSignals(False)

    def moveIndex(self, index, delta=1):
        """
        Move the item represented by index. +1 means down, -1 means up.
        """

        if not index.isValid():
            return

        if index.parent().isValid():
            parentItem = index.parent().internalPointer()
        else:
            parentItem = index.model().rootItem

        parentItem.childItems.insert(index.row() + delta,
                                     parentItem.childItems.pop(index.row()))
        parentItem.updateWordCount()

    def moveUp(self): self.move(-1)
    def moveDown(self): self.move(+1)

    def splitDialog(self):
        """
        Opens a dialog to split selected items.

        Call context: if at least one index is selected. Folder or text.
        """

        indexes = self.getSelection()
        if len(indexes) == 0:
            # No selection, we use parent
            indexes = [self.rootIndex()]

        splitDialog(self, indexes)

    def merge(self):
        """
        Merges selected items together.

        Call context: Multiple selection, same parent.
        """

        # Get selection
        indexes = self.getSelection()
        # Get items
        items = [i.internalPointer() for i in indexes if i.isValid()]
        # Remove folders
        items = [i for i in items if not i.isFolder()]

        # Check that we have at least 2 items
        if len(items) < 2:
            statusMessage(qApp.translate("outlineBasics",
                          "Select at least two items. Folders are ignored."),
                          importance=2)
            return

        # Check that all share the same parent
        p = items[0].parent()
        for i in items:
            if i.parent() != p:
                statusMessage(qApp.translate("outlineBasics",
                          "All items must be on the same level (share the same parent)."),
                          importance=2)
                return

        # Sort items by row
        items = sorted(items, key=lambda i: i.row())

        items[0].mergeWith(items[1:])

    def setPOV(self, POV):
        for i in self.getSelection():
            self.model().setData(i.sibling(i.row(), Outline.POV), str(POV))

    def setStatus(self, status):
        for i in self.getSelection():
            self.model().setData(i.sibling(i.row(), Outline.status), str(status))

    def setLabel(self, label):
        for i in self.getSelection():
            self.model().setData(i.sibling(i.row(), Outline.label), str(label))

    def setCustomIcon(self, customIcon):
        for i in self.getSelection():
            item = i.internalPointer()
            item.setCustomIcon(customIcon)

    def setCustomIconFromItem(self, item):
        icon = item.data(Qt.UserRole)
        self.setCustomIcon(icon)
        self.menu.close()

    def filterLstIcons(self, text):
        for l in self.lstIcons.findItems("", Qt.MatchContains):
            l.setHidden(not text in l.data(Qt.UserRole))
