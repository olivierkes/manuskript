#!/usr/bin/python
# -*- coding: utf-8 -*-

#==============================================================================
#   MARKDOWN STATES
#==============================================================================

class MarkdownState:
    MarkdownStateUnknown = -1
    MarkdownStateParagraphBreak = 0
    MarkdownStateListLineBreak = 1
    MarkdownStateParagraph = 2
    MarkdownStateAtxHeading1 = 3
    MarkdownStateAtxHeading2 = 4
    MarkdownStateAtxHeading3 = 5
    MarkdownStateAtxHeading4 = 6
    MarkdownStateAtxHeading5 = 7
    MarkdownStateAtxHeading6 = 8
    MarkdownStateBlockquote = 9
    MarkdownStateCodeBlock = 10
    MarkdownStateInGithubCodeFence = 11
    MarkdownStateInPandocCodeFence = 12
    MarkdownStateCodeFenceEnd = 13
    MarkdownStateComment = 14
    MarkdownStateHorizontalRule = 15
    MarkdownStateNumberedList = 16
    MarkdownStateBulletPointList = 17
    MarkdownStateSetextHeading1Line1 = 18
    MarkdownStateSetextHeading1Line2 = 19
    MarkdownStateSetextHeading2Line1 = 20
    MarkdownStateSetextHeading2Line2 = 21
    MarkdownStatePipeTableHeader = 22
    MarkdownStatePipeTableDivider = 23
    MarkdownStatePipeTableRow = 24

#==============================================================================
#   MARKDOWN TOKEN TYPE
#==============================================================================

class MarkdownTokenType:
    TokenUnknown  = -1

    # Titles
    TokenAtxHeading1 = 0
    TokenAtxHeading2 = 1
    TokenAtxHeading3 = 2
    TokenAtxHeading4 = 3
    TokenAtxHeading5 = 4
    TokenAtxHeading6 = 5
    TokenSetextHeading1Line1 = 6
    TokenSetextHeading1Line2 = 7
    TokenSetextHeading2Line1 = 8
    TokenSetextHeading2Line2 = 9

    TokenEmphasis = 10
    TokenStrong = 11
    TokenStrikethrough = 12
    TokenVerbatim = 13
    TokenHtmlTag = 14
    TokenHtmlEntity = 15
    TokenAutomaticLink = 16
    TokenInlineLink = 17
    TokenReferenceLink = 18
    TokenReferenceDefinition = 19
    TokenImage = 20
    TokenHtmlComment = 21
    TokenNumberedList = 22
    TokenBulletPointList = 23
    TokenHorizontalRule = 24
    TokenLineBreak = 25
    TokenBlockquote = 26
    TokenCodeBlock = 27
    TokenGithubCodeFence = 28
    TokenPandocCodeFence = 29
    TokenCodeFenceEnd = 30
    TokenMention = 31
    TokenTableHeader = 32
    TokenTableDivider = 33
    TokenTablePipe = 34
    TokenSuperScript = 35
    TokenSubScript = 36
    # CriticMarkup
    TokenCMAddition = 37 # {++ ++}
    TokenCMDeletion = 38 # {-- --}
    TokenCMSubstitution = 39 #{~~ ~> ~~}
    TokenCMComment = 40 # {>> <<}
    TokenCMHighlight = 41 # {== ==}{>> <<}
    TokenLast = 42

    TITLES =  [TokenAtxHeading1, TokenAtxHeading2, TokenAtxHeading3,
               TokenAtxHeading4, TokenAtxHeading5, TokenAtxHeading6,
               TokenSetextHeading1Line1, TokenSetextHeading1Line2,
               TokenSetextHeading2Line1, TokenSetextHeading2Line2]



class BlockquoteStyle:
    BlockquoteStylePlain = 0
    BlockquoteStyleItalic = 1
    BlockquoteStyleFancy = 2
