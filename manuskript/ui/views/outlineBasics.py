#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt, QSignalMapper, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAbstractItemView, qApp, QMenu, QAction
from PyQt5.QtWidgets import QListWidget, QWidgetAction, QListWidgetItem, QLineEdit

from manuskript import settings
from manuskript.enums import Outline
from manuskript.functions import mainWindow
from manuskript.functions import toInt, customIcons
from manuskript.models.outlineModel import outlineItem


class outlineBasics(QAbstractItemView):
    def __init__(self, parent=None):
        pass

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
        else:
            QAbstractItemView.mouseReleaseEvent(self, event)

    def makePopupMenu(self):
        index = self.currentIndex()
        sel = self.getSelection()
        clipboard = qApp.clipboard()

        menu = QMenu(self)

        # Add / remove items
        self.actOpen = QAction(QIcon.fromTheme("go-right"), qApp.translate("outlineBasics", "Open Item"), menu)
        self.actOpen.triggered.connect(self.openItem)
        menu.addAction(self.actOpen)

        menu.addSeparator()

        # Add / remove items
        self.actAddFolder = QAction(QIcon.fromTheme("folder-new"), qApp.translate("outlineBasics", "New Folder"), menu)
        self.actAddFolder.triggered.connect(self.addFolder)
        menu.addAction(self.actAddFolder)

        self.actAddText = QAction(QIcon.fromTheme("document-new"), qApp.translate("outlineBasics", "New Text"), menu)
        self.actAddText.triggered.connect(self.addText)
        menu.addAction(self.actAddText)

        self.actDelete = QAction(QIcon.fromTheme("edit-delete"), qApp.translate("outlineBasics", "Delete"), menu)
        self.actDelete.triggered.connect(self.delete)
        menu.addAction(self.actDelete)

        menu.addSeparator()

        # Copy, cut, paste
        self.actCopy = QAction(QIcon.fromTheme("edit-copy"), qApp.translate("outlineBasics", "Copy"), menu)
        self.actCopy.triggered.connect(self.copy)
        menu.addAction(self.actCopy)

        self.actCut = QAction(QIcon.fromTheme("edit-cut"), qApp.translate("outlineBasics", "Cut"), menu)
        self.actCut.triggered.connect(self.cut)
        menu.addAction(self.actCut)

        self.actPaste = QAction(QIcon.fromTheme("edit-paste"), qApp.translate("outlineBasics", "Paste"), menu)
        self.actPaste.triggered.connect(self.paste)
        menu.addAction(self.actPaste)

        menu.addSeparator()

        # POV
        self.menuPOV = QMenu(qApp.translate("outlineBasics", "Set POV"), menu)
        mw = mainWindow()
        a = QAction(QIcon.fromTheme("dialog-no"), qApp.translate("outlineBasics", "None"), self.menuPOV)
        a.triggered.connect(lambda: self.setPOV(""))
        self.menuPOV.addAction(a)
        self.menuPOV.addSeparator()

        menus = []
        for i in [self.tr("Main"), self.tr("Secondary"), self.tr("Minor")]:
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
        self.menuCustomIcons = QMenu(qApp.translate("outlineBasics", "Set Custom Icon"), menu)
        a = QAction(qApp.translate("outlineBasics", "Restore to default"), self.menuCustomIcons)
        a.triggered.connect(lambda: self.setCustomIcon(""))
        self.menuCustomIcons.addAction(a)
        self.menuCustomIcons.addSeparator()

        txt = QLineEdit()
        txt.textChanged.connect(self.filterLstIcons)
        txt.setPlaceholderText("Filter icons")
        txt.setStyleSheet("background: transparent; border: none;")
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
        if len(sel) > 0 and index.isValid() and not index.internalPointer().isFolder() \
                or not clipboard.mimeData().hasFormat("application/xml"):
            self.actPaste.setEnabled(False)

        if len(sel) > 0 and index.isValid() and not index.internalPointer().isFolder():
            self.actAddFolder.setEnabled(False)
            self.actAddText.setEnabled(False)

        if len(sel) == 0:
            self.actOpen.setEnabled(False)
            self.actCopy.setEnabled(False)
            self.actCut.setEnabled(False)
            self.actDelete.setEnabled(False)
            self.menuPOV.setEnabled(False)
            self.menuStatus.setEnabled(False)
            self.menuLabel.setEnabled(False)
            self.menuCustomIcons.setEnabled(False)

        return menu

    def openItem(self):
        idx = self.currentIndex()
        from manuskript.functions import MW
        MW.openIndex(idx)

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

    def paste(self):
        index = self.currentIndex()
        if len(self.getSelection()) == 0:
            index = self.rootIndex()
        data = qApp.clipboard().mimeData()
        self.model().dropMimeData(data, Qt.CopyAction, -1, 0, index)

    def cut(self):
        self.copy()
        self.delete()

    def delete(self):
        self.model().removeIndexes(self.getSelection())

    def setPOV(self, POV):
        for i in self.getSelection():
            self.model().setData(i.sibling(i.row(), Outline.POV.value), str(POV))

    def setStatus(self, status):
        for i in self.getSelection():
            self.model().setData(i.sibling(i.row(), Outline.status.value), str(status))

    def setLabel(self, label):
        for i in self.getSelection():
            self.model().setData(i.sibling(i.row(), Outline.label.value), str(label))

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
