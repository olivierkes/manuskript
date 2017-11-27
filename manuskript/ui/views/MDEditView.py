#!/usr/bin/env python
# --!-- coding: utf8 --!--

import re

from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QTextCursor
# from PyQt5.QtWidgets import

from manuskript.ui.views.textEditView import textEditView
from manuskript.ui.highlighters import MarkdownHighlighter
# from manuskript.ui.editors.textFormat import textFormat
# from manuskript.ui.editors.MDFunctions import MDFormatSelection


class MDEditView(textEditView):
    def __init__(self, parent=None, index=None, html=None, spellcheck=True,
                 highlighting=False, dict="", autoResize=False):
        textEditView.__init__(self, parent, index, html, spellcheck,
                              highlighting=True, dict=dict,
                              autoResize=autoResize)

        # Highlighter
        self._textFormat = "md"
        self._highlighterClass = MarkdownHighlighter

        if index:
            # We have to setup things anew, for the highlighter notably
            self.setCurrentModelIndex(index)

    # def focusInEvent(self, event):
    #     """Finds textFormatter and attach them to that view."""
    #     textEditView.focusInEvent(self, event)
    #
    #     p = self.parent()
    #     while p.parent():
    #         p = p.parent()
    #
    #     if self._index:
    #         for tF in p.findChildren(textFormat, QRegExp(".*"),
    #                                  Qt.FindChildrenRecursively):
    #             tF.updateFromIndex(self._index)
    #             tF.setTextEdit(self)

    ###########################################################################
    # FORMATTING (#FIXME)
    ###########################################################################

    def applyFormat(self, _format):

        if self._textFormat == "md":
            if _format == "Bold": self.bold()
            elif _format == "Italic": self.italic()
            elif _format == "Code": self.verbatim()
            elif _format == "Clear": self.clearFormat()

    def bold(self): self.insertFormattingMarkup("**")
    def italic(self): self.insertFormattingMarkup("*")
    def strike(self): self.insertFormattingMarkup("~~")
    def verbatim(self): self.insertFormattingMarkup("`")
    def superscript(self): self.insertFormattingMarkup("^")
    def subscript(self): self.insertFormattingMarkup("~")

    def selectWord(self, cursor):
        if cursor.selectedText():
            return
        end = cursor.selectionEnd()
        cursor.movePosition(QTextCursor.StartOfWord)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)

    def selectBlock(self, cursor):
        cursor.movePosition(QTextCursor.StartOfBlock)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)

    def comment(self):
        cursor = self.textCursor()

        # Select begining and end of words
        self.selectWord(cursor)

        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText("<!-- " + text + " -->")
        else:
            cursor.insertText("<!--  -->")
            cursor.movePosition(QTextCursor.PreviousCharacter,
                                QTextCursor.MoveAnchor, 4)
            self.setTextCursor(cursor)

    def commentLine(self):
        cursor = self.textCursor()

        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        block = self.document().findBlock(start)
        block2 = self.document().findBlock(end)

        if True:
            # Method 1
            cursor.beginEditBlock()
            while block.isValid():
                self.commentBlock(block)
                if block == block2: break
                block = block.next()
            cursor.endEditBlock()

        else:
            # Method 2
            cursor.beginEditBlock()
            cursor.setPosition(block.position())
            cursor.insertText("<!--\n")
            cursor.setPosition(block2.position() + block2.length() - 1)
            cursor.insertText("\n-->")
            cursor.endEditBlock()

    def commentBlock(self, block):
        cursor = QTextCursor(block)
        text = block.text()
        if text[:5] == "<!-- " and \
           text[-4:] == " -->":
            text2 = text[5:-4]
        else:
            text2 = "<!-- " + text + " -->"
        self.selectBlock(cursor)
        cursor.insertText(text2)

    def insertFormattingMarkup(self, markup):
        cursor = self.textCursor()

        # Select begining and end of words
        self.selectWord(cursor)

        if cursor.hasSelection():
            start = cursor.selectionStart()
            end = cursor.selectionEnd() + len(markup)
            cursor.beginEditBlock()
            cursor.setPosition(start)
            cursor.insertText(markup)
            cursor.setPosition(end)
            cursor.insertText(markup)
            cursor.endEditBlock()
            cursor.movePosition(QTextCursor.PreviousCharacter,
                                QTextCursor.KeepAnchor, len(markup))
            #self.setTextCursor(cursor)

        else:
            # Insert markup twice (for opening and closing around the cursor),
            # and then move the cursor to be between the pair.
            cursor.beginEditBlock()
            cursor.insertText(markup)
            cursor.insertText(markup)
            cursor.movePosition(QTextCursor.PreviousCharacter,
                                QTextCursor.MoveAnchor, len(markup))
            cursor.endEditBlock()
            self.setTextCursor(cursor)

    def clearFormat(self):
        cursor = self.textCursor()
        text = cursor.selectedText()
        if not text:
            self.selectBlock(cursor)
            text = cursor.selectedText()
        text = self.clearedFormat(text)
        cursor.insertText(text)

    def clearedFormat(self, text):
        # FIXME: clear also block formats
        for reg, rep, flags in [
            ("\*\*(.*?)\*\*", "\\1", None), # bold
            ("__(.*?)__", "\\1", None), # bold
            ("\*(.*?)\*", "\\1", None), # emphasis
            ("_(.*?)_", "\\1", None), # emphasis
            ("`(.*?)`", "\\1", None), # verbatim
            ("~~(.*?)~~", "\\1", None), # strike
            ("\^(.*?)\^", "\\1", None), # superscript
            ("~(.*?)~", "\\1", None), # subscript
            ("<!--(.*)-->", "\\1", re.S), # comments


            # LINES OR BLOCKS
            (r"^#*\s*(.+?)\s*", "\\1", re.M), # ATX
            (r"^[=-]*$", "", re.M), # Setext
            (r"^`*$", "", re.M), # Code block fenced
            (r"^\s*[-+*]\s*(.*?)\s*$", "\\1", re.M), # Bullet List
            (r"^\s*[0-9a-z](\.|\))\s*(.*?)\s*$", "\\2", re.M), # Bullet List
            (r"\s*[>\s]*(.*?)\s*$", "\\1", re.M), # Code block and blockquote

            ]:
            text = re.sub(reg, rep, text, flags if flags else 0)
        return text

    def clearedFormatForStats(self, text):
        # Remove stuff that musn't be counted
        # FIXME: clear also block formats
        for reg, rep, flags in [
            ("<!--.*-->", "", re.S), # comments
            ]:
            text = re.sub(reg, rep, text, flags if flags else 0)
        return text

    def titleSetext(self, level):
        cursor = self.textCursor()

        cursor.beginEditBlock()
        # Is it already a Setext header?
        if cursor.block().userState() in [
                MS.MarkdownStateSetextHeading1Line2,
                MS.MarkdownStateSetextHeading2Line2]:
            cursor.movePosition(QTextCursor.PreviousBlock)

        text = cursor.block().text()

        if cursor.block().userState() in [
                MS.MarkdownStateSetextHeading1Line1,
                MS.MarkdownStateSetextHeading2Line1]:
            # Need to remove line below
            c = QTextCursor(cursor.block().next())
            self.selectBlock(c)
            c.insertText("")

        char = "=" if level == 1 else "-"
        text = re.sub("^#*\s*(.*)\s*#*", "\\1", text)  # Removes #
        sub = char * len(text)
        text = text + "\n" + sub

        self.selectBlock(cursor)
        cursor.insertText(text)
        cursor.endEditBlock()

    def titleATX(self, level):
        cursor = self.textCursor()
        text = cursor.block().text()

        # Are we in a Setext Header?
        if cursor.block().userState() in [
                MS.MarkdownStateSetextHeading1Line1,
                MS.MarkdownStateSetextHeading2Line1]:
            # Need to remove line below
            cursor.beginEditBlock()
            c = QTextCursor(cursor.block().next())
            self.selectBlock(c)
            c.insertText("")

            self.selectBlock(cursor)
            cursor.insertText(text)
            cursor.endEditBlock()
            return

        elif cursor.block().userState() in [
                MS.MarkdownStateSetextHeading1Line2,
                MS.MarkdownStateSetextHeading2Line2]:
            cursor.movePosition(QTextCursor.PreviousBlock)
            self.setTextCursor(cursor)
            self.titleATX(level)
            return

        m = re.match("^(#+)(\s*)(.+)", text)
        if m:
            pre = m.group(1)
            space = m.group(2)
            txt = m.group(3)

            if len(pre) == level:
                # Remove title
                text = txt
            else:
                text = "#" * level + space + txt

        else:
            text = "#" * level + " " + text

        self.selectBlock(cursor)
        cursor.insertText(text)
