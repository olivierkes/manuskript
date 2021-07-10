#!/usr/bin/env python
# --!-- coding: utf8 --!--
import re, textwrap

from PyQt5.Qt import QApplication
from PyQt5.QtCore import QTimer, QModelIndex, Qt, QEvent, pyqtSignal, QRegExp, QLocale, QPersistentModelIndex, QMutex
from PyQt5.QtGui import QTextBlockFormat, QTextCharFormat, QFont, QColor, QIcon, QMouseEvent, QTextCursor
from PyQt5.QtWidgets import QWidget, QTextEdit, qApp, QAction, QMenu, QToolTip

from manuskript import settings
from manuskript.enums import Outline, World, Character, Plot
from manuskript import functions as F
from manuskript.models import outlineModel, outlineItem
from manuskript.ui.highlighters import BasicHighlighter
from manuskript.ui import style as S
from manuskript.functions import Spellchecker
from manuskript.models.characterModel import Character, CharacterInfo


import logging
LOGGER = logging.getLogger(__name__)

# See implementation of QTextDocument::toPlainText()
PLAIN_TRANSLATION_TABLE = {0x2028: "\n", 0x2029: "\n", 0xfdd0: "\n", 0xfdd1: "\n"}

class textEditView(QTextEdit):

    def __init__(self, parent=None, index=None, html=None, spellcheck=None,
                 highlighting=False, dict="", autoResize=False):
        QTextEdit.__init__(self, parent)
        self._column = Outline.text
        self._index = None
        self._indexes = None
        self._model = None
        self._placeholderText = self.placeholderText()
        self._updating = QMutex()
        self._item = None
        self._highlighting = highlighting
        self._textFormat = "text"
        self.setAcceptRichText(False)
        # When setting up a theme, this becomes true.
        self._fromTheme = False
        self._themeData = None
        self._highlighterClass = BasicHighlighter

        if spellcheck == None:
            spellcheck = settings.spellcheck

        self.spellcheck = spellcheck
        self.currentDict = dict if dict else settings.dict
        self._defaultFontSize = qApp.font().pointSize()
        self.highlighter = None
        self.setAutoResize(autoResize)
        self._defaultBlockFormat = QTextBlockFormat()
        self._defaultCharFormat = QTextCharFormat()
        self.highlightWord = ""
        self.highligtCS = False
        self._dict = None
        self._tooltip = { 'depth' : 0, 'active' : 0 }

        # self.document().contentsChanged.connect(self.submit, F.AUC)

        # Submit text changed only after 500ms without modifications
        self.updateTimer = QTimer()
        self.updateTimer.setInterval(500)
        self.updateTimer.setSingleShot(True)
        self.updateTimer.timeout.connect(self.submit)
        # self.updateTimer.timeout.connect(lambda: LOGGER.debug("Timeout."))

        self.updateTimer.stop()
        self.document().contentsChanged.connect(self.updateTimer.start, F.AUC)
        # self.document().contentsChanged.connect(lambda: LOGGER.debug("Document changed."))

        # self.document().contentsChanged.connect(lambda: LOGGER.debug("Contents changed: %s", self.objectName()))

        self.setEnabled(False)

        if index:
            self.setCurrentModelIndex(index)

        elif html:
            self.document().setHtml(html)
            self.setReadOnly(True)

        # Spellchecking
        if self.spellcheck:
            self._dict = Spellchecker.getDictionary(self.currentDict)

        if not self._dict:
            self.spellcheck = False

        if self._highlighting and not self.highlighter:
            self.highlighter = self._highlighterClass(self)
            self.highlighter.setDefaultBlockFormat(self._defaultBlockFormat)

    def setModel(self, model):
        self._model = model
        try:
            self._model.dataChanged.connect(self.update, F.AUC)
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
            self._index = QPersistentModelIndex(index)

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

    def currentIndex(self):
        """
        Getter function used to normalized views access with QAbstractItemViews.
        """
        if self._index:
            return self._index
        else:
            return QModelIndex()

    def getSelection(self):
        """
        Getter function used to normalized views access with QAbstractItemViews.
        """
        return [self.currentIndex()]

    def setCurrentModelIndexes(self, indexes):
        self._index = None
        self._indexes = []

        for i in indexes:
            if i.isValid():
                self.setEnabled(True)
                if i.column() != self._column:
                    i = i.sibling(i.row(), self._column)
                self._indexes.append(QModelIndex(i))

                if not self._model:
                    self.setModel(i.model())

        self.updateText()

    def setupEditorForIndex(self, index):
        # Setting highlighter
        if self._highlighting:
            self.highlighter = self._highlighterClass(self)
            self.highlighter.setDefaultBlockFormat(self._defaultBlockFormat)
            self.highlighter.updateColorScheme()

    def loadFontSettings(self):
        if self._fromTheme or \
            not self._index or \
                type(self._index.model()) != outlineModel or \
                self._column != Outline.text:
            return

        opt = settings.textEditor
        f = QFont()
        f.fromString(opt["font"])
        background = (opt["background"] if not opt["backgroundTransparent"]
                      else "transparent")
        foreground = opt["fontColor"]  # if not opt["backgroundTransparent"]
        #                               else S.text
        # self.setFont(f)
        self.setStyleSheet("""QTextEdit{{
            background: {bg};
            color: {foreground};
            font-family: {ff};
            font-size: {fs};
            margin: {mTB}px {mLR}px;
            {maxWidth}
            }}
            """.format(
            bg=background,
            foreground=foreground,
            ff=f.family(),
            fs="{}pt".format(str(f.pointSize())),
            mTB=opt["marginsTB"],
            mLR=opt["marginsLR"],
            maxWidth="max-width: {}px;".format(
                opt["maxWidth"]) if opt["maxWidth"] else "",
        )
        )
        self._defaultFontSize = f.pointSize()

        # We set the parent background to the editor's background in case
        # there are margins. We check that the parent class is a QWidget because
        # if textEditView is used in fullScreenEditor, then we don't want to
        # set the background.
        if self.parent().__class__ == QWidget:
            self.parent().setStyleSheet("""
                QWidget#{name}{{
                    background: {bg};
                }}""".format(
                # We style by name, otherwise all inheriting widgets get the same
                # colored background, for example context menu.
                name=self.parent().objectName(),
                bg=background,
            ))

        cf = QTextCharFormat()
        # cf.setFont(f)
        # cf.setForeground(QColor(opt["fontColor"]))

        self.setCursorWidth(opt["cursorWidth"])

        bf = QTextBlockFormat()
        bf.setLineHeight(opt["lineSpacing"], bf.ProportionalHeight)
        bf.setTextIndent(opt["tabWidth"] * 1 if opt["indent"] else 0)
        bf.setTopMargin(opt["spacingAbove"])
        bf.setBottomMargin(opt["spacingBelow"])
        bf.setAlignment(Qt.AlignLeft if opt["textAlignment"] == 0 else
                        Qt.AlignCenter if opt["textAlignment"] == 1 else
                        Qt.AlignRight if opt["textAlignment"] == 2 else
                        Qt.AlignJustify)

        self._defaultCharFormat = cf
        self._defaultBlockFormat = bf

        if self.highlighter:
            self.highlighter.updateColorScheme()
            self.highlighter.setMisspelledColor(QColor(opt["misspelled"]))
            self.highlighter.setDefaultCharFormat(self._defaultCharFormat)
            self.highlighter.setDefaultBlockFormat(self._defaultBlockFormat)

    def update(self, topLeft, bottomRight):
        update = False

        if self._index and self._index.isValid():
            if topLeft.parent() != self._index.parent():
                return

                # LOGGER.debug("Model changed: ({}:{}), ({}:{}/{}), ({}:{}) for {} of {}".format(
                # topLeft.row(), topLeft.column(),
                # self._index.row(), self._index.row(), self._column,
                # bottomRight.row(), bottomRight.column(),
                # self.objectName(), self.parent().objectName()))

            if topLeft.row() <= self._index.row() <= bottomRight.row():
                if topLeft.column() <= self._column <= bottomRight.column():
                    update = True

        elif self._indexes:
            for i in self._indexes:
                if topLeft.row() <= i.row() <= bottomRight.row():
                    update = True

        if update:
            self.updateText()

    def disconnectDocument(self):
        try:
            self.document().contentsChanged.disconnect(self.updateTimer.start)
        except:
            pass

    def reconnectDocument(self):
        self.document().contentsChanged.connect(self.updateTimer.start, F.AUC)

    def toIdealText(self):
        """QTextDocument::toPlainText() replaces NBSP with spaces, which we don't want.
        QTextDocument::toRawText() replaces nothing, but that leaves fancy paragraph and line separators that users would likely complain about.
        This reimplements toPlainText(), except without the NBSP destruction."""
        return self.document().toRawText().translate(PLAIN_TRANSLATION_TABLE)
    toPlainText = toIdealText

    def updateText(self):
        self._updating.lock()

        # LOGGER.debug("Updating %s", self.objectName())
        if self._index:
            self.disconnectDocument()
            if self.toIdealText() != F.toString(self._index.data()):
                # LOGGER.debug("    Updating plaintext")
                self.document().setPlainText(F.toString(self._index.data()))
            self.reconnectDocument()

        elif self._indexes:
            self.disconnectDocument()
            t = []
            same = True
            for i in self._indexes:
                item = i.internalPointer()
                t.append(F.toString(item.data(self._column)))

            for t2 in t[1:]:
                if t2 != t[0]:
                    same = False
                    break

            if same:
                self.document().setPlainText(t[0])
            else:
                self.document().setPlainText("")

                if not self._placeholderText:
                    self._placeholderText = self.placeholderText()

                self.setPlaceholderText(self.tr("Various"))
            self.reconnectDocument()

        self._updating.unlock()

    def submit(self):
        self.updateTimer.stop()

        self._updating.lock()
        text = self.toIdealText()
        self._updating.unlock()

        # LOGGER.debug("Submitting %s", self.objectName())
        if self._index and self._index.isValid():
            # item = self._index.internalPointer()
            if text != self._index.data():
                # LOGGER.debug("    Submitting plain text")
                self._model.setData(QModelIndex(self._index), text)

        elif self._indexes:
            for i in self._indexes:
                item = i.internalPointer()
                if text != F.toString(item.data(self._column)):
                    LOGGER.debug("Submitting many indexes")
                    self._model.setData(i, text)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_V and event.modifiers() & Qt.ControlModifier:
            text = QApplication.clipboard().text()
            self.insertPlainText(text)
        else:
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
        opt = settings.textEditor
        docHeight = self.document().size().height() + 2 * opt["marginsTB"]
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
        if d:
            self._dict = Spellchecker.getDictionary(d)
        if self.highlighter:
            self.highlighter.rehighlight()

    def toggleSpellcheck(self, v):
        self.spellcheck = v
        if self.spellcheck and not self._dict:
            self._dict = Spellchecker.getDictionary(self.currentDict)

        if not self._dict:
            self.spellcheck = False

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

    def beginTooltipMoveEvent(self):
        self._tooltip['depth'] += 1

    def endTooltipMoveEvent(self):
        self._tooltip['depth'] -= 1

    def showTooltip(self, pos, text):
        QToolTip.showText(pos, text)
        self._tooltip['active'] = self._tooltip['depth']

    def hideTooltip(self):
        if self._tooltip['active'] == self._tooltip['depth']:
            QToolTip.hideText()

    def mouseMoveEvent(self, event):
        """
        When mouse moves, we show tooltip when appropriate.
        """
        self.beginTooltipMoveEvent()
        QTextEdit.mouseMoveEvent(self, event)
        self.endTooltipMoveEvent()

        match = None

        # Check if the selected word has any suggestions for correction
        if self.spellcheck and self._dict:
            cursor = self.cursorForPosition(event.pos())

            # Searches for correlating/overlapping matches
            suggestions = self._dict.findSuggestions(self.toPlainText(), cursor.selectionStart(), cursor.selectionEnd())

            if len(suggestions) > 0:
                # I think it should focus on one type of error at a time.
                match = suggestions[0]

        if match:
            # Wrap the message into a fitting width
            msg_lines = textwrap.wrap(match.msg, 48)

            self.showTooltip(event.globalPos(), "\n".join(msg_lines))
        else:
            self.hideTooltip()

    def wheelEvent(self, event):
        """
        We catch wheelEvent if key modifier is CTRL to change font size.
        Note: this should be in a class specific for main textEditView (#TODO).
        """
        if event.modifiers() & Qt.ControlModifier:
            # Get the wheel angle.
            d = event.angleDelta().y() / 120

            # Update settings
            f = QFont()
            f.fromString(settings.textEditor["font"])
            f.setPointSizeF(f.pointSizeF() + d)
            settings.textEditor["font"] = f.toString()

            # Update font to all textEditView. Drastically.
            for w in F.mainWindow().findChildren(textEditView, QRegExp(".*")):
                w.loadFontSettings()

            # We tell the world that we accepted this event
            event.accept()
            return

        QTextEdit.wheelEvent(self, event)

    class SpellAction(QAction):
        """A special QAction that returns the text in a signal. Used for spellcheck."""

        correct = pyqtSignal(str)

        def __init__(self, *args):
            QAction.__init__(self, *args)

            self.triggered.connect(lambda x: self.correct.emit(
                str(self.text())))

    def contextMenuEvent(self, event):
        # Based on http://john.nachtimwald.com/2009/08/22/qplaintextedit-with-in-line-spell-check/
        popup_menu = self.createStandardContextMenu()
        popup_menu.exec_(event.globalPos())

    def newCharacter(self):
        text = self.sender().data()
        LOGGER.debug(f'New character: {text}')
        # switch to character page
        mw = F.mainWindow()
        mw.tabMain.setCurrentIndex(mw.TabPersos)
        # add character
        c = mw.mdlCharacter.addCharacter(name=text)
        # switch to character
        item = mw.lstCharacters.getItemByID(c.ID())
        mw.lstCharacters.setCurrentItem(item)

    def newPlotItem(self):
        text = self.sender().data()
        LOGGER.debug(f'New plot item: {text}')
        # switch to plot page
        mw = F.mainWindow()
        mw.tabMain.setCurrentIndex(mw.TabPlots)
        # add character
        p, ID = mw.mdlPlots.addPlot(text)
        # switch to character
        plotIndex = mw.mdlPlots.getIndexFromID(ID.text())
        # segfaults for some reason
        # mw.lstSubPlots.setCurrentIndex(plotIndex)

    def newWorldItem(self):
        text = self.sender().data()
        LOGGER.debug(f'New world item: {text}')
        mw = F.mainWindow()
        mw.tabMain.setCurrentIndex(mw.TabWorld)
        item = mw.mdlWorld.addItem(title=text)
        mw.treeWorld.setCurrentIndex(
            mw.mdlWorld.indexFromItem(item))


    def appendContextMenuEntriesForWord(self, popup_menu, selectedWord):
        # add "new <something>" buttons at end
        if selectedWord != None:
            # new character
            charAction = QAction(self.tr("&New Character"), popup_menu)
            charAction.setIcon(F.themeIcon("characters"))
            charAction.triggered.connect(self.newCharacter)
            charAction.setData(selectedWord)
            popup_menu.insertAction(None, charAction)

            # new plot item
            plotAction = QAction(self.tr("&New Plot Item"), popup_menu)
            plotAction.setIcon(F.themeIcon("plots"))
            plotAction.triggered.connect(self.newPlotItem)
            plotAction.setData(selectedWord)
            popup_menu.insertAction(None, plotAction)

            # new world item
            worldAction = QAction(self.tr("&New World Item"), popup_menu)
            worldAction.setIcon(F.themeIcon("world"))
            worldAction.triggered.connect(self.newWorldItem)
            worldAction.setData(selectedWord)
            popup_menu.insertAction(None, worldAction)

        return popup_menu

    def createStandardContextMenu(self):
        popup_menu = QTextEdit.createStandardContextMenu(self)

        cursor = self.textCursor()
        selectedWord = cursor.selectedText() if cursor.hasSelection() else None

        if not self.spellcheck:
            return self.appendContextMenuEntriesForWord(popup_menu, selectedWord)

        suggestions = []

        # Check for any suggestions for corrections at the cursors position
        if self._dict != None:
            text = self.toPlainText()

            suggestions = self._dict.findSuggestions(text, cursor.selectionStart(), cursor.selectionEnd())

            # Select the word under the cursor if necessary.
            # But only if there is no selection (otherwise it's impossible to select more text to copy/cut)
            if not cursor.hasSelection() and len(suggestions) == 0:
                old_position = cursor.position()

                cursor.select(QTextCursor.WordUnderCursor)
                self.setTextCursor(cursor)

                if cursor.hasSelection():
                    selectedWord = cursor.selectedText()

                    # Check if the selected word is misspelled and offer spelling
                    # suggestions if it is.
                    suggestions = self._dict.findSuggestions(text, cursor.selectionStart(), cursor.selectionEnd())

                if len(suggestions) == 0:
                    cursor.clearSelection()
                    cursor.setPosition(old_position, QTextCursor.MoveAnchor)
                    self.setTextCursor(cursor)

                    selectedWord = None

        popup_menu = self.appendContextMenuEntriesForWord(popup_menu, selectedWord)

        if len(suggestions) > 0 or selectedWord != None:
            valid = len(suggestions) == 0

            if not valid:
                # I think it should focus on one type of error at a time.
                match = suggestions[0]

                popup_menu.insertSeparator(popup_menu.actions()[0])

                if match.locqualityissuetype == 'misspelling':
                    spell_menu = QMenu(self.tr('Spelling Suggestions'), self)
                    spell_menu.setIcon(F.themeIcon("spelling"))

                    if (match.end > match.start and selectedWord == None):
                        # Select the actual area of the match
                        cursor = self.textCursor()
                        cursor.setPosition(match.start, QTextCursor.MoveAnchor);
                        cursor.setPosition(match.end, QTextCursor.KeepAnchor);
                        self.setTextCursor(cursor)

                        selectedWord = cursor.selectedText()

                    for word in match.replacements:
                        action = self.SpellAction(word, spell_menu)
                        action.correct.connect(self.correctWord)
                        spell_menu.addAction(action)

                    # Adds: add to dictionary
                    addAction = QAction(self.tr("&Add to dictionary"), popup_menu)
                    addAction.setIcon(QIcon.fromTheme("list-add"))
                    addAction.triggered.connect(self.addWordToDict)
                    addAction.setData(selectedWord)

                    popup_menu.insertAction(popup_menu.actions()[0], addAction)

                    # Only add the spelling suggests to the menu if there are
                    # suggestions.
                    if len(match.replacements) > 0:
                        # Adds: suggestions
                        popup_menu.insertMenu(popup_menu.actions()[0], spell_menu)
                else:
                    correct_menu = None
                    correct_action = None

                    if (len(match.replacements) > 0 and match.end > match.start):
                        # Select the actual area of the match
                        cursor = self.textCursor()
                        cursor.setPosition(match.start, QTextCursor.MoveAnchor);
                        cursor.setPosition(match.end, QTextCursor.KeepAnchor);
                        self.setTextCursor(cursor)

                        if len(match.replacements) > 0:
                            correct_menu = QMenu(self.tr('&Correction Suggestions'), self)
                            correct_menu.setIcon(F.themeIcon("spelling"))

                            for word in match.replacements:
                                action = self.SpellAction(word, correct_menu)
                                action.correct.connect(self.correctWord)
                                correct_menu.addAction(action)

                    if correct_menu == None:
                        correct_action = QAction(self.tr('&Correction Suggestion'), popup_menu)
                        correct_action.setIcon(F.themeIcon("spelling"))
                        correct_action.setEnabled(False)

                    # Wrap the message into a fitting width
                    msg_lines = textwrap.wrap(match.msg, 48)

                    # Insert the lines of the message backwards
                    for i in range(0, len(msg_lines)):
                        popup_menu.insertSection(popup_menu.actions()[0], msg_lines[len(msg_lines) - (i + 1)])

                    if correct_menu != None:
                        popup_menu.insertMenu(popup_menu.actions()[0], correct_menu)
                    else:
                        popup_menu.insertAction(popup_menu.actions()[0], correct_action)

            # If word was added to custom dict, give the possibility to remove it
            elif self._dict.isCustomWord(selectedWord):
                popup_menu.insertSeparator(popup_menu.actions()[0])
                # Adds: remove from dictionary
                rmAction = QAction(
                    self.tr("&Remove from custom dictionary"), popup_menu)
                rmAction.setIcon(QIcon.fromTheme("list-remove"))
                rmAction.triggered.connect(self.rmWordFromDict)
                rmAction.setData(selectedWord)
                popup_menu.insertAction(popup_menu.actions()[0], rmAction)

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

    def addWordToDict(self):
        word = self.sender().data()
        self._dict.addWord(word)
        self.highlighter.rehighlight()

    def rmWordFromDict(self):
        word = self.sender().data()
        self._dict.removeWord(word)
        self.highlighter.rehighlight()

    ###############################################################################
    # FORMATTING
    ###############################################################################

    def focusOutEvent(self, event):
        """Submit changes just before focusing out."""
        QTextEdit.focusOutEvent(self, event)
        self.submit()

    ###############################################################################
    # KEYBOARD SHORTCUTS
    ###############################################################################

    def callMainTreeView(self, functionName):
        """
        The tree view in main window must have same index as the text
        edit that has focus. So we can pass it the call for documents
        edits like: duplicate, move up, etc.
        """
        if self._index and self._column == Outline.text:
            function = getattr(F.mainWindow().treeRedacOutline, functionName)
            function()

    def rename(self): self.callMainTreeView("rename")
    def duplicate(self): self.callMainTreeView("duplicate")
    def moveUp(self): self.callMainTreeView("moveUp")
    def moveDown(self): self.callMainTreeView("moveDown")
