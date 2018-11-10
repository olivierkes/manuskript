#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from manuskript.ui.highlighters import MarkdownState as MS
from manuskript.ui.highlighters import MarkdownTokenType as MTT

# This file is simply a python translation of GhostWriter's Tokenizer.
# http://wereturtle.github.io/ghostwriter/
# GPLV3+.

# ==============================================================================
#   TOKEN
# ==============================================================================

class Token:
    def __init__(self):
        self.type = -1
        self.position = 0
        self.length = 0
        self.openingMarkupLength = 0
        self.closingMarkupLength = 0

# ==============================================================================
#   HIGHLIGHT TOKENIZER
# ==============================================================================

class HighlightTokenizer:
    def __init__(self):
        self.tokens = []

    def tokenize(text, currentState, previousState, nextState):
        # Subclass me
        return 0

    def getTokens(self):
        self.tokens = sorted(self.tokens, key=lambda t: t.position)
        return self.tokens

    def getState(self):
        return self.state

    def backtrackRequested(self):
        return self.backtrack

    def clear(self):
        self.tokens = []
        self.backtrack = False
        self.state = -1

    def addToken(self, token):
        self.tokens.append(token)

        if token.type == -1:
            print("Error here", token.position, token.length)

    def setState(self, state):
        self.state = state

    def requestBacktrack(self):
        self.backtrack = True

    def tokenLessThan(self, t1, t2):
        return t1.getPosition() < t2.getPosition()


class MarkdownTokenizer(HighlightTokenizer):

    DUMMY_CHAR = "$"
    MAX_MARKDOWN_HEADING_LEVEL = 6

    paragraphBreakRegex = QRegExp("^\\s*$")
    heading1SetextRegex = QRegExp("^===+\\s*$")
    heading2SetextRegex = QRegExp("^---+\\s*$")
    blockquoteRegex = QRegExp("^ {0,3}>.*$")
    githubCodeFenceStartRegex = QRegExp("^```+.*$")
    githubCodeFenceEndRegex = QRegExp("^```+\\s*$")
    pandocCodeFenceStartRegex = QRegExp("^~~~+.*$")
    pandocCodeFenceEndRegex = QRegExp("^~~~+\\s*$")
    numberedListRegex = QRegExp("^ {0,3}[0-9a-z]+[.)]\\s+.*$")
    numberedNestedListRegex = QRegExp("^\\s*[0-9a-z]+[.)]\\s+.*$")
    hruleRegex = QRegExp("\\s*(\\*\\s*){3,}|(\\s*(_\\s*){3,})|((\\s*(-\\s*){3,}))")
    lineBreakRegex = QRegExp(".*\\s{2,}$")
    emphasisRegex = QRegExp("(\\*(?![\\s*]).*[^\\s*]\\*)|_(?![\\s_]).*[^\\s_]_")
    emphasisRegex.setMinimal(True)
    strongRegex = QRegExp("\\*\\*(?=\\S).*\\S\\*\\*(?!\\*)|__(?=\\S).*\\S__(?!_)")
    strongRegex.setMinimal(True)
    strikethroughRegex = QRegExp("~~[^\\s]+.*[^\\s]+~~")
    strikethroughRegex.setMinimal(True)
    superScriptRegex = QRegExp(r"\^([^\s]|(\\\\\s))+\^")  # Spaces must be escaped "\ "
    superScriptRegex.setMinimal(True)
    subScriptRegex = QRegExp("~([^\\s]|(\\\\\\s))+~")  # Spaces must be escaped "\ "
    subScriptRegex.setMinimal(True)
    verbatimRegex = QRegExp("`+")
    htmlTagRegex = QRegExp("<[^<>]+>")
    htmlTagRegex.setMinimal(True)
    htmlEntityRegex = QRegExp("&[a-zA-Z]+;|&#x?[0-9]+;")
    automaticLinkRegex = QRegExp("(<([a-zA-Z]+\\:.+)>)|(<(.+@.+)>)")
    automaticLinkRegex.setMinimal(True)
    inlineLinkRegex = QRegExp("\\[(.+)\\]\\((.+)\\)")
    inlineLinkRegex.setMinimal(True)
    referenceLinkRegex = QRegExp("\\[(.+)\\]")
    referenceLinkRegex.setMinimal(True)
    referenceDefinitionRegex = QRegExp("^\\s*\\[.+\\]:")
    imageRegex = QRegExp("!\\[(.*)\\]\\((.+)\\)")
    imageRegex.setMinimal(True)
    htmlInlineCommentRegex = QRegExp("<!--.*-->")
    htmlInlineCommentRegex.setMinimal(True)
    mentionRegex = QRegExp("\\B@\\w+(\\-\\w+)*(/\\w+(\\-\\w+)*)?")
    pipeTableDividerRegex = QRegExp("^ {0,3}(\\|[ :]?)?-{3,}([ :]?\\|[ :]?-{3,}([ :]?\\|)?)+\\s*$")
    CMAdditionRegex = QRegExp("(\\{\\+\\+.*\\+\\+\\})")
    CMAdditionRegex.setMinimal(True)
    CMDeletionRegex = QRegExp("(\\{--.*--\\})")
    CMDeletionRegex.setMinimal(True)
    CMSubstitutionRegex = QRegExp("(\\{~~.*~>.*~~\\})")
    CMSubstitutionRegex.setMinimal(True)
    CMCommentRegex = QRegExp("(\\{>>.*<<\\})")
    CMCommentRegex.setMinimal(True)
    CMHighlightRegex = QRegExp("(\\{==.*==\\})")
    CMHighlightRegex.setMinimal(True)

    def __init__(self):
        HighlightTokenizer.__init__(self)

    def tokenize(self, text, currentState, previousState, nextState):
        self.currentState = currentState
        self.previousState = previousState
        self.nextState = nextState

        if (self.previousState == MS.MarkdownStateInGithubCodeFence or \
            self.previousState == MS.MarkdownStateInPandocCodeFence) and \
                self.tokenizeCodeBlock(text):
            # No further tokenizing required
            pass

        elif self.previousState != MS.MarkdownStateComment \
            and self.paragraphBreakRegex.exactMatch(text):

            if previousState in [MS.MarkdownStateListLineBreak,
                                 MS.MarkdownStateNumberedList,
                                 MS.MarkdownStateBulletPointList]:
                self.setState(MS.MarkdownStateListLineBreak)
            elif previousState != MS.MarkdownStateCodeBlock or \
                (text[:1] != "\t" and text[-4:] != "    "):
                self.setState(MS.MarkdownStateParagraphBreak)

        elif self.tokenizeSetextHeadingLine2(text) or \
             self.tokenizeCodeBlock(text) or \
             self.tokenizeMultilineComment(text) or \
             self.tokenizeHorizontalRule(text) or \
             self.tokenizeTableDivider(text):
            # No further tokenizing required
            pass

        elif self.tokenizeSetextHeadingLine1(text) or \
             self.tokenizeAtxHeading(text) or \
             self.tokenizeBlockquote(text) or \
             self.tokenizeNumberedList(text) or \
             self.tokenizeBulletPointList(text):
            self.tokenizeLineBreak(text)
            self.tokenizeInline(text)

        else:
            if previousState in [MS.MarkdownStateListLineBreak,
                                 MS.MarkdownStateNumberedList,
                                 MS.MarkdownStateNumberedList]:
                if not self.tokenizeNumberedList(text) and \
                   not self.tokenizeBulletPointList(text) and \
                   (text[:1] == "\t" or text[:4] == "    "):
                    self.setState(previousState)
                else:
                    self.setState(MS.MarkdownStateParagraph)
            else:
                self.setState(MS.MarkdownStateParagraph)
            self.tokenizeLineBreak(text)
            self.tokenizeInline(text)

        # Make sure that if the second line of a setext heading is removed the
        # first line is reprocessed.  Otherwise, it will still show up in the
        # document as a heading.
        if (previousState == MS.MarkdownStateSetextHeading1Line1 and \
           self.getState() != MS.MarkdownStateSetextHeading1Line2) or \
           (previousState == MS.MarkdownStateSetextHeading2Line1 and \
           self.getState() != MS.MarkdownStateSetextHeading2Line2):
            self.requestBacktrack()

    def tokenizeSetextHeadingLine1(self, text):
        #Check the next line's state to see if this is a setext-style heading.
        level = 0
        token = Token()
        nextState = self.nextState

        if MS.MarkdownStateSetextHeading1Line2 == nextState:
            level = 1
            self.setState(MS.MarkdownStateSetextHeading1Line1)
            token.type = MTT.TokenSetextHeading1Line1

        elif MS.MarkdownStateSetextHeading2Line2 == nextState:
            level = 2
            self.setState(MS.MarkdownStateSetextHeading2Line1)
            token.type = MTT.TokenSetextHeading2Line1

        if level > 0:
            token.length = len(text)
            token.position = 0
            self.addToken(token)
            return True

        return False

    def tokenizeSetextHeadingLine2(self, text):
        level = 0
        setextMatch = False
        token = Token()
        previousState = self.previousState
        if previousState == MS.MarkdownStateSetextHeading1Line1:
            level = 1
            setextMatch = self.heading1SetextRegex.exactMatch(text)
            self.setState(MS.MarkdownStateSetextHeading1Line2)
            token.type = MTT.TokenSetextHeading1Line2

        elif previousState == MS.MarkdownStateSetextHeading2Line1:
            level = 2
            setextMatch = self.heading2SetextRegex.exactMatch(text)
            self.setState(MS.MarkdownStateSetextHeading2Line2)
            token.type = MTT.TokenSetextHeading2Line2

        elif previousState == MS.MarkdownStateParagraph:
            h1Line2 = self.heading1SetextRegex.exactMatch(text)
            h2Line2 = self.heading2SetextRegex.exactMatch(text)

            if h1Line2 or h2Line2:
                # Restart tokenizing on the previous line.
                self.requestBacktrack()
                token.length = len(text)
                token.position = 0

                if h1Line2:
                    self.setState(MS.MarkdownStateSetextHeading1Line2)
                    token.type = MTT.TokenSetextHeading1Line2

                else:
                    self.setState(MS.MarkdownStateSetextHeading2Line2)
                    token.type = MTT.TokenSetextHeading2Line2

                self.addToken(token)
                return True

        if level > 0:
            if setextMatch:
                token.length = len(text)
                token.position = 0
                self.addToken(token)
                return True

            else:
                # Restart tokenizing on the previous line.
                self.requestBacktrack()
                return False

        return False

    def tokenizeAtxHeading(self, text):
        escapedText = self.dummyOutEscapeCharacters(text)
        trailingPoundCount = 0
        level = 0

        #Count the number of pound signs at the front of the string,
        #up to the maximum allowed, to determine the heading level.

        while escapedText[level] == "#":
            level += 1
            if level >= len(escapedText) or level >= self.MAX_MARKDOWN_HEADING_LEVEL:
                break

        if level > 0 and level < len(text):
            # Count how many pound signs are at the end of the text.
            while escapedText[-trailingPoundCount -1] == "#":
                trailingPoundCount += 1

            token = Token()
            token.position = 0
            token.length = len(text)
            token.type = MTT.TokenAtxHeading1 + level -1
            token.openingMarkupLength = level
            token.closingMarkupLength = trailingPoundCount
            self.addToken(token)
            self.setState(MS.MarkdownStateAtxHeading1 + level -1)
            return True
        return False

    def tokenizeNumberedList(self, text):
        previousState = self.previousState
        if (previousState in [MS.MarkdownStateParagraphBreak,
                             MS.MarkdownStateUnknown,
                             MS.MarkdownStateCodeBlock,
                             MS.MarkdownStateCodeFenceEnd,] and \
           self.numberedListRegex.exactMatch(text)) or \
           (previousState in [MS.MarkdownStateListLineBreak,
                             MS.MarkdownStateNumberedList,
                             MS.MarkdownStateBulletPointList,] and \
           self.numberedNestedListRegex.exactMatch(text)):
            periodIndex = text.find(".")
            parenthIndex = text.find(")")

            if periodIndex < 0:
                index = parenthIndex
            elif parenthIndex < 0:
                index = periodIndex
            elif parenthIndex > periodIndex:
                index = periodIndex
            else:
                index = parenthIndex

            if index > 0:
                token = Token()
                token.type = MTT.TokenNumberedList
                token.position = 0
                token.length = len(text)
                token.openingMarkupLength = index + 2
                self.addToken(token)
                self.setState(MS.MarkdownStateNumberedList)
                return True

            return False

        return False

    def tokenizeBulletPointList(self, text):
        foundBulletChar = False
        bulletCharIndex = -1
        spaceCount = 0
        whitespaceFoundAfterBulletChar = False
        previousState = self.previousState

        if previousState not in [MS.MarkdownStateUnknown,
                                 MS.MarkdownStateParagraphBreak,
                                 MS.MarkdownStateListLineBreak,
                                 MS.MarkdownStateNumberedList,
                                 MS.MarkdownStateBulletPointList,
                                 MS.MarkdownStateCodeBlock,
                                 MS.MarkdownStateCodeFenceEnd]:
            return False

        # Search for the bullet point character, which can
        # be either a '+', '-', or '*'.

        for i in range(len(text)):
            if text[i] == " ":
                if foundBulletChar:
                    # We've confirmed it's a bullet point by the whitespace that
                    # follows the bullet point character, and can now exit the
                    # loop.

                    whitespaceFoundAfterBulletChar = True
                    break

                else:
                    spaceCount += 1

                    # If this list item is the first in the list, ensure the
                    # number of spaces preceeding the bullet point does not
                    # exceed three, as that would indicate a code block rather
                    # than a bullet point list.

                    if spaceCount > 3 and previousState not in [
                        MS.MarkdownStateNumberedList,
                        MS.MarkdownStateBulletPointList,
                        MS.MarkdownStateListLineBreak,] and \
                       previousState in [
                        MS.MarkdownStateParagraphBreak,
                        MS.MarkdownStateUnknown,
                        MS.MarkdownStateCodeBlock,
                        MS.MarkdownStateCodeFenceEnd,]:
                        return False

            elif text[i] == "\t":
                if foundBulletChar:
                    # We've confirmed it's a bullet point by the whitespace that
                    # follows the bullet point character, and can now exit the
                    # loop.

                    whitespaceFoundAfterBulletChar = True
                    break

                elif previousState in [
                    MS.MarkdownStateParagraphBreak,
                    MS.MarkdownStateUnknown]:

                    # If this list item is the first in the list, ensure that
                    # no tab character preceedes the bullet point, as that would
                    # indicate a code block rather than a bullet point list.

                    return False

            elif text[i] in ["+", "-", "*"]:
                foundBulletChar = True
                bulletCharIndex = i

            else:
                return False

        if bulletCharIndex >= 0 and whitespaceFoundAfterBulletChar:
            token = Token()
            token.type = MTT.TokenBulletPointList
            token.position = 0
            token.length = len(text)
            token.openingMarkupLength = bulletCharIndex + 2
            self.addToken(token)
            self.setState(MS.MarkdownStateBulletPointList)
            return True

        return False

    def tokenizeHorizontalRule (self, text):
        if self.hruleRegex.exactMatch(text):
            token = Token()
            token.type = MTT.TokenHorizontalRule
            token.position = 0
            token.length = len(text)
            self.addToken(token)
            self.setState(MS.MarkdownStateHorizontalRule)
            return True

        return False

    def tokenizeLineBreak(self, text):
        currentState = self.currentState
        previousState = self.previousState
        nextState = self.nextState

        if currentState in [
            MS.MarkdownStateParagraph,
            MS.MarkdownStateBlockquote,
            MS.MarkdownStateNumberedList,
            MS.MarkdownStateBulletPointList,]:
            if previousState in [
                MS.MarkdownStateParagraph,
                MS.MarkdownStateBlockquote,
                MS.MarkdownStateNumberedList,
                MS.MarkdownStateBulletPointList,]:
                self.requestBacktrack()

            if nextState in [
                MS.MarkdownStateParagraph,
                MS.MarkdownStateBlockquote,
                MS.MarkdownStateNumberedList,
                MS.MarkdownStateBulletPointList,]:
                if self.lineBreakRegex.exactMatch(text):
                    token = Token()
                    token.type = MTT.TokenLineBreak
                    token.position = len(text) - 1
                    token.length = 1
                    self.addToken(token)
                    return True

        return False

    def tokenizeBlockquote(self, text):
        previousState = self.previousState
        if previousState == MS.MarkdownStateBlockquote or \
           self.blockquoteRegex.exactMatch(text):

            # Find any '>' characters at the front of the line.
            markupLength = 0

            for i in range(len(text)):
                if text[i] == ">":
                    markupLength = i + 1
                elif text[i] != " ":
                    # There are no more '>' characters at the front of the line,
                    # so stop processing.
                    break

            token = Token()
            token.type = MTT.TokenBlockquote
            token.position = 0
            token.length = len(text)

            if markupLength > 0:
                token.openingMarkupLength = markupLength

            self.addToken(token)
            self.setState(MS.MarkdownStateBlockquote)
            return True
        return False

    def tokenizeCodeBlock(self, text):
        previousState = self.previousState
        if previousState in [
                MS.MarkdownStateInGithubCodeFence,
                MS.MarkdownStateInPandocCodeFence]:
            self.setState(previousState)

            if (previousState == MS.MarkdownStateInGithubCodeFence and \
               self.githubCodeFenceEndRegex.exactMatch(text)) or \
               (previousState == MS.MarkdownStateInPandocCodeFence and \
               self.pandocCodeFenceEndRegex.exactMatch(text)):
                token = Token()
                token.type = MTT.TokenCodeFenceEnd
                token.position = 0
                token.length = len(text)
                self.addToken(token)
                self.setState(MS.MarkdownStateCodeFenceEnd)

            else:
                token = Token()
                token.type = MTT.TokenCodeBlock
                token.position = 0
                token.length = len(text)
                self.addToken(token)

            return True

        elif previousState in [
                MS.MarkdownStateCodeBlock,
                MS.MarkdownStateParagraphBreak,
                MS.MarkdownStateUnknown,] and \
             (text[:1] == "\t" or text[:4] == "    "):
            token = Token()
            token.type = MTT.TokenCodeBlock
            token.position = 0
            token.length = len(text)
            token.openingMarkupLength = len(text) - len(text.lstrip())
            self.addToken(token)
            self.setState(MS.MarkdownStateCodeBlock)
            return True

        elif previousState in [
                MS.MarkdownStateParagraphBreak,
                MS.MarkdownStateParagraph,
                MS.MarkdownStateUnknown,
                MS.MarkdownStateListLineBreak,]:
            foundCodeFenceStart = False
            token = Token()
            if self.githubCodeFenceStartRegex.exactMatch(text):
                foundCodeFenceStart = True
                token.type = MTT.TokenGithubCodeFence
                self.setState(MS.MarkdownStateInGithubCodeFence)

            elif self.pandocCodeFenceStartRegex.exactMatch(text):
                foundCodeFenceStart = True
                token.type = MTT.TokenPandocCodeFence
                self.setState(MS.MarkdownStateInPandocCodeFence)

            if foundCodeFenceStart:
                token.position = 0
                token.length = len(text)
                self.addToken(token)
                return True

        return False

    def tokenizeMultilineComment(self, text):
        previousState = self.previousState

        if previousState == MS.MarkdownStateComment:
            # Find the end of the comment, if any.
            index = text.find("-->")
            token = Token()
            token.type = MTT.TokenHtmlComment
            token.position = 0

            if index >= 0:
                token.length = index + 3
                self.addToken(token)

                # Return false so that the rest of the line that isn't within
                # the commented segment can be highlighted as normal paragraph
                # text.

            else:
                token.length = len(text)
                self.addToken(token)
                self.setState(MS.MarkdownStateComment)
                return True

        return False

    def tokenizeInline(self, text):
        escapedText = self.dummyOutEscapeCharacters(text)

        # Check if the line is a reference definition.
        if self.referenceDefinitionRegex.exactMatch(text):
            colonIndex = escapedText.find(":")
            token = Token()
            token.type = MTT.TokenReferenceDefinition
            token.position = 0
            token.length = colonIndex + 1
            self.addToken(token)

            # Replace the first bracket so that the '[...]:' reference definition
            # start doesn't get highlighted as a reference link.

            firstBracketIndex = escapedText.find("[")
            if firstBracketIndex >= 0:
                i = firstBracketIndex
                escapedText = escapedText[:i] + self.DUMMY_CHAR + escapedText[i+1:]

        escapedText = self.tokenizeVerbatim(escapedText)
        escapedText = self.tokenizeHtmlComments(escapedText)
        escapedText = self.tokenizeTableHeaderRow(escapedText)
        escapedText = self.tokenizeTableRow(escapedText)
        escapedText = self.tokenizeMatches(MTT.TokenImage, escapedText, self.imageRegex, 0, 0, False, True)
        escapedText = self.tokenizeMatches(MTT.TokenInlineLink, escapedText, self.inlineLinkRegex, 0, 0, False, True)
        escapedText = self.tokenizeMatches(MTT.TokenReferenceLink, escapedText, self.referenceLinkRegex, 0, 0, False, True)
        escapedText = self.tokenizeMatches(MTT.TokenHtmlEntity, escapedText, self.htmlEntityRegex)
        escapedText = self.tokenizeMatches(MTT.TokenAutomaticLink, escapedText, self.automaticLinkRegex, 0, 0, False, True)
        escapedText = self.tokenizeMatches(MTT.TokenStrong, escapedText, self.strongRegex, 2, 2, True)
        escapedText = self.tokenizeMatches(MTT.TokenEmphasis, escapedText, self.emphasisRegex, 1, 1, True)
        escapedText = self.tokenizeMatches(MTT.TokenMention, escapedText, self.mentionRegex, 0, 0, False, True)
        escapedText = self.tokenizeMatches(MTT.TokenCMAddition, escapedText, self.CMAdditionRegex, 3, 3, True)
        escapedText = self.tokenizeMatches(MTT.TokenCMDeletion, escapedText, self.CMDeletionRegex, 3, 3, True)
        escapedText = self.tokenizeMatches(MTT.TokenCMSubstitution, escapedText, self.CMSubstitutionRegex, 3, 3, True)
        escapedText = self.tokenizeMatches(MTT.TokenCMComment, escapedText, self.CMCommentRegex, 3, 3, True)
        escapedText = self.tokenizeMatches(MTT.TokenCMHighlight, escapedText, self.CMHighlightRegex, 3, 3, True)
        escapedText = self.tokenizeMatches(MTT.TokenStrikethrough, escapedText, self.strikethroughRegex, 2, 2, True)
        escapedText = self.tokenizeMatches(MTT.TokenHtmlTag, escapedText, self.htmlTagRegex)
        escapedText = self.tokenizeMatches(MTT.TokenSubScript, escapedText, self.subScriptRegex, 1, 1, True)
        escapedText = self.tokenizeMatches(MTT.TokenSuperScript, escapedText, self.superScriptRegex, 1, 1, True)

        return True

    def tokenizeVerbatim(self, text):
        index = self.verbatimRegex.indexIn(text)

        while index >= 0:
            end = ""
            count = self.verbatimRegex.matchedLength()

            # Search for the matching end, which should have the same number
            # of back ticks as the start.
            for i in range(count):
                end += '`'

            endIndex = text.find(end, index + count)

            # If the end was found, add the verbatim token.
            if endIndex >= 0:
                token = Token()
                token.type = MTT.TokenVerbatim
                token.position = index
                token.length = endIndex + count - index
                token.openingMarkupLength = count
                token.closingMarkupLength = count
                self.addToken(token)

                # Fill out the token match in the string with the dummy
                # character so that searches for other Markdown elements
                # don't find anything within this token's range in the string.

                for i in range(index, index + token.length):
                    text = text[:i] + self.DUMMY_CHAR + text[i+1:]

                index += token.length

            # Else start searching again at the very next character.
            else:
                index += 1

            index = self.verbatimRegex.indexIn(text, index)
        return text

    def tokenizeHtmlComments(self, text):
        previousState = self.previousState

        # Check for the end of a multiline comment so that it doesn't get further
        # tokenized. Don't bother formatting the comment itself, however, because
        # it should have already been tokenized in tokenizeMultilineComment().
        if previousState == MS.MarkdownStateComment:
            commentEnd = text.find("-->")
            for i in range(commentEnd + 3):
                text = text[:i] + self.DUMMY_CHAR + text[i+1:]

        # Now check for inline comments (non-multiline).
        commentStart = self.htmlInlineCommentRegex.indexIn(text)

        while commentStart >= 0:
            commentLength = self.htmlInlineCommentRegex.matchedLength()
            token = Token()
            token.type = MTT.TokenHtmlComment
            token.position = commentStart
            token.length = commentLength
            self.addToken(token)

            # Replace comment segment with dummy characters so that it doesn't
            # get tokenized again.

            for i in range(commentStart, commentStart + commentLength):
                text = text[:i] + self.DUMMY_CHAR + text[i+1:]

            commentStart = self.htmlInlineCommentRegex.indexIn(text, commentStart + commentLength)

        # Find multiline comment start, if any.
        commentStart = text.find("<!--")
        if commentStart >= 0:
            token = Token()
            token.type = MTT.TokenHtmlComment
            token.position = commentStart
            token.length = len(text) - commentStart
            self.addToken(token)
            self.setState(MS.MarkdownStateComment)

            # Replace comment segment with dummy characters so that it doesn't
            # get tokenized again.

            for i in range(commentStart, len(text)):
                text = text[:i] + self.DUMMY_CHAR + text[i+1:]
        return text

    def tokenizeTableHeaderRow(self, text):
        previousState = self.previousState
        nextState = self.nextState

        if previousState in [
            MS.MarkdownStateParagraphBreak,
            MS.MarkdownStateListLineBreak,
            MS.MarkdownStateSetextHeading1Line2,
            MS.MarkdownStateSetextHeading2Line2,
            MS.MarkdownStateAtxHeading1,
            MS.MarkdownStateAtxHeading2,
            MS.MarkdownStateAtxHeading3,
            MS.MarkdownStateAtxHeading4,
            MS.MarkdownStateAtxHeading5,
            MS.MarkdownStateAtxHeading6,
            MS.MarkdownStateHorizontalRule,
            MS.MarkdownStateCodeFenceEnd,
            MS.MarkdownStateUnknown,] and \
           self.getState() in [
            MS.MarkdownStateParagraph,
            MS.MarkdownStateUnknown] and \
           nextState == MS.MarkdownStatePipeTableDivider:
            self.setState(MS.MarkdownStatePipeTableHeader)

            headerStart = 0
            for i in range(len(text)):
                if text[i] == "|":
                    # Replace pipe with space so that it doesn't get formatted
                    # again with, for example, strong or emphasis formatting.
                    # Note that we use a space rather than DUMMY_CHAR for this,
                    # to prevent formatting such as strong and emphasis from
                    # picking it up.
                    text = text[:i] + " " + text[i+1:]

                    token = Token()

                    if i > 0:
                        token.type = MTT.TokenTableHeader
                        token.position = headerStart
                        token.length = i - headerStart
                        self.addToken(token)

                    token.type = MTT.TokenTablePipe
                    token.position = i
                    token.length = 1
                    self.addToken(token)
                    headerStart = i + 1

            if headerStart < len(text):
                token = Token()
                token.type = MTT.TokenTableHeader
                token.position = headerStart
                token.length = len(text) - headerStart
                self.addToken(token)

        return text

    def tokenizeTableDivider(self, text):
        previousState = self.previousState
        if previousState == MS.MarkdownStatePipeTableHeader:
            if self.pipeTableDividerRegex.exactMatch(text):
                self.setState(MS.MarkdownStatePipeTableDivider)
                token = Token()
                token.type = MTT.TokenTableDivider
                token.length = len(text)
                token.position = 0
                self.addToken(token)

                return True

            else:
                # Restart tokenizing on the previous line.
                self.requestBacktrack()
        elif previousState == MS.MarkdownStateParagraph:
            if self.pipeTableDividerRegex.exactMatch(text):
                # Restart tokenizing on the previous line.
                self.requestBacktrack()
                self.setState(MS.MarkdownStatePipeTableDivider)

                token = Token()
                token.length = len(text)
                token.position = 0
                token.type = MTT.TokenTableDivider
                self.addToken(token)
                return True

        return False

    def tokenizeTableRow(self, text):
        previousState = self.previousState

        if previousState in [
            MS.MarkdownStatePipeTableDivider,
            MS.MarkdownStatePipeTableRow]:
            self.setState(MS.MarkdownStatePipeTableRow)

            for i in range(len(text)):
                if text[i] == "|":
                    # Replace pipe with space so that it doesn't get formatted
                    # again with, for example, strong or emphasis formatting.
                    # Note that we use a space rather than DUMMY_CHAR for this,
                    # to prevent formatting such as strong and emphasis from
                    # picking it up.

                    text = text[:i] + " " + text[i+1:]

                    token = Token()
                    token.type = MTT.TokenTablePipe
                    token.position = i
                    token.length = 1
                    self.addToken(token)

        return text

    def tokenizeMatches(self, tokenType, text, regex,
                        markupStartCount=0, markupEndCount=0,
                        replaceMarkupChars=False, replaceAllChars=False):
        """
        Tokenizes a block of text, searching for all occurrances of regex.
        Occurrances are set to the given token type and added to the list of
        tokens.  The markupStartCount and markupEndCount values are used to
        indicate how many markup special characters preceed and follow the
        main text, respectively.

        For example, if the matched string is "**bold**", and
        markupStartCount = 2 and markupEndCount = 2, then the asterisks
        preceeding and following the word "bold" will be set as opening and
        closing markup in the token.

        If replaceMarkupChars is true, then the markupStartCount and
        markupEndCount characters will be replaced with a dummy character in
        the text QString so that subsequent parsings of the same line do not
        pick up the original characters.

        If replaceAllChars is true instead, then the entire matched text will
        be replaced with dummy characters--again, for ease in parsing the
        same line for other regular expression matches.
        """
        index = regex.indexIn(text)

        while index >= 0:
            length = regex.matchedLength()
            token = Token()
            token.type = tokenType
            token.position = index
            token.length = length

            if markupStartCount > 0:
                token.openingMarkupLength = markupStartCount

            if markupEndCount > 0:
                token.closingMarkupLength = markupEndCount

            if replaceAllChars:
                for i in range(index, index + length):
                    text = text[:i] + self.DUMMY_CHAR + text[i+1:]

            elif replaceMarkupChars:
                for i in range(index, index + markupStartCount):
                    text = text[:i] + self.DUMMY_CHAR + text[i+1:]
                for i in range(index + length - markupEndCount, index + length):
                    text = text[:i] + self.DUMMY_CHAR + text[i+1:]

            self.addToken(token)
            index = regex.indexIn(text, index + length)

        return text

    def dummyOutEscapeCharacters(self, text):
        """
        Replaces escaped characters in text so they aren't picked up
        during parsing.  Returns a copy of the input text string
        with the escaped characters replaced with a dummy character.
        """

        return re.sub("\\\\.", r"\$", text)

        #escape = False
        #escapedText = text

        #for i in range(len(text)):
            #if escape:
                #escapedText = escapedText[:i] + self.DUMMY_CHAR + escapedText[i+1:]
                #escape = False
            #elif text[i] == "\\":
                #escape = True
        #return escapedText
