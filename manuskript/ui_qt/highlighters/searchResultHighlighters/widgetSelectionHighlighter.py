#!/usr/bin/env python
# --!-- coding: utf8 --!--

from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QTextEdit, QTableView, QListView, QLineEdit, QPlainTextEdit, QLabel


class widgetSelectionHighlighter():
    """
    Utility class for highlighting a search result on a widget.
    """
    def __init__(self):
        pass

    def highlight_widget_selection(self, widget, startPos, endPos, clearOnFocusOut=True):
        if isinstance(widget, QTextEdit) or isinstance(widget, QPlainTextEdit):
            self._highlightTextEditSearchResult(widget, startPos, endPos, clearOnFocusOut)
        elif isinstance(widget, QLineEdit):
            self._highlightLineEditSearchResult(widget, startPos, endPos, clearOnFocusOut)
        elif isinstance(widget, QTableView):
            self._highlightTableViewSearchResult(widget, startPos, clearOnFocusOut)
        elif isinstance(widget, QListView):
            self._highlightListViewSearchResult(widget, startPos, clearOnFocusOut)
        elif isinstance(widget, QLabel):
            self._highlightLabelSearchResult(widget, clearOnFocusOut)
        else:
            raise NotImplementedError

        widget.setFocus(True)

    @staticmethod
    def generateClearHandler(widget, clearCallback):
        """
        Generates a clear handler to be run when the given widget loses focus.

        :param widget: widget we want to attach the handler to
        :param clearCallback: callback to be called when the given widget loses focus.
        :return:
        """
        def clearHandler(_widget, previous_on_focus_out_event):
            clearCallback(_widget)
            _widget.focusOutEvent = previous_on_focus_out_event

        widget.focusOutEvent = lambda e: clearHandler(widget, widget.focusOutEvent)

    def _highlightTextEditSearchResult(self, textEdit, startPos, endPos, clearOnFocusOut):
        # On focus out, clear text edit selection.
        oldTextCursor = textEdit.textCursor()
        if clearOnFocusOut:
            self.generateClearHandler(textEdit, lambda widget: widget.setTextCursor(oldTextCursor))

        # Highlight search result on the text edit.
        c = textEdit.textCursor()
        c.setPosition(startPos)
        c.setPosition(endPos, QTextCursor.KeepAnchor)
        textEdit.setTextCursor(c)

    def _highlightLineEditSearchResult(self, lineEdit, startPos, endPos, clearOnFocusOut):
        # On focus out, clear line edit selection.
        if clearOnFocusOut:
            self.generateClearHandler(lineEdit, lambda widget: widget.deselect())

        # Highlight search result on line edit.
        lineEdit.setCursorPosition(startPos)
        lineEdit.cursorForward(True, endPos - startPos)

    def _highlightTableViewSearchResult(self, tableView, startPos, clearOnFocusOut):
        # On focus out, clear table selection.
        if clearOnFocusOut:
            self.generateClearHandler(tableView, lambda widget: widget.clearSelection())

        # Highlight table row containing search result.
        tableView.selectRow(startPos)

    def _highlightListViewSearchResult(self, listView, startPos, clearOnFocusOut):
        # On focus out, clear table selection.
        if clearOnFocusOut:
            self.generateClearHandler(listView, lambda widget: widget.selectionModel().clearSelection())

        # Highlight list item containing search result.
        listView.setCurrentIndex(listView.model().index(startPos, 0, listView.rootIndex()))

    def _highlightLabelSearchResult(self, label, clearOnFocusOut):
        # On focus out, clear label selection.
        # FIXME: This would overwrite all styles!
        oldStyle = label.styleSheet()
        if clearOnFocusOut:
            self.generateClearHandler(label, lambda widget: widget.setStyleSheet(oldStyle))

        # Highlight search result on label.
        label.setStyleSheet("background-color: steelblue")
