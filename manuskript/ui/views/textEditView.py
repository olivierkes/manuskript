#!/usr/bin/env python
# --!-- coding: utf8 --!--
import re

from PyQt5.QtCore import QTimer, QModelIndex, Qt, QEvent, pyqtSignal, QRegExp
from PyQt5.QtGui import QTextBlockFormat, QTextCharFormat, QFont, QColor, QMouseEvent, QTextCursor
from PyQt5.QtWidgets import QTextEdit, qApp, QAction, QMenu

from manuskript import settings
from manuskript.enums import Outline
from manuskript.functions import AUC
from manuskript.functions import toString
from manuskript.models.outlineModel import outlineModel
from manuskript.ui.editors.MMDHighlighter import MMDHighlighter
from manuskript.ui.editors.basicHighlighter import basicHighlighter
from manuskript.ui.editors.t2tFunctions import t2tClearFormat
from manuskript.ui.editors.t2tFunctions import t2tFormatSelection
from manuskript.ui.editors.t2tHighlighter import t2tHighlighter
from manuskript.ui.editors.textFormat import textFormat

try:
    import enchant
except ImportError:
    enchant = None


class textEditView(QTextEdit):
    def __init__(self, parent=None, index=None, html=None, spellcheck=True, highlighting=False, dict="",
                 autoResize=False):
        QTextEdit.__init__(self, parent)
        self._column = Outline.text.value
        self._index = None
        self._indexes = None
        self._model = None
        self._placeholderText = self.placeholderText()
        self._updating = False
        self._item = None
        self._highlighting = highlighting
        self._textFormat = "text"
        self.setAcceptRichText(False)
        # When setting up a theme, this becomes true.
        self._fromTheme = False

        self.spellcheck = spellcheck
        self.currentDict = dict if dict else settings.dict
        self.highlighter = None
        self.setAutoResize(autoResize)
        self._defaultBlockFormat = QTextBlockFormat()
        self._defaultCharFormat = QTextCharFormat()
        self.highlightWord = ""
        self.highligtCS = False
        self.defaultFontPointSize = qApp.font().pointSize()
        self._dict = None
        # self.document().contentsChanged.connect(self.submit, AUC)

        # Submit text changed only after 500ms without modifications
        self.updateTimer = QTimer()
        self.updateTimer.setInterval(500)
        self.updateTimer.setSingleShot(True)
        self.updateTimer.timeout.connect(self.submit)
        # self.updateTimer.timeout.connect(lambda: print("Timeout"))

        self.updateTimer.stop()
        self.document().contentsChanged.connect(self.updateTimer.start, AUC)
        # self.document().contentsChanged.connect(lambda: print("Document changed"))

        # self.document().contentsChanged.connect(lambda: print(self.objectName(), "Contents changed"))

        self.setEnabled(False)

        if index:
            self.setCurrentModelIndex(index)

        elif html:
            self.document().setHtml(html)
            self.setReadOnly(True)

        # Spellchecking
        if enchant and self.spellcheck:
            self._dict = enchant.Dict(self.currentDict if self.currentDict else enchant.get_default_language())
        else:
            self.spellcheck = False

        if self._highlighting and not self.highlighter:
            self.highlighter = basicHighlighter(self)
            self.highlighter.setDefaultBlockFormat(self._defaultBlockFormat)

    def setModel(self, model):
        self._model = model
        try:
            self._model.dataChanged.connect(self.update, AUC)
        except TypeError:
            pass
        try:
            self._model.rowsAboutToBeRemoved.connect(self.rowsAboutToBeRemoved, AUC)
        except TypeError:
            pass

    def setColumn(self, col):
        self._column = col

    def setHighlighting(self, val):
        self._highlighting = val

    def setDefaultBlockFormat(self, bf):
        self._defaultBlockFormat = bf
        if self.highlighter:
            self.highlighter.setDefaultBlockFormat(bf)

    def setCurrentModelIndex(self, index):
        self._indexes = None
        if index.isValid():
            self.setEnabled(True)
            if index.column() != self._column:
                index = index.sibling(index.row(), self._column)
            self._index = index

            self.setPlaceholderText(self._placeholderText)

            if not self._model:
                self.setModel(index.model())

            self.setupEditorForIndex(self._index)
            self.loadFontSettings()
            self.updateText()

        else:
            self._index = QModelIndex()

            self.setPlainText("")
            self.setEnabled(False)

    def setCurrentModelIndexes(self, indexes):
        self._index = None
        self._indexes = []

        for i in indexes:
            if i.isValid():
                self.setEnabled(True)
                if i.column() != self._column:
                    i = i.sibling(i.row(), self._column)
                self._indexes.append(i)

                if not self._model:
                    self.setModel(i.model())

        self.updateText()

    def setupEditorForIndex(self, index):
        # what type of text are we editing?
        if type(index.model()) != outlineModel:
            self._textFormat = "text"
            return

        if self._column not in [Outline.text.value, Outline.notes.value]:
            self._textFormat = "text"

        else:
            item = index.internalPointer()
            if item.isHTML():
                self._textFormat = "html"
            elif item.isT2T():
                self._textFormat = "t2t"
            elif item.isMD():
                self._textFormat = "md"
            else:
                self._textFormat = "text"

        # Accept richtext maybe
        if self._textFormat == "html":
            self.setAcceptRichText(True)
        else:
            self.setAcceptRichText(False)

        # Setting highlighter
        if self._highlighting:
            item = index.internalPointer()
            if self._column == Outline.text.value and not (item.isT2T() or item.isMD()):
                self.highlighter = basicHighlighter(self)
            elif item.isT2T():
                self.highlighter = t2tHighlighter(self)
            elif item.isMD():
                self.highlighter = MMDHighlighter(self)

            self.highlighter.setDefaultBlockFormat(self._defaultBlockFormat)

    def loadFontSettings(self):
        if self._fromTheme or \
                not self._index or \
                    type(self._index.model()) != outlineModel or \
                    self._column != Outline.text.value:
            return

        opt = settings.textEditor
        f = QFont()
        f.fromString(opt["font"])
        # self.setFont(f)
        self.setStyleSheet("""
            background: {bg};
            color: {foreground};
            font-family: {ff};
            font-size: {fs};
            """.format(
                bg=opt["background"],
                foreground=opt["fontColor"],
                ff=f.family(),
                fs="{}pt".format(str(f.pointSize()))))

        cf = QTextCharFormat()
        # cf.setFont(f)
        # cf.setForeground(QColor(opt["fontColor"]))

        bf = QTextBlockFormat()
        bf.setLineHeight(opt["lineSpacing"], bf.ProportionalHeight)
        bf.setTextIndent(opt["tabWidth"] * 1 if opt["indent"] else 0)
        bf.setTopMargin(opt["spacingAbove"])
        bf.setBottomMargin(opt["spacingBelow"])

        self._defaultCharFormat = cf
        self._defaultBlockFormat = bf

        if self.highlighter:
            self.highlighter.setMisspelledColor(QColor(opt["misspelled"]))
            self.highlighter.setDefaultCharFormat(self._defaultCharFormat)
            self.highlighter.setDefaultBlockFormat(self._defaultBlockFormat)

    def update(self, topLeft, bottomRight):
        if self._updating:
            return

        elif self._index:

            if topLeft.parent() != self._index.parent():
                return

                # print("Model changed: ({}:{}), ({}:{}/{}), ({}:{}) for {} of {}".format(
                # topLeft.row(), topLeft.column(),
                # self._index.row(), self._index.row(), self._column,
                # bottomRight.row(), bottomRight.column(),
                # self.objectName(), self.parent().objectName()))

            if topLeft.row() <= self._index.row() <= bottomRight.row():
                if self._column == Outline.text.value and \
                                        topLeft.column() <= Outline.type.value <= bottomRight.column():
                    # If item type change, and we display the main text,
                    # we reset the index to set the proper
                    # highlighter and other defaults
                    self.setupEditorForIndex(self._index)
                    self.updateText()

                elif topLeft.column() <= self._column <= bottomRight.column():
                    self.updateText()

        elif self._indexes:
            update = False
            for i in self._indexes:
                if topLeft.row() <= i.row() <= bottomRight.row():
                    update = True
            if update:
                self.updateText()

    def rowsAboutToBeRemoved(self, parent, first, last):
        if self._index:
            if self._index.parent() == parent and \
                                    first <= self._index.row() <= last:
                self._index = None
                self.setEnabled(False)

                # FIXME: self._indexes

    def disconnectDocument(self):
        try:
            self.document().contentsChanged.disconnect(self.updateTimer.start)
        except:
            pass

    def reconnectDocument(self):
        self.document().contentsChanged.connect(self.updateTimer.start, AUC)

    def updateText(self):
        if self._updating:
            return
        # print("Updating", self.objectName())
        self._updating = True
        if self._index:
            self.disconnectDocument()
            if self._textFormat == "html":
                if self.toHtml() != toString(self._model.data(self._index)):
                    # print("    Updating html")
                    html = self._model.data(self._index)
                    self.document().setHtml(toString(html))
            else:
                if self.toPlainText() != toString(self._model.data(self._index)):
                    # print("    Updating plaintext")
                    self.document().setPlainText(toString(self._model.data(self._index)))
            self.reconnectDocument()

        elif self._indexes:
            self.disconnectDocument()
            t = []
            same = True
            for i in self._indexes:
                item = i.internalPointer()
                t.append(toString(item.data(self._column)))

            for t2 in t[1:]:
                if t2 != t[0]:
                    same = False
                    break

            if same:
                # Assuming that we don't use HTML with multiple items
                self.document().setPlainText(t[0])
            else:
                self.document().setPlainText("")

                if not self._placeholderText:
                    self._placeholderText = self.placeholderText()

                self.setPlaceholderText(self.tr("Various"))
            self.reconnectDocument()
        self._updating = False

    def submit(self):
        self.updateTimer.stop()
        if self._updating:
            return
        # print("Submitting", self.objectName())
        if self._index:
            # item = self._index.internalPointer()
            if self._textFormat == "html":
                if self.toHtml() != self._model.data(self._index):
                    # print("    Submitting html")
                    self._updating = True
                    html = self.toHtml()
                    # We don't store paragraph and font settings
                    html = re.sub(r"font-family:.*?;\s*", "", html)
                    html = re.sub(r"font-size:.*?;\s*", "", html)
                    html = re.sub(r"margin-.*?;\s*", "", html)
                    html = re.sub(r"text-indent:.*?;\s*", "", html)
                    html = re.sub(r"line-height:.*?;\s*", "", html)
                    # print("Submitting:", html)
                    self._model.setData(self._index, html)
                    self._updating = False
            else:
                if self.toPlainText() != self._model.data(self._index):
                    # print("    Submitting plain text")
                    self._updating = True
                    self._model.setData(self._index, self.toPlainText())
                    self._updating = False

        elif self._indexes:
            self._updating = True
            for i in self._indexes:
                item = i.internalPointer()
                if self.toPlainText() != toString(item.data(self._column)):
                    print("Submitting many indexes")
                    self._model.setData(i, self.toPlainText())
            self._updating = False

    def keyPressEvent(self, event):
        QTextEdit.keyPressEvent(self, event)
        if event.key() == Qt.Key_Space:
            self.submit()

    # -----------------------------------------------------------------------------------------------------
    # Resize stuff

    def resizeEvent(self, e):
        QTextEdit.resizeEvent(self, e)
        if self._autoResize:
            self.sizeChange()

    def sizeChange(self):
        docHeight = self.document().size().height()
        if self.heightMin <= docHeight <= self.heightMax:
            self.setMinimumHeight(docHeight)

    def setAutoResize(self, val):
        self._autoResize = val
        if self._autoResize:
            self.document().contentsChanged.connect(self.sizeChange)
            self.heightMin = 0
            self.heightMax = 65000
            self.sizeChange()

        ###############################################################################
        # SPELLCHECKING
        ###############################################################################
        # Based on http://john.nachtimwald.com/2009/08/22/qplaintextedit-with-in-line-spell-check/

    def setDict(self, d):
        self.currentDict = d
        self._dict = enchant.Dict(d)
        if self.highlighter:
            self.highlighter.rehighlight()

    def toggleSpellcheck(self, v):
        self.spellcheck = v
        if enchant and self.spellcheck and not self._dict:
            self._dict = enchant.Dict(self.currentDict if self.currentDict else enchant.get_default_language())
        if self.highlighter:
            self.highlighter.rehighlight()
        else:
            self.spellcheck = False

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            # Rewrite the mouse event to a left button event so the cursor is
            # moved to the location of the pointer.
            event = QMouseEvent(QEvent.MouseButtonPress, event.pos(),
                                Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        QTextEdit.mousePressEvent(self, event)

    class SpellAction(QAction):
        """A special QAction that returns the text in a signal. Used for spellckech."""

        correct = pyqtSignal(str)

        def __init__(self, *args):
            QAction.__init__(self, *args)

            self.triggered.connect(lambda x: self.correct.emit(
                    str(self.text())))

    def contextMenuEvent(self, event):
        # Based on http://john.nachtimwald.com/2009/08/22/qplaintextedit-with-in-line-spell-check/
        popup_menu = self.createStandardContextMenu()
        popup_menu.exec_(event.globalPos())

    def createStandardContextMenu(self):
        popup_menu = QTextEdit.createStandardContextMenu(self)

        if not self.spellcheck:
            return popup_menu

        # Select the word under the cursor.
        cursor = self.textCursor()
        # cursor = self.cursorForPosition(pos)
        cursor.select(QTextCursor.WordUnderCursor)
        self.setTextCursor(cursor)
        # Check if the selected word is misspelled and offer spelling
        # suggestions if it is.
        if cursor.hasSelection():
            text = str(cursor.selectedText())
            if not self._dict.check(text):
                spell_menu = QMenu(self.tr('Spelling Suggestions'), self)
                for word in self._dict.suggest(text):
                    action = self.SpellAction(word, spell_menu)
                    action.correct.connect(self.correctWord)
                    spell_menu.addAction(action)
                # Only add the spelling suggests to the menu if there are
                # suggestions.
                if len(spell_menu.actions()) != 0:
                    popup_menu.insertSeparator(popup_menu.actions()[0])
                    popup_menu.insertMenu(popup_menu.actions()[0], spell_menu)

        return popup_menu

    def correctWord(self, word):
        """
        Replaces the selected text with word.
        """
        cursor = self.textCursor()
        cursor.beginEditBlock()

        cursor.removeSelectedText()
        cursor.insertText(word)

        cursor.endEditBlock()

    ###############################################################################
    # FORMATTING
    ###############################################################################

    def focusOutEvent(self, event):
        """Submit changes just before focusing out."""
        QTextEdit.focusOutEvent(self, event)
        self.submit()

    def focusInEvent(self, event):
        """Finds textFormatter and attach them to that view."""
        QTextEdit.focusInEvent(self, event)

        p = self.parent()
        while p.parent():
            p = p.parent()

        if self._index:
            for tF in p.findChildren(textFormat, QRegExp(".*"), Qt.FindChildrenRecursively):
                tF.updateFromIndex(self._index)
                tF.setTextEdit(self)

    def applyFormat(self, _format):

        if self._textFormat == "html":

            if _format == "Clear":

                cursor = self.textCursor()

                if _format == "Clear":
                    fmt = self._defaultCharFormat
                    cursor.setCharFormat(fmt)
                    bf = self._defaultBlockFormat
                    cursor.setBlockFormat(bf)

            elif _format in ["Bold", "Italic", "Underline"]:

                cursor = self.textCursor()

                # If no selection, selects the word in which the cursor is now
                if not cursor.hasSelection():
                    cursor.movePosition(QTextCursor.StartOfWord,
                                        QTextCursor.MoveAnchor)
                    cursor.movePosition(QTextCursor.EndOfWord,
                                        QTextCursor.KeepAnchor)

                fmt = cursor.charFormat()

                if _format == "Bold":
                    fmt.setFontWeight(QFont.Bold if fmt.fontWeight() != QFont.Bold else QFont.Normal)
                elif _format == "Italic":
                    fmt.setFontItalic(not fmt.fontItalic())
                elif _format == "Underline":
                    fmt.setFontUnderline(not fmt.fontUnderline())

                fmt2 = self._defaultCharFormat
                fmt2.setFontWeight(fmt.fontWeight())
                fmt2.setFontItalic(fmt.fontItalic())
                fmt2.setFontUnderline(fmt.fontUnderline())

                cursor.mergeCharFormat(fmt2)

            elif _format in ["Left", "Center", "Right", "Justify"]:

                cursor = self.textCursor()

                # bf = cursor.blockFormat()
                bf = QTextBlockFormat()
                bf.setAlignment(
                        Qt.AlignLeft if _format == "Left" else
                        Qt.AlignHCenter if _format == "Center" else
                        Qt.AlignRight if _format == "Right" else
                        Qt.AlignJustify)

                cursor.setBlockFormat(bf)
                self.setTextCursor(cursor)

        elif self._textFormat == "t2t":
            if _format == "Bold":
                t2tFormatSelection(self, 0)
            elif _format == "Italic":
                t2tFormatSelection(self, 1)
            elif _format == "Underline":
                t2tFormatSelection(self, 2)
            elif _format == "Clear":
                t2tClearFormat(self)

        elif self._textFormat == "md":
            # FIXME
            print("Not implemented yet.")
