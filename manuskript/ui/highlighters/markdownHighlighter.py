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

from manuskript.ui.highlighters.markdownTokenizer import MarkdownTokenizer
from manuskript.ui.highlighters.markdownEnums import MarkdownState as MS
from manuskript.ui.highlighters.markdownEnums import MarkdownTokenType as MTT
from manuskript.ui.highlighters.markdownEnums import BlockquoteStyle as BS

# Un longue ligne. Un longue ligne. Un longue ligne. Un longue ligne.asdasdasda

GW_FADE_ALPHA = 140

# Highlighter based on GhostWriter (http://wereturtle.github.io/ghostwriter/).
# GPLV3+.

#FIXME: Setext heading don't work anymore

class MarkdownHighlighter(QSyntaxHighlighter):

    highlightBlockAtPosition = pyqtSignal(int)
    headingFound = pyqtSignal(int, str, QTextBlock)
    headingRemoved = pyqtSignal(int)

    def __init__(self, editor):
        QSyntaxHighlighter.__init__(self, editor.document())

        #default values
        self.editor = editor
        self.tokenizer = MarkdownTokenizer()

        self.spellCheckEnabled = False
        #self.typingPaused = True
        self.inBlockquote = False
        self.defaultTextColor = QColor(Qt.black)
        self.backgroundColor = QColor(Qt.white)
        self.markupColor = QColor(Qt.black)
        self.linkColor = QColor(Qt.blue)
        self.spellingErrorColor = QColor(Qt.red)
        self.blockquoteStyle = BS.BlockquoteStyleFancy

        # Settings
        self.useUndlerlineForEmphasis = False
        self.highlightLineBreaks = True

        self.highlightBlockAtPosition.connect(self.onHighlightBlockAtPosition,
                                              Qt.QueuedConnection)

        # font = QFont("Monospace", 12, QFont.Normal, False)
        font = self.document().defaultFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        self.defaultFormat = QTextCharFormat()
        self.defaultFormat.setFont(font)
        self.defaultFormat.setForeground(QBrush(self.defaultTextColor))

        self.theme = self.defaultTheme()
        self.setupHeadingFontSize(True)

        self.highlightedWords = []
        self.highlightedTags = []
        self.searchExpression = ""
        self.searchExpressionRegExp = False
        self.searchExpressionCase = False

        self.customRules = [
            ("(°).*?(°)", {"background": Qt.yellow,
                           "markupColor":Qt.lightGray}),
            ]

        #f = self.document().defaultFont()
        #f.setFamily("monospace")
        #self.document().setDefaultFont(f)

    def highlightBlock(self, text):
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

        if self.currentBlock().blockNumber() == 0:
            # This is the title
            bf = QTextCharFormat()
            bf.setFontPointSize(self.editor.font().pointSize() * 2)
            bf.setFontWeight(QFont.Bold)
            bf.setForeground(Qt.lightGray)
            self.setFormat(0, len(text), bf)
            return

        lastState = self.currentBlockState()
        self.setFormat(0, len(text), self.defaultFormat)

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
                #fmt = QTextCharFormat(self.defaultFormat)
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

        # HASHTAGS AND HIGHLIGHTS

        # Hashtags
        s = 0
        ht = QRegExp(r'([^#])(#[\w]+)')
        while ht.indexIn(text, s) >= 0:
            f = self.format(ht.pos()+1)
            f.setForeground(QColor("#07c"))
            f.setFontWeight(QFont.Bold)
            self.setFormat(ht.pos()+1, ht.matchedLength()-1, f)
            s = ht.pos() + 1

        # Highlighted
        for w in self.highlightedWords + self.highlightedTags:
            pos = text.lower().find(w.lower())
            while pos >= 0:
                for i in range(pos, pos + len(w)):
                    f = self.format(i)
                    f.setBackground(QBrush(QColor("#fAf")))
                    self.setFormat(i, 1, f)
                pos = text.lower().find(w.lower(), pos+1)

        # Searched
        #FIXME: consider searchExpressionRegExp
        if self.searchExpression:
            s = self.searchExpression

            if not self.searchExpressionRegExp:
                if self.searchExpressionCase:
                    pos = text.find(s)
                else:
                    pos = text.lower().find(s.lower())
                while pos >= 0:
                    for i in range(pos, pos + len(s)):
                        f = self.format(i)
                        f.setBackground(QBrush(QColor("#Aff")))
                        self.setFormat(i, 1, f)
                    pos = text.lower().find(s.lower(), pos+1)

            else:
                # Using QRegExp
                rx = QRegExp(s)
                if not self.searchExpressionCase:
                    rx.setCaseSensitivity(Qt.CaseInsensitive)
                p = rx.indexIn(text)
                while p != -1:
                    f = self.format(p)
                    f.setBackground(QBrush(QColor("#Aff")))
                    self.setFormat(p, rx.matchedLength(), f)
                    p = rx.indexIn(text, p + 1)

                # Using python re
                #try:
                    #for m in re.finditer(s, text):
                        #f = self.format(m.start())
                        #f.setBackground(QBrush(QColor("#0ff")))
                        #self.setFormat(m.start(), len(m.group()), f)
                #except:
                    ## Probably malformed regExp
                    #pass

        # Custom rules
        for rule, theme in self.customRules:
            for m in re.finditer(rule, text):

                if not m.groups():  # No groups, therefore no markup
                    f = self.format(m.start())
                    f, garbage = self.formatsFromTheme(theme, f)
                    self.setFormat(m.start(), len(m.group()), f)

                else:
                    mf = self.format(m.start())
                    f = self.format(m.start() + len(m.group(1)))
                    f, mf = self.formatsFromTheme(theme, f, mf)
                    self.setFormat(m.start(1), len(m.group(1)), mf)
                    self.setFormat(m.start(2), len(m.group(2)), mf)
                    self.setFormat(m.start(1) + len(m.group(1)),
                                   len(m.group())
                                   - len(m.group(1))
                                   - len(m.group(2)), f)

        # If the block has transitioned from previously being a heading to now
        # being a non-heading, signal that the position in the document no
        # longer contains a heading.

        if self.isHeadingBlockState(lastState) and \
           not self.isHeadingBlockState(self.currentBlockState()):
            self.headingRemoved.emit(self.currentBlock().position())


    ###########################################################################
    # COLORS & FORMATTING
    ###########################################################################

    def defaultTheme(self):

        markup = qApp.palette().color(QPalette.Mid)
        if markup == Qt.black:
            markup = Qt.lightGray
        dark = qApp.palette().color(QPalette.Dark)
        if dark == Qt.black:
            dark = QColor(Qt.gray)
        darker = dark.darker(150)

        # Text background
        background = qApp.palette().color(QPalette.Base)
        lightBackground = background.darker(130)
        veryLightBackground = background.darker(105)

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
                "monospace": True,
                #"color": Qt.darkBlue if i % 2 == 1 else Qt.darkMagenta,
            }
        b = 100
        d = 50
        color = QColor(Qt.darkBlue)
        theme[MTT.TokenAtxHeading1]["color"] = color
        theme[MTT.TokenAtxHeading2]["color"] = color.lighter(b + d)
        theme[MTT.TokenAtxHeading3]["color"] = color.lighter(b + 2*d)
        theme[MTT.TokenAtxHeading4]["color"] = color.lighter(b + 3*d)
        theme[MTT.TokenAtxHeading5]["color"] = color.lighter(b + 4*d)
        theme[MTT.TokenAtxHeading6]["color"] = color.lighter(b + 5*d)

        for i in [MTT.TokenSetextHeading1Line2, MTT.TokenSetextHeading2Line2]:
            theme[i] = {
                "color": markup,
                "monospace":True}

        # Beautifiers
        theme[MTT.TokenEmphasis] = {
                "italic":True,}
        theme[MTT.TokenStrong] = {
            "bold":True}
        theme[MTT.TokenStrikethrough] = {
            "strike":True}
        theme[MTT.TokenVerbatim] = {
            "monospace":True,
            "background": veryLightBackground,
            "formatMarkup": True,
            "markupColor": markup}
        theme[MTT.TokenSuperScript] = {
            "super":True,
            "formatMarkup":True}
        theme[MTT.TokenSubScript] = {
            "sub":True,
            "formatMarkup":True}

        theme[MTT.TokenHtmlTag] = {
            "color":Qt.red}
        theme[MTT.TokenHtmlEntity] = {
            "color":Qt.red}
        theme[MTT.TokenAutomaticLink] = {
            "color": qApp.palette().color(QPalette.Link)}
        theme[MTT.TokenInlineLink] = {
            "color": qApp.palette().color(QPalette.Link)}
        theme[MTT.TokenReferenceLink] = {
            "color": qApp.palette().color(QPalette.Link)}
        theme[MTT.TokenReferenceDefinition] = {
            "color": qApp.palette().color(QPalette.Link)}
        theme[MTT.TokenImage] = {
            "color": Qt.green}
        theme[MTT.TokenHtmlComment] = {
            "color": dark}
        theme[MTT.TokenNumberedList] = {
            "markupColor": QColor(Qt.red).lighter(),
            "markupBold": True,
            "markupMonospace": True,}
        theme[MTT.TokenBulletPointList] = {
            "markupColor": QColor(Qt.red).lighter(),
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
            "color": darker,
            "markupColor": lightBackground,
            "markupBackground": lightBackground}
        theme[MTT.TokenCodeBlock] = {
            "color": darker,
            "markupBackground": veryLightBackground,
            "monospace":True}
        theme[MTT.TokenGithubCodeFence] = {
            "color": markup}
        theme[MTT.TokenPandocCodeFence] = {
            "color": markup}
        theme[MTT.TokenCodeFenceEnd] = {
            "color": markup}
        theme[MTT.TokenMention] = {} # FIXME
        theme[MTT.TokenTableHeader] = {
            "color": darker, "monospace":True}
        theme[MTT.TokenTableDivider] = {
            "color": markup, "monospace":True}
        theme[MTT.TokenTablePipe] = {
            "color": markup, "monospace":True}

        return theme

    def setColorScheme(self, defaultTextColor, backgroundColor, markupColor,
                       linkColor, spellingErrorColor):
        self.defaultTextColor = defaultTextColor
        self.backgroundColor = backgroundColor
        self.markupColor = markupColor
        self.linkColor = linkColor
        self.spellingErrorColor = spellingErrorColor
        self.defaultFormat.setForeground(QBrush(defaultTextColor))

        # FIXME: generate a theme based on that
        self.rehighlight()

    ###########################################################################
    # ACTUAL FORMATTING
    ###########################################################################

    def applyFormattingForToken(self, token, text):
        if token.type != MTT.TokenUnknown:
            format = self.format(token.position + token.openingMarkupLength)
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

            #if token.type in range(6, 10):
            #debug()

            theme = self.theme.get(token.type)
            if theme:
                format, markupFormat = self.formatsFromTheme(theme,
                                                             format,
                                                             markupFormat)

            # Format openning Markup
            self.setFormat(token.position, token.openingMarkupLength,
                           markupFormat)

            # Format Text
            self.setFormat(
                token.position + token.openingMarkupLength,
                token.length - token.openingMarkupLength - token.closingMarkupLength,
                format)

            # Format closing Markup
            if token.closingMarkupLength > 0:
                self.setFormat(
                    token.position + token.length - token.closingMarkupLength,
                    token.closingMarkupLength,
                    markupFormat)

        else:
            qWarning("MarkdownHighlighter.applyFormattingForToken() was passed"
                     " in a token of unknown type.")

    def formatsFromTheme(self, theme, format=QTextCharFormat(),
                         markupFormat=QTextCharFormat()):
        # Token
        if theme.get("color"):
            format.setForeground(theme["color"])
        if theme.get("deltaSize"):
            format.setFontPointSize(format.fontPointSize() + theme["deltaSize"])
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
        self.defaultFormat.setFontPointSize(self.defaultFormat.fontPointSize()
                                            + 1.0)
        self.rehighlight()

    def decreaseFontSize(self):
        self.defaultFormat.setFontPointSize(self.defaultFormat.fontPointSize()
                                            - 1.0)
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
        font = QFont(family=fontFamily, pointSize=fontSize, weight=QFont.Normal, italic=False)
        self.defaultFormat.setFont(font)
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
