#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt, QRect, QEvent, QCoreApplication
from PyQt5.QtGui import QPalette, QFontMetrics, QKeySequence
from PyQt5.QtWidgets import QWidget, qApp, QListWidgetItem, QStyledItemDelegate, QStyle, QLabel, QToolTip, QShortcut


from manuskript.functions import mainWindow
from manuskript.ui_qt import style
from manuskript.ui_qt.search_ui import Ui_search
from manuskript.enums import Model

from manuskript.models.flatDataModelWrapper import flatDataModelWrapper
from manuskript.ui_qt.searchMenu import searchMenu
from manuskript.ui_qt.highlighters.searchResultHighlighters.searchResultHighlighter import searchResultHighlighter


class search(QWidget, Ui_search):
    def __init__(self, parent=None):
        _translate = QCoreApplication.translate

        QWidget.__init__(self, parent)
        self.setupUi(self)

        self.searchTextInput.returnPressed.connect(self.search)

        self.searchMenu = searchMenu()
        self.btnOptions.setMenu(self.searchMenu)

        self.delegate = listResultDelegate(self)
        self.result.setItemDelegate(self.delegate)
        self.result.setMouseTracking(True)
        self.result.itemClicked.connect(self.openItem)

        self.result.setStyleSheet(style.searchResultSS())
        self.searchTextInput.setStyleSheet(style.lineEditSS())

        self.searchResultHighlighter = searchResultHighlighter()

        self.noResultsLabel = QLabel(_translate("Search", "No results found"), self.result)
        self.noResultsLabel.setVisible(False)
        self.noResultsLabel.setStyleSheet("QLabel {color: gray;}")

        # Add shortcuts for navigating through search results
        QShortcut(QKeySequence(_translate("MainWindow", "F3")), self.searchTextInput, self.nextSearchResult)
        QShortcut(QKeySequence(_translate("MainWindow", "Shift+F3")), self.searchTextInput, self.previousSearchResult)

        # These texts are already included in translation files but including ":" at the end. We force here the
        # translation for them without ":"
        _translate("MainWindow", "Situation")
        _translate("MainWindow", "Status")

    def nextSearchResult(self):
        if self.result.currentRow() < self.result.count() - 1:
            self.result.setCurrentRow(self.result.currentRow() + 1)
        else:
            self.result.setCurrentRow(0)

        if 0 < self.result.currentRow() < self.result.count():
            self.openItem(self.result.currentItem())

    def previousSearchResult(self):
        if self.result.currentRow() > 0:
            self.result.setCurrentRow(self.result.currentRow() - 1)
        else:
            self.result.setCurrentRow(self.result.count() - 1)

        if 0 < self.result.currentRow() < self.result.count():
            self.openItem(self.result.currentItem())

    def prepareRegex(self, searchText):
        import re

        flags = re.UNICODE

        if self.searchMenu.caseSensitive() is False:
            flags |= re.IGNORECASE

        if self.searchMenu.regex() is False:
            searchText = re.escape(searchText)

        if self.searchMenu.matchWords() is True:
            # Source: https://stackoverflow.com/a/15863102
            searchText = r'\b' + searchText + r'\b'

        return re.compile(searchText, flags)

    def search(self):
        self.result.clear()
        self.result.setCurrentRow(0)

        searchText = self.searchTextInput.text()
        if len(searchText) > 0:
            searchRegex = self.prepareRegex(searchText)
            results = []

            # Set override cursor
            qApp.setOverrideCursor(Qt.WaitCursor)

            for model, modelName in [
                (mainWindow().mdlOutline, Model.Outline),
                (mainWindow().mdlCharacter, Model.Character),
                (flatDataModelWrapper(mainWindow().mdlFlatData), Model.FlatData),
                (mainWindow().mdlWorld, Model.World),
                (mainWindow().mdlPlots, Model.Plot)
            ]:
                filteredColumns = self.searchMenu.columns(modelName)

                # Searching
                if len(filteredColumns):
                    results += model.searchOccurrences(searchRegex, filteredColumns)

            # Showing results
            self.generateResultsLists(results)

            # Remove override cursor
            qApp.restoreOverrideCursor()

    def generateResultsLists(self, results):
        self.noResultsLabel.setVisible(len(results) == 0)
        for result in results:
            item = QListWidgetItem(result.title(), self.result)
            item.setData(Qt.UserRole, result)
            item.setData(Qt.UserRole + 1, ' > '.join(result.path()))
            item.setData(Qt.UserRole + 2, result.context())
            self.result.addItem(item)

    def openItem(self, item):
        self.searchResultHighlighter.highlightSearchResult(item.data(Qt.UserRole))

    def leaveEvent(self, event):
        self.delegate.mouseLeave()

class listResultDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self._tooltipRowIndex = -1

    def paint(self, painter, option, index):
        extra = index.data(Qt.UserRole + 1)

        if not extra:
            return QStyledItemDelegate.paint(self, painter, option, index)
        else:
            if option.state & QStyle.State_Selected:
                painter.fillRect(option.rect, option.palette.color(QPalette.Highlight))

            title = index.data()
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
            painter.drawText(r.adjusted(2, 1, 0, 0), Qt.AlignLeft, " - {}".format(extra))
            painter.restore()

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseMove and self._tooltipRowIndex != index.row():
            self._tooltipRowIndex = index.row()
            context = index.data(Qt.UserRole + 2)
            extra = index.data(Qt.UserRole + 1)
            QToolTip.showText(event.globalPos(),
                              "<p>#" + str(index.row()) + " - " + extra + "</p><p>" + context + "</p>")
            return True
        return False

    def mouseLeave(self):
        self._tooltipRowIndex = -1
