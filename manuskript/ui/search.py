#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPalette, QFontMetrics
from PyQt5.QtWidgets import QWidget, QMenu, QAction, qApp, QListWidgetItem, QStyledItemDelegate, QStyle

from manuskript.enums import Outline
from manuskript.functions import mainWindow
from manuskript.ui import style
from manuskript.ui.search_ui import Ui_search
from manuskript.models import references as Ref


class search(QWidget, Ui_search):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        self.options = {
            "All": True,
            "Title": True,
            "Text": True,
            "Summary": False,
            "Notes": False,
            "POV": False,
            "Status": False,
            "Label": False,
            "CS": True
        }

        self.text.returnPressed.connect(self.search)
        self.generateOptionMenu()

        self.delegate = listResultDelegate(self)
        self.result.setItemDelegate(self.delegate)
        self.result.itemClicked.connect(self.openItem)

        self.result.setStyleSheet(style.searchResultSS())
        self.text.setStyleSheet(style.lineEditSS())

    def generateOptionMenu(self):
        self.menu = QMenu(self)
        a = QAction(self.tr("Search in:"), self.menu)
        a.setEnabled(False)
        self.menu.addAction(a)
        for i, d in [
            (self.tr("All"), "All"),
            (self.tr("Title"), "Title"),
            (self.tr("Text"), "Text"),
            (self.tr("Summary"), "Summary"),
            (self.tr("Notes"), "Notes"),
            (self.tr("POV"), "POV"),
            (self.tr("Status"), "Status"),
            (self.tr("Label"), "Label"),
        ]:
            a = QAction(i, self.menu)
            a.setCheckable(True)
            a.setChecked(self.options[d])
            a.setData(d)
            a.triggered.connect(self.updateOptions)
            self.menu.addAction(a)
        self.menu.addSeparator()

        a = QAction(self.tr("Options:"), self.menu)
        a.setEnabled(False)
        self.menu.addAction(a)
        for i, d in [
            (self.tr("Case sensitive"), "CS"),
        ]:
            a = QAction(i, self.menu)
            a.setCheckable(True)
            a.setChecked(self.options[d])
            a.setData(d)
            a.triggered.connect(self.updateOptions)
            self.menu.addAction(a)
        self.menu.addSeparator()

        self.btnOptions.setMenu(self.menu)

    def updateOptions(self):
        a = self.sender()
        self.options[a.data()] = a.isChecked()

    def search(self):
        text = self.text.text()

        # Chosing the right columns
        lstColumns = [
            ("Title", Outline.title.value),
            ("Text", Outline.text.value),
            ("Summary", Outline.summarySentence.value),
            ("Summary", Outline.summaryFull.value),
            ("Notes", Outline.notes.value),
            ("POV", Outline.POV.value),
            ("Status", Outline.status.value),
            ("Label", Outline.label.value),
        ]
        columns = [c[1] for c in lstColumns if self.options[c[0]] or self.options["All"]]

        # Setting override cursor
        qApp.setOverrideCursor(Qt.WaitCursor)

        # Searching
        model = mainWindow().mdlOutline
        results = model.findItemsContaining(text, columns, self.options["CS"])

        # Showing results
        self.result.clear()
        for r in results:
            index = model.getIndexByID(r)
            if not index.isValid():
                continue
            item = index.internalPointer()
            i = QListWidgetItem(item.title(), self.result)
            i.setData(Qt.UserRole, r)
            i.setData(Qt.UserRole + 1, item.path())
            self.result.addItem(i)

        # Removing override cursor
        qApp.restoreOverrideCursor()

    def openItem(self, item):
        r = Ref.textReference(item.data(Qt.UserRole))
        Ref.open(r)
        # mw = mainWindow()
        # index = mw.mdlOutline.getIndexByID(item.data(Qt.UserRole))
        # mw.mainEditor.setCurrentModelIndex(index, newTab=True)


class listResultDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)

    def paint(self, painter, option, index):
        extra = index.data(Qt.UserRole + 1)
        if not extra:
            return QStyledItemDelegate.paint(self, painter, option, index)

        else:
            if option.state & QStyle.State_Selected:
                painter.fillRect(option.rect, option.palette.color(QPalette.Highlight))

            title = index.data()
            extra = " - {}".format(extra)
            painter.drawText(option.rect.adjusted(2, 1, 0, 0), Qt.AlignLeft, title)

            fm = QFontMetrics(option.font)
            w = fm.width(title)
            r = QRect(option.rect)
            r.setLeft(r.left() + w)
            painter.save()
            if option.state & QStyle.State_Selected:
                painter.setPen(Qt.white)
            else:
                painter.setPen(Qt.gray)
            painter.drawText(r.adjusted(2, 1, 0, 0), Qt.AlignLeft, extra)
            painter.restore()
