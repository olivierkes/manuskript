#!/usr/bin/env python
# --!-- coding: utf8 --!--

import datetime
import difflib
import re

from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPalette, QFontMetrics
from PyQt5.QtWidgets import QWidget, QMenu, QActionGroup, QAction, QListWidgetItem, QStyledItemDelegate, QStyle

from manuskript.enums import Outline
from manuskript.ui.revisions_ui import Ui_revisions
from manuskript.models import references as Ref


class revisions(QWidget, Ui_revisions):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.splitter.setStretchFactor(0, 5)
        self.splitter.setStretchFactor(1, 70)

        self.listDelegate = listCompleterDelegate(self)
        self.list.setItemDelegate(self.listDelegate)
        self.list.itemClicked.connect(self.showDiff)
        self.list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self.popupMenu)
        self.btnDelete.setEnabled(False)
        self.btnDelete.clicked.connect(self.delete)
        self.btnRestore.clicked.connect(self.restore)
        self.btnRestore.setEnabled(False)

        # self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.updateTimer = QTimer()
        self.updateTimer.setSingleShot(True)
        self.updateTimer.setInterval(500)
        self.updateTimer.timeout.connect(self.update)
        self.updateTimer.stop()

        self.menu = QMenu(self)
        self.actGroup = QActionGroup(self)

        self.actShowDiff = QAction(self.tr("Show modifications"), self.menu)
        self.actShowDiff.setCheckable(True)
        self.actShowDiff.setChecked(True)
        self.actShowDiff.triggered.connect(self.showDiff)
        self.menu.addAction(self.actShowDiff)
        self.actGroup.addAction(self.actShowDiff)

        self.actShowVersion = QAction(self.tr("Show ancient version"), self.menu)
        self.actShowVersion.setCheckable(True)
        self.actShowVersion.setChecked(False)
        self.actShowVersion.triggered.connect(self.showDiff)
        self.menu.addAction(self.actShowVersion)
        self.actGroup.addAction(self.actShowVersion)

        self.menu.addSeparator()
        self.actShowSpaces = QAction(self.tr("Show spaces"), self.menu)
        self.actShowSpaces.setCheckable(True)
        self.actShowSpaces.setChecked(False)
        self.actShowSpaces.triggered.connect(self.showDiff)
        self.menu.addAction(self.actShowSpaces)

        self.actDiffOnly = QAction(self.tr("Show modifications only"), self.menu)
        self.actDiffOnly.setCheckable(True)
        self.actDiffOnly.setChecked(True)
        self.actDiffOnly.triggered.connect(self.showDiff)
        self.menu.addAction(self.actDiffOnly)
        self.btnOptions.setMenu(self.menu)

        self._model = None
        self._index = None

    def setModel(self, model):
        self._model = model
        self._model.dataChanged.connect(self.updateMaybe)

    def setCurrentModelIndex(self, index):
        self._index = index
        self.view.setText("")
        self.update()

    def updateMaybe(self, topLeft, bottomRight):
        if self._index and \
                                topLeft.column() <= Outline.revisions.value <= bottomRight.column() and \
                                topLeft.row() <= self._index.row() <= bottomRight.row():
            # self.update()
            self.updateTimer.start()

    def update(self):
        self.list.clear()
        item = self._index.internalPointer()
        rev = item.revisions()
        # Sort revisions
        rev = sorted(rev, key=lambda x: x[0], reverse=True)
        for r in rev:
            timestamp = datetime.datetime.fromtimestamp(r[0]).strftime('%Y-%m-%d %H:%M:%S')
            readable = self.readableDelta(r[0])
            i = QListWidgetItem(readable)
            i.setData(Qt.UserRole, r[0])
            i.setData(Qt.UserRole + 1, timestamp)
            self.list.addItem(i)

    def readableDelta(self, timestamp):
        now = datetime.datetime.now()
        delta = now - datetime.datetime.fromtimestamp(timestamp)
        if delta.days > 365:
            return self.tr("{} years ago").format(str(int(delta.days / 365)))
        elif delta.days > 30:
            return self.tr("{} months ago").format(str(int(delta.days / 30.5)))
        elif delta.days > 0:
            return self.tr("{} days ago").format(str(delta.days))
        if delta.days == 1:
            return self.tr("1 day ago")
        elif delta.seconds > 60 * 60:
            return self.tr("{} hours ago").format(str(int(delta.seconds / 60 / 60)))
        elif delta.seconds > 60:
            return self.tr("{} minutes ago").format(str(int(delta.seconds / 60)))
        else:
            return self.tr("{} seconds ago").format(str(delta.seconds))

    def showDiff(self):
        # UI stuff
        self.actShowSpaces.setEnabled(self.actShowDiff.isChecked())
        self.actDiffOnly.setEnabled(self.actShowDiff.isChecked())

        # FIXME: Errors in line number
        i = self.list.currentItem()

        if not i:
            self.btnDelete.setEnabled(False)
            self.btnRestore.setEnabled(False)
            return

        self.btnDelete.setEnabled(True)
        self.btnRestore.setEnabled(True)

        ts = i.data(Qt.UserRole)
        item = self._index.internalPointer()

        textNow = item.text()
        textBefore = [r[1] for r in item.revisions() if r[0] == ts][0]

        if self.actShowVersion.isChecked():
            self.view.setText(textBefore)
            return

        textNow = textNow.splitlines()
        textBefore = textBefore.splitlines()

        d = difflib.Differ()
        diff = list(d.compare(textBefore, textNow))

        if self.actShowSpaces.isChecked():
            _format = lambda x: x.replace(" ", "␣ ")
        else:
            _format = lambda x: x

        extra = "<br>"
        diff = [d for d in diff if d and not d[:2] == "? "]
        mydiff = ""
        skip = False
        for n, l in enumerate(diff):
            l = diff[n]
            op = l[:2]
            txt = l[2:]
            op2 = diff[n + 1][:2] if n + 1 < len(diff) else None
            txt2 = diff[n + 1][2:] if n + 1 < len(diff) else None

            if skip:
                skip = False
                continue

            # Same line
            if op == "  " and not self.actDiffOnly.isChecked():
                mydiff += "{}{}".format(txt, extra)

            elif op == "- " and op2 == "+ ":
                if self.actDiffOnly.isChecked():
                    mydiff += "<br><span style='color: blue;'>{}</span><br>".format(
                            self.tr("Line {}:").format(str(n)))
                s = difflib.SequenceMatcher(None, txt, txt2, autojunk=True)
                newline = ""
                for tag, i1, i2, j1, j2 in s.get_opcodes():
                    if tag == "equal":
                        newline += txt[i1:i2]
                    elif tag == "delete":
                        newline += "<span style='color:red; background:yellow;'>{}</span>".format(_format(txt[i1:i2]))
                    elif tag == "insert":
                        newline += "<span style='color:green; background:yellow;'>{}</span>".format(
                            _format(txt2[j1:j2]))
                    elif tag == "replace":
                        newline += "<span style='color:red; background:yellow;'>{}</span>".format(_format(txt[i1:i2]))
                        newline += "<span style='color:green; background:yellow;'>{}</span>".format(
                            _format(txt2[j1:j2]))

                # Few ugly tweaks for html diffs
                newline = re.sub(r"(<span style='color.*?><span.*?>)</span>(.*)<span style='color:.*?>(</span></span>)",
                                 "\\1\\2\\3", newline)
                newline = re.sub(
                    r"<p align=\"<span style='color:red; background:yellow;'>cen</span><span style='color:green; background:yellow;'>righ</span>t<span style='color:red; background:yellow;'>er</span>\" style=\" -qt-block-indent:0; -qt-user-state:0; \">(.*?)</p>",
                    "<p align=\"right\"><span style='color:green; background:yellow;'>\\1</span></p>", newline)
                newline = re.sub(
                    r"<p align=\"<span style='color:green; background:yellow;'>cente</span>r<span style='color:red; background:yellow;'>ight</span>\" style=\" -qt-block-indent:0; -qt-user-state:0; \">(.*)</p>",
                    "<p align=\"center\"><span style='color:green; background:yellow;'>\\1</span></p>", newline)
                newline = re.sub(r"<p(<span.*?>)(.*?)(</span>)(.*?)>(.*?)</p>",
                                 "<p\\2\\4>\\1\\5\\3</p>", newline)

                mydiff += newline + extra
                skip = True
            elif op == "- ":
                if self.actDiffOnly.isChecked():
                    mydiff += "<br>{}:<br>".format(str(n))
                mydiff += "<span style='color:red;'>{}</span>{}".format(txt, extra)
            elif op == "+ ":
                if self.actDiffOnly.isChecked():
                    mydiff += "<br>{}:<br>".format(str(n))
                mydiff += "<span style='color:green;'>{}</span>{}".format(txt, extra)

        self.view.setText(mydiff)

    def restore(self):
        i = self.list.currentItem()
        if not i:
            return
        ts = i.data(Qt.UserRole)
        item = self._index.internalPointer()
        textBefore = [r[1] for r in item.revisions() if r[0] == ts][0]
        index = self._index.sibling(self._index.row(), Outline.text.value)
        self._index.model().setData(index, textBefore)
        # item.setData(Outline.text.value, textBefore)

    def delete(self):
        i = self.list.currentItem()
        if not i:
            return
        ts = i.data(Qt.UserRole)
        self._index.internalPointer().deleteRevision(ts)

    def clearAll(self):
        self._index.internalPointer().clearAllRevisions()

    def saveState(self):
        return [
            self.actShowDiff.isChecked(),
            self.actShowVersion.isChecked(),
            self.actShowSpaces.isChecked(),
            self.actDiffOnly.isChecked(),
        ]

    def popupMenu(self, pos):
        i = self.list.itemAt(pos)
        m = QMenu(self)
        if i:
            m.addAction(self.tr("Restore")).triggered.connect(self.restore)
            m.addAction(self.tr("Delete")).triggered.connect(self.delete)
            m.addSeparator()
        if self.list.count():
            m.addAction(self.tr("Clear all")).triggered.connect(self.clearAll)

        m.popup(self.list.mapToGlobal(pos))

    def restoreState(self, state):
        self.actShowDiff.setChecked(state[0])
        self.actShowVersion.setChecked(state[1])
        self.actShowSpaces.setChecked(state[2])
        self.actDiffOnly.setChecked(state[3])
        self.actShowSpaces.setEnabled(self.actShowDiff.isChecked())
        self.actDiffOnly.setEnabled(self.actShowDiff.isChecked())


class listCompleterDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)

    def paint(self, painter, option, index):
        extra = index.data(Qt.UserRole + 1)
        if not extra:
            return QStyledItemDelegate.paint(self, painter, option, index)

        else:
            if option.state & QStyle.State_Selected:
                painter.fillRect(option.rect, option.palette.color(QPalette.Inactive, QPalette.Highlight))

            title = index.data()
            extra = " - {}".format(extra)
            painter.drawText(option.rect, Qt.AlignLeft, title)

            fm = QFontMetrics(option.font)
            w = fm.width(title)
            r = QRect(option.rect)
            r.setLeft(r.left() + w)
            painter.save()
            painter.setPen(Qt.gray)
            painter.drawText(r, Qt.AlignLeft, extra)
            painter.restore()
