#!/usr/bin/python
# -*- coding: utf8 -*-


# TODO: creates a general way to generate styles (and edit/import/export)
from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QFont, QTextBlockFormat, QColor, QFontMetrics, QTextCharFormat
from PyQt5.QtWidgets import qApp

from manuskript.ui.editors.blockUserData import blockUserData
from manuskript.ui.editors.t2tFunctions import State


class t2tHighlighterStyle():
    """Style for the Syntax highlighter for the Txt2Tags language.
    """

    validStyles = ["Default", "Monospace"]

    def __init__(self, editor, charFormat, name="Default"):

        self.editor = editor
        self.name = name
        self._defaultCharFormat = charFormat

        # Defaults
        # self.defaultFontPointSize = self.editor.defaultFontPointSize
        self.defaultFontFamily = qApp.font().family()
        self.tabStopWidth = 40

        self.setupEditor()

        if self.name == "Default":
            self.initDefaults()
        # Temporary other theme
        elif self.name == "Monospace":
            self.defaultFontFamily = "Monospace"
            self.initDefaults()
            for i in self.styles:
                f = self.styles[i]
                f.setFontFixedPitch(True)
                f.setFontFamily(self.defaultFontFamily)
                f.setFontPointSize(self._defaultCharFormat.font().pointSize())
            self.styles[i] = f

    def setupEditor(self):
        self.editor.setTabStopWidth(self.tabStopWidth)

    def initDefaults(self):
        self.styles = {}
        for i in [State.CODE_AREA,
                  State.CODE_LINE,
                  State.COMMENT_AREA,
                  State.COMMENT_LINE,
                  State.SETTINGS_LINE,
                  State.BLOCKQUOTE_LINE,
                  State.RAW_AREA,
                  State.RAW_LINE,
                  State.TAGGED_AREA,
                  State.TAGGED_LINE,
                  State.TITLE_1,
                  State.TITLE_2,
                  State.TITLE_3,
                  State.TITLE_4,
                  State.TITLE_5,
                  State.NUMBERED_TITLE_1,
                  State.NUMBERED_TITLE_2,
                  State.NUMBERED_TITLE_3,
                  State.NUMBERED_TITLE_4,
                  State.NUMBERED_TITLE_5,
                  State.TABLE_HEADER,
                  State.TABLE_LINE,
                  State.HORIZONTAL_LINE,
                  State.MARKUP,
                  State.LIST_BULLET,
                  State.LIST_BULLET_ENDS,
                  State.LINKS,
                  State.MACRO,
                  State.DEFAULT,
                  State.HEADER_LINE]:
            self.styles[i] = self.makeFormat(preset=i)

    def format(self, state):
        return self.styles[state]

    def beautifyFormat(self, base, beautifiers):
        """Apply beautifiers given in beautifiers array to format"""
        if max(beautifiers) == 2:
            return self.makeFormat(preset=State.MARKUP, base=base)
        else:
            if beautifiers[0]:  # bold
                base.setFontWeight(QFont.Bold)
            if beautifiers[1]:  # italic
                base.setFontItalic(True)
            if beautifiers[2]:  # underline
                base.setFontUnderline(True)
            if beautifiers[3]:  # strikeout
                base.setFontStrikeOut(True)
            if beautifiers[4]:  # code
                base = self.makeFormat(base=base, preset=State.CODE_LINE)
            if beautifiers[5]:  # tagged
                base = self.makeFormat(base=base, preset=State.TAGGED_LINE)
            return base

    def formatBlock(self, block, state):
        """Apply transformation to given block."""
        blockFormat = QTextBlockFormat()

        if state == State.BLOCKQUOTE_LINE:
            # Number of tabs
            n = block.text().indexOf(QRegExp(r'[^\t]'), 0)
            blockFormat.setIndent(0)
            blockFormat.setTextIndent(-self.tabStopWidth * n)
            blockFormat.setLeftMargin(self.tabStopWidth * n)
            # blockFormat.setRightMargin(self.editor.contentsRect().width()
            # - self.editor.lineNumberAreaWidth()
            # - fm.width("X") * self.editor.LimitLine
            # + self.editor.tabStopWidth())
            blockFormat.setAlignment(Qt.AlignJustify)
            if self.name == "Default":
                blockFormat.setTopMargin(5)
                blockFormat.setBottomMargin(5)
        elif state == State.HEADER_LINE:
            blockFormat.setBackground(QColor("#EEEEEE"))
        elif state in State.LIST:
            data = blockUserData.getUserData(block)
            if str(data.listSymbol()) in "+-":
                blockFormat.setBackground(QColor("#EEFFEE"))
            else:
                blockFormat.setBackground(QColor("#EEEEFA"))
            n = blockUserData.getUserData(block).leadingSpaces() + 1

            f = QFontMetrics(QFont(self.defaultFontFamily,
                                   self._defaultCharFormat.font().pointSize()))
            fm = f.width(" " * n +
                         blockUserData.getUserData(block).listSymbol())
            blockFormat.setTextIndent(-fm)
            blockFormat.setLeftMargin(fm)
            if blockUserData.getUserState(block) == State.LIST_BEGINS and \
                            self.name == "Default":
                blockFormat.setTopMargin(5)
        return blockFormat

    def makeFormat(self, color='', style='', size='', base='', fixedPitch='',
                   preset='', title_level='', bgcolor=''):
        """
        Returns a QTextCharFormat with the given attributes, using presets.
        """

        _color = QColor()
        # _format = QTextCharFormat()
        # _format.setFont(self.editor.font())
        # size = _format.fontPointSize()
        _format = QTextCharFormat(self._defaultCharFormat)

        # Base
        if base:
            _format = base

        # Presets
        if preset in [State.CODE_AREA, State.CODE_LINE, "code"]:
            style = "bold"
            color = "black"
            fixedPitch = True
            _format.setBackground(QColor("#EEEEEE"))

        if preset in [State.COMMENT_AREA, State.COMMENT_LINE, "comment"]:
            style = "italic"
            color = "darkGreen"

        if preset in [State.SETTINGS_LINE, "setting", State.MACRO]:
            # style = "italic"
            color = "magenta"

        if preset in [State.BLOCKQUOTE_LINE]:
            color = "red"

        if preset in [State.HEADER_LINE]:
            size *= 2
            # print size

        if preset in [State.RAW_AREA, State.RAW_LINE, "raw"]:
            color = "blue"

        if preset in [State.TAGGED_AREA, State.TAGGED_LINE, "tagged"]:
            color = "purple"

        if preset in State.TITLES:
            style = "bold"
            color = "darkRed" if State.titleLevel(preset) % 2 == 1 else "blue"
            size = (self._defaultCharFormat.font().pointSize()
                    + 11 - 2 * State.titleLevel(preset))

        if preset == State.TABLE_HEADER:
            style = "bold"
            color = "darkMagenta"

        if preset == State.TABLE_LINE:
            color = "darkMagenta"

        if preset == State.LIST_BULLET:
            color = "red"
            style = "bold"
            fixedPitch = True

        if preset == State.LIST_BULLET_ENDS:
            color = "darkGray"
            fixedPitch = True

        if preset in [State.MARKUP, "markup"]:
            color = "darkGray"

        if preset in [State.HORIZONTAL_LINE]:
            color = "cyan"
            fixedPitch = True

        if preset == State.LINKS:
            color = "blue"
            # style="underline"

        if preset == "selected":
            _format.setBackground(QColor("yellow"))

        if preset == "higlighted":
            bgcolor = "yellow"

            # if preset == State.DEFAULT:
            # size = self.defaultFontPointSize
            # _format.setFontFamily(self.defaultFontFamily)

        # Manual formatting
        if color:
            _color.setNamedColor(color)
            _format.setForeground(_color)
        if bgcolor:
            _color.setNamedColor(bgcolor)
            _format.setBackground(_color)

        if 'bold' in style:
            _format.setFontWeight(QFont.Bold)
        if 'italic' in style:
            _format.setFontItalic(True)
        if 'strike' in style:
            _format.setFontStrikeOut(True)
        if 'underline' in style:
            _format.setFontUnderline(True)
        if size:
            _format.setFontPointSize(size)
        if fixedPitch:
            _format.setFontFixedPitch(True)

        return _format
