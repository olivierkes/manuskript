#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
A QSyntaxHighlighter for markdown, using tokenizer. More accurate than simple
regexp, but not yet perfect.
"""

import re
from PyQt5.QtCore import Qt, pyqtSignal, qWarning, QRegExp
from PyQt5.QtGui import (QSyntaxHighlighter, QTextBlock, QColor, QFont,
                         QTextCharFormat, QBrush, QPalette)
from PyQt5.QtWidgets import qApp, QStyle

from manuskript.ui.highlighters import BasicHighlighter
from manuskript.ui.highlighters import MarkdownTokenizer
from manuskript.ui.highlighters import MarkdownState as MS
from manuskript.ui.highlighters import MarkdownTokenType as MTT
from manuskript.ui.highlighters import BlockquoteStyle as BS
from manuskript.ui import style as S
from manuskript import settings
from manuskript import functions as F

# Un longue ligne. Un longue ligne. Un longue ligne. Un longue ligne.asdasdasda

GW_FADE_ALPHA = 140

# Highlighter based on GhostWriter (http://wereturtle.github.io/ghostwriter/).
# GPLV3+.

#FIXME: Setext heading don't work anymore

class MarkdownHighlighter(BasicHighlighter):

    highlightBlockAtPosition = pyqtSignal(int)
    headingFound = pyqtSignal(int, str, QTextBlock)
    headingRemoved = pyqtSignal(int)

    def __init__(self, editor):
        BasicHighlighter.__init__(self, editor)

        #default values
        self.editor = editor
        self.tokenizer = MarkdownTokenizer()

        self.spellCheckEnabled = False
        #self.typingPaused = True
        self.inBlockquote = False
        self.blockquoteStyle = BS.BlockquoteStyleFancy

        # Settings
        self.useUndlerlineForEmphasis = False
        self.highlightLineBreaks = True

        self.highlightBlockAtPosition.connect(self.onHighlightBlockAtPosition,
                                              Qt.QueuedConnection)

        self.theme = self.defaultTheme()
        self.setupHeadingFontSize(True)

        self.highlightedWords = []
        self.highlightedTags = []
        self.searchExpression = ""
        self.searchExpressionRegExp = False
        self.searchExpressionCase = False

        #f = self.document().defaultFont()
        #f.setFamily("monospace")
        #self.document().setDefaultFont(f)

    def transparentFormat(self, fmt, alpha=75):
        """
        Takes a QTextCharFormat and modify it with colors made transparent
        using alpha channel. For focus mode
        """
        c = fmt.foreground().color()
        c.setAlpha(alpha)
        fmt.setForeground(QBrush(c))
        b = fmt.background()
        if b.style() != Qt.NoBrush:
            c = b.color()
            c.setAlpha(alpha)
            fmt.setBackground(QBrush(b))

    def unfocusConditions(self):
        """
        Returns:
        - True if the text is suposed to be unfocused
        - (start, end) if block is supposed to be unfocused except for that part.
        """

        if self.editor._noFocusMode or not settings.textEditor["focusMode"]:
            return False

        if settings.textEditor["focusMode"] == "paragraph":
            return not self.currentBlock().contains(
                self.editor.textCursor().position())

        elif settings.textEditor["focusMode"] == "line":
            if self.currentBlock().contains(
                    self.editor.textCursor().position()):
                block = self.currentBlock()
                # Position of cursor in block
                pos = self.editor.textCursor().position() - block.position()
                for i in range(block.layout().lineCount()):
                    line = block.layout().lineAt(i)
                    start = line.textStart()
                    end = line.textStart() + line.textLength()
                    if start <= pos <= end:
                        return (start, end)
            else:
                return True

        elif settings.textEditor["focusMode"] == "sentence":
            if self.currentBlock().contains(
                    self.editor.textCursor().position()):
                block = self.currentBlock()
                # Position of cursor in block
                pos = self.editor.textCursor().position() - block.position()
                ENDChars = "!.?"
                txt = block.text()
                start = -1
                for i in range(len(txt)):
                    if start == -1: start = i
                    if txt[i] in ENDChars:
                        s = txt[start:i+1]
                        if start <= pos <= start + len(s):
                            return start, i+1
                        start = -1
                return (start, len(txt))

            else:
                return True

        return False

    def doHighlightBlock(self, text):
        """
        Note:  Never set the QTextBlockFormat for a QTextBlock from within
        the highlighter. Depending on how the block format is modified,
        a recursive call to the highlighter may be triggered, which will
        cause the application to crash.

        Likewise, don't try to set the QTextBlockFormat outside the highlighter
        (i.e., from within the text editor).  While the application will not
        crash, the format change will be added to the undo stack.  Attempting
        to undo from that point on will cause the undo stack to be virtually
        frozen, since undoing the format operation causes the text to be
        considered changed, thus triggering the slot that changes the text
        formatting to be triggered yet again.
        """

        lastState = self.currentBlockState()
        # self.setFormat(0, len(text), self._defaultCharFormat)

        # Focus mode
        unfocus = self.unfocusConditions()
        if unfocus:
            fmt = self.format(0)
            fmt.setForeground(QBrush(self.defaultTextColor))
            self.transparentFormat(fmt)
            if type(unfocus) != bool:
                start, end = unfocus
                self.setFormat(0, start, fmt)
                self.setFormat(end, len(text), fmt)
            else:
                self.setFormat(0, len(text), fmt)

        if self.tokenizer != None:
            self.tokenizer.clear()
            block = self.currentBlock()
            nextState = MS.MarkdownStateUnknown
            previousState = self.previousBlockState()

            if block.next().isValid():
                nextState = block.next().userState()

            self.tokenizer.tokenize(text, lastState, previousState, nextState)
            self.setCurrentBlockState(self.tokenizer.getState())

            self.inBlockquote = self.tokenizer.getState() == MS.MarkdownStateBlockquote

            # STATE FORMATTING
            # FIXME: generic
            if self.currentBlockState() in [
                    MS.MarkdownStatePipeTableHeader,
                    MS.MarkdownStatePipeTableDivider,
                    MS.MarkdownStatePipeTableRow]:
                fmt = QTextCharFormat()
                f = fmt.font()
                f.setFamily("Monospace")
                fmt.setFont(f)
                self.setFormat(0, len(text), fmt)

            # Monospace the blank chars
            i = 0
            while i <= len(text)-1 and text[i] in [" ", "\t"]:
                fmt = self.format(i)
                fmt.setFontFamily("Monospace")
                self.setFormat(i, 1, fmt)
                i += 1

            #if self.currentBlockState() == MS.MarkdownStateBlockquote:
                #fmt = QTextCharFormat(self._defaultCharFormat)
                #fmt.setForeground(Qt.lightGray)
                #self.setFormat(0, len(text), fmt)

            tokens = self.tokenizer.getTokens()

            for token in tokens:
                if token.type == MTT.TokenUnknown:
                    qWarning("Highlighter found unknown token type in text block.")
                    continue

                if token.type in [
                        MTT.TokenAtxHeading1,
                        MTT.TokenAtxHeading2,
                        MTT.TokenAtxHeading3,
                        MTT.TokenAtxHeading4,
                        MTT.TokenAtxHeading5,
                        MTT.TokenAtxHeading6,
                        MTT.TokenSetextHeading1Line1,
                        MTT.TokenSetextHeading2Line1,
                    ]:
                    self.storeHeadingData(token, text)

                self.applyFormattingForToken(token, text)

            if self.tokenizer.backtrackRequested():
                previous = self.currentBlock().previous()
                self.highlightBlockAtPosition.emit(previous.position())

        if self.spellCheckEnabled:
            self.spellCheck(text)

        # If the block has transitioned from previously being a heading to now
        # being a non-heading, signal that the position in the document no
        # longer contains a heading.

        if self.isHeadingBlockState(lastState) and \
           not self.isHeadingBlockState(self.currentBlockState()):
            self.headingRemoved.emit(self.currentBlock().position())


    ###########################################################################
    # COLORS & FORMATTING
    ###########################################################################

    def updateColorScheme(self, rehighlight=True):
        BasicHighlighter.updateColorScheme(self, rehighlight)
        self.theme = self.defaultTheme()
        self.setEnableLargeHeadingSizes(True)

    def defaultTheme(self):

        # Base Colors
        background = self.backgroundColor
        text = self.defaultTextColor
        highlightedText = QColor(S.highlightedText)
        highlightedTextDark = QColor(S.highlightedTextDark)
        highlightedTextLight = QColor(S.highlightedTextLight)
        highlight = QColor(S.highlight)
        link = self.linkColor
        linkVisited = QColor(S.linkVisited)

        # titleColor = highlight
        titleColor = QColor(S.highlightedTextDark)

        # FullscreenEditor probably
        if self.editor._fromTheme and self.editor._themeData:
            text = QColor(self.editor._themeData["Text/Color"])
            background =  QColor(self.editor._themeData["Background/Color"])
            titleColor = text

        # Compositions
        light = F.mixColors(text, background, .75)
        markup = F.mixColors(text, background, .5)
        veryLight = F.mixColors(text, background, .25)
        listToken = F.mixColors(highlight, background, .4)
        titleMarkupColor = F.mixColors(titleColor, background, .3)


        theme = {
            "markup": markup}

        #Exemple:
            #"color": Qt.red,
            #"deltaSize": 10,
            #"background": Qt.yellow,
            #"monospace": True,
            #"bold": True,
            #"italic": True,
            #"underline": True,
            #"overline": True,
            #"strike": True,
            #"formatMarkup": True,
            #"markupBold": True,
            #"markupColor": Qt.blue,
            #"markupBackground": Qt.green,
            #"markupMonospace": True,
            #"super":True,
            #"sub":True

        for i in MTT.TITLES:
            theme[i] = {
                "formatMarkup":True,
                "bold": True,
                # "monospace": True,
                "markupColor": titleMarkupColor
            }

        theme[MTT.TokenAtxHeading1]["color"] = titleColor
        theme[MTT.TokenAtxHeading2]["color"] = F.mixColors(titleColor,
                                                           background, .9)
        theme[MTT.TokenAtxHeading3]["color"] = F.mixColors(titleColor,
                                                           background, .8)
        theme[MTT.TokenAtxHeading4]["color"] = F.mixColors(titleColor,
                                                           background, .7)
        theme[MTT.TokenAtxHeading5]["color"] = F.mixColors(titleColor,
                                                           background, .6)
        theme[MTT.TokenAtxHeading6]["color"] = F.mixColors(titleColor,
                                                           background, .5)

        theme[MTT.TokenSetextHeading1Line1]["color"] = titleColor
        theme[MTT.TokenSetextHeading2Line1]["color"] = F.mixColors(titleColor,
                                                                   background,
                                                                   .9)

        for i in [MTT.TokenSetextHeading1Line1, MTT.TokenSetextHeading2Line1]:
            theme[i]["monospace"] = True

        for i in [MTT.TokenSetextHeading1Line2, MTT.TokenSetextHeading2Line2]:
            theme[i] = {
                "color": titleMarkupColor,
                "monospace":True}

        # Beautifiers
        theme[MTT.TokenEmphasis] = {
            "italic":True}
        theme[MTT.TokenStrong] = {
            "bold":True}
        theme[MTT.TokenStrikethrough] = {
            "strike":True}
        theme[MTT.TokenVerbatim] = {
            "monospace":True,
            "background": veryLight,
            "formatMarkup": True,
            "markupColor": markup,
            "deltaSize": -1}
        theme[MTT.TokenSuperScript] = {
            "super":True,
            "formatMarkup":True}
        theme[MTT.TokenSubScript] = {
            "sub":True,
            "formatMarkup":True}
        theme[MTT.TokenHtmlTag] = {
            "color": linkVisited}
        theme[MTT.TokenHtmlEntity] = {  # &nbsp;
            "color": linkVisited}
        theme[MTT.TokenAutomaticLink] = {
            "color": link}
        theme[MTT.TokenInlineLink] = {
            "color": link}
        theme[MTT.TokenReferenceLink] = {
            "color": link}
        theme[MTT.TokenReferenceDefinition] = {
            "color": link}
        theme[MTT.TokenImage] = {
            "color": highlightedTextDark}
        theme[MTT.TokenHtmlComment] = {
            "color": markup}
        theme[MTT.TokenNumberedList] = {
            "markupColor": listToken,
            "markupBold": True,
            "markupMonospace": True,}
        theme[MTT.TokenBulletPointList] = {
            "markupColor": listToken,
            "markupBold": True,
            "markupMonospace": True,}
        theme[MTT.TokenHorizontalRule] = {
            "overline": True,
            "underline": True,
            "monospace": True,
            "color": markup}
        theme[MTT.TokenLineBreak] = {
            "background": markup}
        theme[MTT.TokenBlockquote] = {
            "color": light,
            "markupColor": veryLight,
            "markupBackground": veryLight}
        theme[MTT.TokenCodeBlock] = {
            "color": light,
            "markupBackground": veryLight,
            "formatMarkup": True,
            "monospace":True,
            "deltaSize":-1}
        theme[MTT.TokenGithubCodeFence] = {
            "color": markup}
        theme[MTT.TokenPandocCodeFence] = {
            "color": markup}
        theme[MTT.TokenCodeFenceEnd] = {
            "color": markup}
        theme[MTT.TokenMention] = {} # FIXME
        theme[MTT.TokenTableHeader] = {
            "color": light, "monospace":True}
        theme[MTT.TokenTableDivider] = {
            "color": markup, "monospace":True}
        theme[MTT.TokenTablePipe] = {
            "color": markup, "monospace":True}

        # CriticMarkup
        theme[MTT.TokenCMAddition] = {
            "color": QColor("#00bb00"),
            "markupColor": QColor(F.mixColors("#00bb00", background, .4)),
            "markupMonospace": True,}
        theme[MTT.TokenCMDeletion] = {
            "color": QColor("#dd0000"),
            "markupColor": QColor(F.mixColors("#dd0000", background, .4)),
            "markupMonospace": True,
            "strike": True}
        theme[MTT.TokenCMSubstitution] = {
            "color": QColor("#ff8600"),
            "markupColor": QColor(F.mixColors("#ff8600", background, .4)),
            "markupMonospace": True,}
        theme[MTT.TokenCMComment] = {
            "color": QColor("#0000bb"),
            "markupColor": QColor(F.mixColors("#0000bb", background, .4)),
            "markupMonospace": True,}
        theme[MTT.TokenCMHighlight] = {
            "color": QColor("#aa53a9"),
            "background": QColor(F.mixColors("#aa53a9", background, .1)),
            "markupBackground": QColor(F.mixColors("#aa53a9", background, .1)),
            "markupColor": QColor(F.mixColors("#aa53a9", background, .5)),
            "markupMonospace": True,}

        return theme

    ###########################################################################
    # ACTUAL FORMATTING
    ###########################################################################

    def applyFormattingForToken(self, token, text):
        if token.type != MTT.TokenUnknown:
            fmt = self.format(token.position + token.openingMarkupLength)
            markupFormat = self.format(token.position)
            if self.theme.get("markup"):
                markupFormat.setForeground(self.theme["markup"])

            ## Debug
            def debug():
                print("{}\n{}{}{}{}   (state:{})".format(
                    text,
                    " "*token.position,
                    "^"*token.openingMarkupLength,
                    str(token.type).center(token.length
                                           - token.openingMarkupLength
                                           - token.closingMarkupLength, "-"),
                    "^" * token.closingMarkupLength,
                    self.currentBlockState(),)
                     )

            # if token.type in range(6, 10):
            # debug()

            theme = self.theme.get(token.type)
            if theme:
                fmt, markupFormat = self.formatsFromTheme(theme,
                                                          fmt,
                                                          markupFormat)

            # Focus mode
            unfocus = self.unfocusConditions()
            if unfocus:
                if (type(unfocus) == bool
                        or token.position < unfocus[0]
                        or unfocus[1] < token.position):
                    self.transparentFormat(fmt)
                    self.transparentFormat(markupFormat)

            # Format openning Markup
            self.setFormat(token.position, token.openingMarkupLength,
                           markupFormat)

            # Format Text
            self.setFormat(
                token.position + token.openingMarkupLength,
                token.length - token.openingMarkupLength - token.closingMarkupLength,
                fmt)

            # Format closing Markup
            if token.closingMarkupLength > 0:
                self.setFormat(
                    token.position + token.length - token.closingMarkupLength,
                    token.closingMarkupLength,
                    markupFormat)

        else:
            qWarning("MarkdownHighlighter.applyFormattingForToken() was passed"
                     " in a token of unknown type.")

    def formatsFromTheme(self, theme, format=None,
                         markupFormat=QTextCharFormat()):
        # Token
        if theme.get("color"):
            format.setForeground(theme["color"])
        if theme.get("deltaSize"):
            size = self.editor._defaultFontSize + theme["deltaSize"]
            if size >= 0:
                f = format.font()
                f.setPointSize(size)
                format.setFont(f)
        if theme.get("background"):
            format.setBackground(theme["background"])
        if theme.get("monospace"):
            format.setFontFamily("Monospace")
        if theme.get("bold"):
            format.setFontWeight(QFont.Bold)
        if theme.get("italic"):
            format.setFontItalic(theme["italic"])
        if theme.get("underline"):
            format.setFontUnderline(theme["underline"])
        if theme.get("overline"):
            format.setFontOverline(theme["overline"])
        if theme.get("strike"):
            format.setFontStrikeOut(theme["strike"])
        if theme.get("super"):
            format.setVerticalAlignment(QTextCharFormat.AlignSuperScript)
        if theme.get("sub"):
            format.setVerticalAlignment(QTextCharFormat.AlignSubScript)

        # Markup
        if theme.get("formatMarkup"):
            c = markupFormat.foreground()
            markupFormat = QTextCharFormat(format)
            markupFormat.setForeground(c)
        if theme.get("markupBold"):
            markupFormat.setFontWeight(QFont.Bold)
        if theme.get("markupColor"):
            markupFormat.setForeground(theme["markupColor"])
        if theme.get("markupBackground"):
            markupFormat.setBackground(theme["markupBackground"])
        if theme.get("markupMonospace"):
            markupFormat.setFontFamily("Monospace")

        return format, markupFormat

    ###########################################################################
    # SETTINGS
    ###########################################################################

    def setHighlighted(self, words, tags):
        rehighlight = (self.highlightedWords != words
                       or self.highlightedTags != tags)
        self.highlightedWords = words
        self.highlightedTags = tags
        if rehighlight:
            self.rehighlight()

    def setSearched(self, expression, regExp=False, caseSensitivity=False):
        """
        Define an expression currently searched, to be highlighted.
        Can be regExp.
        """
        rehighlight = self.searchExpression != expression or \
                      self.searchExpressionRegExp != regExp or \
                      self.searchExpressionCase != caseSensitivity
        self.searchExpression = expression
        self.searchExpressionRegExp = regExp
        self.searchExpressionCase = caseSensitivity
        if rehighlight:
            self.rehighlight()

    def setDictionary(self, dictionary):
        self.dictionary = dictionary
        if self.spellCheckEnabled:
            self.rehighlight()

    def increaseFontSize(self):
        self._defaultCharFormat.setFontPointSize(
            self._defaultCharFormat.font().pointSize() + 1.0)
        self.rehighlight()

    def decreaseFontSize(self):
        self._defaultCharFormat.setFontPointSize(
            self._defaultCharFormat.font().pointSize() - 1.0)
        self.rehighlight()

    def setEnableLargeHeadingSizes(self, enable):
        self.setupHeadingFontSize(enable)
        self.rehighlight()

    def setupHeadingFontSize(self, useLargeHeadings):
        if useLargeHeadings:
            self.theme[MTT.TokenSetextHeading1Line1]["deltaSize"] = 7
            self.theme[MTT.TokenSetextHeading2Line1]["deltaSize"] = 5
            self.theme[MTT.TokenSetextHeading1Line2]["deltaSize"] = 7
            self.theme[MTT.TokenSetextHeading2Line2]["deltaSize"] = 5
            self.theme[MTT.TokenAtxHeading1]["deltaSize"] = 7
            self.theme[MTT.TokenAtxHeading2]["deltaSize"] = 5
            self.theme[MTT.TokenAtxHeading3]["deltaSize"] = 3
            self.theme[MTT.TokenAtxHeading4]["deltaSize"] = 2
            self.theme[MTT.TokenAtxHeading5]["deltaSize"] = 1
            self.theme[MTT.TokenAtxHeading6]["deltaSize"] = 0

        else:
            for i in MTT.TITLES:
                self.theme[i]["deltaSize"] = 0

    def setUseUnderlineForEmphasis(self, enable):
        self.useUndlerlineForEmphasis = enable
        self.rehighlight()

    def setFont(self, fontFamily, fontSize):
        font = QFont(family=fontFamily, pointSize=fontSize,
                     weight=QFont.Normal, italic=False)
        self._defaultCharFormat.setFont(font)
        self.rehighlight()

    def setSpellCheckEnabled(self, enabled):
        self.spellCheckEnabled = enabled
        self.rehighlight()

    def setBlockquoteStyle(self, style):
        self.blockquoteStyle = style

        if style == BS.BlockquoteStyleItalic:
            self.emphasizeToken[MTT.TokenBlockquote] = True
        else:
            self.emphasizeToken[MTT.TokenBlockquote] = False

        self.rehighlight()

    def setHighlightLineBreaks(self, enable):
        self.highlightLineBreaks = enable
        self.rehighlight()

    ###########################################################################
    # GHOSTWRITER SPECIFIC?
    ###########################################################################

    def onTypingResumed(self):
        self.typingPaused = False

    def onTypingPaused(self):
        self.typingPaused = True
        block = self.document().findBlock(self.editor.textCursor().position())
        self.rehighlightBlock(block)

    def onHighlightBlockAtPosition(self, position):
        block = self.document().findBlock(position)
        self.rehighlightBlock(block)

    def onTextBlockRemoved(self, block):
        if self.isHeadingBlockState(block.userState):
            self.headingRemoved.emit(block.position())

    ###########################################################################
    # SPELLCHECK
    ###########################################################################

    def spellCheck(self, text):
        cursorPosition = self.editor.textCursor().position()
        cursorPosBlock = self.document().findBlock(cursorPosition)
        cursorPosInBlock = -1

        if self.currentBlock() == cursorPosBlock:
            cursorPosInBlock = cursorPosition - cursorPosBlock.position()

        misspelledWord = self.dictionary.check(text, 0)

        while not misspelledWord.isNull():
            startIndex = misspelledWord.position()
            length = misspelledWord.length()

            if self.typingPaused or cursorPosInBlock != startIndex + length:
                spellingErrorFormat = self.format(startIndex)
                spellingErrorFormat.setUnderlineColor(self.spellingErrorColor)
                spellingErrorFormat.setUnderlineStyle(
                    qApp.stlye().styleHint(QStyle.SH_SpellCheckUnderlineStyle))

                self.setFormat(startIndex, length, spellingErrorFormat)

            startIndex += length
            misspelledWord = self.dictionary.check(text, startIndex)

    def storeHeadingData(self, token, text):
        if token.type in [
                MTT.TokenAtxHeading1,
                MTT.TokenAtxHeading2,
                MTT.TokenAtxHeading3,
                MTT.TokenAtxHeading4,
                MTT.TokenAtxHeading5,
                MTT.TokenAtxHeading6]:
            level = token.type - MTT.TokenAtxHeading1 + 1
            s = token.position + token.openingMarkupLength
            l = (token.length
                 - token.openingMarkupLength
                 - token.closingMarkupLength)
            headingText = text[s:s+l].strip()

        elif token.type == MTT.TokenSetextHeading1Line1:
            level = 1
            headingText = text

        elif token.type == MTT.TokenSetextHeading2Line1:
            level = 2
            headingText = text

        else:
            qWarning("MarkdownHighlighter.storeHeadingData() encountered" +
                     " unexpected token: {}".format(token.getType()))
            return

        # FIXME: TypeError: could not convert 'TextBlockData' to 'QTextBlockUserData'
        # blockData = self.currentBlockUserData()
        # if blockData is None:
        #     blockData = TextBlockData(self.document(), self.currentBlock())
        #
        # self.setCurrentBlockUserData(blockData)
        self.headingFound.emit(level, headingText, self.currentBlock())

    def isHeadingBlockState(self, state):
        return state in [
            MS.MarkdownStateAtxHeading1,
            MS.MarkdownStateAtxHeading2,
            MS.MarkdownStateAtxHeading3,
            MS.MarkdownStateAtxHeading4,
            MS.MarkdownStateAtxHeading5,
            MS.MarkdownStateAtxHeading6,
            MS.MarkdownStateSetextHeading1Line1,
            MS.MarkdownStateSetextHeading2Line1,]


def getLuminance(color):
    return (0.30 * color.redF()) + \
           (0.59 * color.greenF()) + \
           (0.11 * color.blueF())


def applyAlphaToChannel(foreground, background, alpha):
    return (foreground * alpha) + (background * (1.0 - alpha))


def applyAlpha(foreground, background, alpha):
    blendedColor = QColor(0, 0, 0)
    normalizedAlpha = alpha / 255.0
    blendedColor.setRed(applyAlphaToChannel(
        foreground.red(), background.red(), normalizedAlpha))
    blendedColor.setGreen(applyAlphaToChannel(
        foreground.green(), background.green(), normalizedAlpha))
    blendedColor.setBlue(applyAlphaToChannel(
        foreground.blue(), background.blue(), normalizedAlpha))
    return blendedColor
