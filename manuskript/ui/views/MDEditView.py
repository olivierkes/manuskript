#!/usr/bin/env python
# --!-- coding: utf8 --!--

import re

from PyQt5.QtCore import QRegExp, Qt, QTimer, QRect, QPoint
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import qApp, QToolTip

from manuskript.ui.views.textEditView import textEditView
from manuskript.ui.highlighters import MarkdownHighlighter
from manuskript import settings
from manuskript.ui.highlighters.markdownEnums import MarkdownState as MS
from manuskript.ui.highlighters.markdownTokenizer import MarkdownTokenizer as MT
from manuskript import functions as F

import logging
LOGGER = logging.getLogger(__name__)

class MDEditView(textEditView):

    blockquoteRegex = QRegExp("^ {0,3}(>\\s*)+")
    listRegex = QRegExp(r"^(\s*)([+*-]|([0-9a-z])+([.\)]))(\s+)")
    inlineLinkRegex = QRegExp("\\[([^\n]+)\\]\\(([^\n]+)\\)")
    imageRegex = QRegExp("!\\[([^\n]*)\\]\\(([^\n]+)\\)")
    automaticLinkRegex = QRegExp("(<([a-zA-Z]+\\:[^\n]+)>)|(<([^\n]+@[^\n]+)>)")

    def __init__(self, parent=None, index=None, html=None, spellcheck=None,
                 highlighting=False, dict="", autoResize=False):
        textEditView.__init__(self, parent, index, html, spellcheck,
                              highlighting=True, dict=dict,
                              autoResize=autoResize)

        # Highlighter
        self._textFormat = "md"
        self._highlighterClass = MarkdownHighlighter
        self._noFocusMode = False
        self._lastCursorPosition = None

        if index:
            # We have to setup things anew, for the highlighter notably
            self.setCurrentModelIndex(index)

        self.cursorPositionChanged.connect(self.cursorPositionHasChanged)
        self.verticalScrollBar().rangeChanged.connect(
            self.scrollBarRangeChanged)

        # Clickable things
        self.clickRects = []
        self.textChanged.connect(self.getClickRects)
        self.document().documentLayoutChanged.connect(self.getClickRects)
        self.setMouseTracking(True)

    ###########################################################################
    # KEYPRESS
    ###########################################################################

    def keyPressEvent(self, event):
        k = event.key()
        m = event.modifiers()
        cursor = self.textCursor()

        # RETURN
        if k == Qt.Key_Return:
            if not cursor.hasSelection():
                if m & Qt.ShiftModifier:
                    # Insert Markdown-style line break
                    cursor.insertText("  ")

                if m & Qt.ControlModifier:
                    cursor.insertText("\n")
                else:
                    self.handleCarriageReturn()
            else:
                textEditView.keyPressEvent(self, event)

        # TAB
        elif k == Qt.Key_Tab:
            #self.indentText()
            # FIXME
            textEditView.keyPressEvent(self, event)
        elif k == Qt.Key_Backtab:
            #self.unindentText()
            # FIXME
            textEditView.keyPressEvent(self, event)

        else:
            textEditView.keyPressEvent(self, event)

    # Thanks to GhostWriter, mainly
    def handleCarriageReturn(self):
        autoInsertText = "";
        cursor = self.textCursor()
        endList = False
        moveBack = False
        text = cursor.block().text()

        if cursor.positionInBlock() < cursor.block().length() - 1:
            autoInsertText = self.getPriorIndentation()
            if cursor.positionInBlock() < len(autoInsertText):
                autoInsertText = autoInsertText[:cursor.positionInBlock()]

        else:
            s = cursor.block().userState()

            if s in [MS.MarkdownStateNumberedList,
                     MS.MarkdownStateBulletPointList]:
                self.listRegex.indexIn(text)
                g = self.listRegex.capturedTexts()
                    # 0 = "   a. " or "  * "
                    # 1 = "   "       "  "
                    # 2 =    "a."       "*"
                    # 3 =    "a"          ""
                    # 4 =     "."         ""
                    # 5 =      " "        " "

                # If the line of text is an empty list item, end the list.
                if len(g[0].strip()) == len(text.strip()):
                    endList = True

                # Else increment the list number
                elif g[3]:  # Numbered list
                    try: # digit
                        i = int(g[3])+1

                    except: # letter
                        i = chr(ord(g[3])+1)

                    autoInsertText = "{}{}{}{}".format(
                            g[1], i, g[4], g[5])

                else:  # Bullet list
                    autoInsertText = g[0]

                if text[-2:] == "  ":
                    autoInsertText = " " * len(autoInsertText)

            elif s == MS.MarkdownStateBlockquote:
                self.blockquoteRegex.indexIn(text)
                g = self.blockquoteRegex.capturedTexts()
                autoInsertText = g[0]

            elif s in [MS.MarkdownStateInGithubCodeFence,
                       MS.MarkdownStateInPandocCodeFence] and \
                 cursor.block().previous().userState() != s:
                autoInsertText = "\n" + text
                moveBack = True

            else:
                autoInsertText = self.getPriorIndentation()

        # Clear the list
        if endList:
            autoInsertText = self.getPriorIndentation()
            cursor.movePosition(QTextCursor.StartOfBlock)
            cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
            cursor.insertText(autoInsertText)
            autoInsertText = ""

        # Finally, we insert
        cursor.insertText("\n" + autoInsertText)
        if moveBack:
            cursor.movePosition(QTextCursor.PreviousBlock)
            self.setTextCursor(cursor)

        self.ensureCursorVisible()

    def getPriorIndentation(self):
        text = self.textCursor().block().text()
        l = len(text) - len(text.lstrip())
        return text[:l]

    def getPriorMarkdownBlockItemStart(self, itemRegex):
        text = self.textCursor().block().text()
        if itemRegex.indexIn(text) >= 0:
            return text[itemRegex.matchedLength():]

        return ""

    ###########################################################################
    # TypeWriterScrolling
    ###########################################################################

    def setCurrentModelIndex(self, index):
        textEditView.setCurrentModelIndex(self, index)
        self.centerCursor()

    def cursorPositionHasChanged(self):
        self.centerCursor()
        # Focus mode
        if self.highlighter and settings.textEditor["focusMode"]:
            if self._lastCursorPosition:
                block = self.document().findBlock(self._lastCursorPosition)
                self.highlighter.rehighlightBlock(block)
            self._lastCursorPosition = self.textCursor().position()
            block = self.document().findBlock(self._lastCursorPosition)
            self.highlighter.rehighlightBlock(block)

    def centerCursor(self, force=False):
        cursor = self.cursorRect()
        scrollbar = self.verticalScrollBar()
        viewport = self.viewport().rect()
        if (force or settings.textEditor["alwaysCenter"]
                or cursor.bottom() >= viewport.bottom()
                or cursor.top() <= viewport.top()):
            offset = viewport.center() - cursor.center()
            scrollbar.setValue(scrollbar.value() - offset.y())

    def scrollBarRangeChanged(self, min, max):
        """
        Adds viewport height to scrollbar max so that we can center cursor
        on screen.
        """
        if settings.textEditor["alwaysCenter"]:
            self.verticalScrollBar().blockSignals(True)
            self.verticalScrollBar().setMaximum(max + self.viewport().height())
            self.verticalScrollBar().blockSignals(False)

    ###########################################################################
    # FORMATTING
    ###########################################################################

    def bold(self): self.insertFormattingMarkup("**")
    def italic(self): self.insertFormattingMarkup("*")
    def strike(self): self.insertFormattingMarkup("~~")
    def verbatim(self): self.insertFormattingMarkup("`")
    def superscript(self): self.insertFormattingMarkup("^")
    def subscript(self): self.insertFormattingMarkup("~")
    def blockquote(self): self.lineFormattingMarkup("> ")
    def orderedList(self): self.lineFormattingMarkup(" 1. ")
    def unorderedList(self): self.lineFormattingMarkup("  - ")

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

        # Select beginning and end of words
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

    def lineFormattingMarkup(self, markup):
        """
        Adds `markup` at the beginning of block.
        """
        cursor = self.textCursor()
        cursor.movePosition(cursor.StartOfBlock)
        cursor.insertText(markup)

    def insertFormattingMarkup(self, markup):
        cursor = self.textCursor()

        # Select beginning and end of words
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
            (r"\*\*(.*?)\*\*", "\\1", None), # bold
            ("__(.*?)__", "\\1", None), # bold
            (r"\*(.*?)\*", "\\1", None), # emphasis
            ("_(.*?)_", "\\1", None), # emphasis
            ("`(.*?)`", "\\1", None), # verbatim
            ("~~(.*?)~~", "\\1", None), # strike
            (r"\^(.*?)\^", "\\1", None), # superscript
            ("~(.*?)~", "\\1", None), # subscript
            (r"<!--\s*(.*?)\s*-->", "\\1", re.S), # comments

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
        text = re.sub(r"^#*\s*(.*)\s*#*", "\\1", text)  # Removes #
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

        m = re.match(r"^(#+)(\s*)(.+)", text)
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

    ###########################################################################
    # CLICKABLE THINKS
    ###########################################################################

    def resizeEvent(self, event):
        textEditView.resizeEvent(self, event)
        self.getClickRects()

    def scrollContentsBy(self, dx, dy):
        textEditView.scrollContentsBy(self, dx, dy)
        self.getClickRects()

    def getClickRects(self):
        """
        Parses the whole texte to catch clickable things: links and images.
        Stores the result so that it can be used elsewhere.
        """
        cursor = self.textCursor()
        refs = []
        text = self.toPlainText()
        for rx in [
                self.imageRegex,
                self.automaticLinkRegex,
                self.inlineLinkRegex,
            ]:
            pos = 0
            while rx.indexIn(text, pos) != -1:
                cursor.setPosition(rx.pos())
                r1 = self.cursorRect(cursor)
                pos = rx.pos() + rx.matchedLength()
                cursor.setPosition(pos)
                r2 = self.cursorRect(cursor)
                if r1.top() == r2.top():
                    ct = ClickThing(
                            QRect(r1.topLeft(), r2.bottomRight()),
                            rx,
                            rx.capturedTexts())
                    refs.append(ct)
                else:
                    r1.setRight(self.viewport().geometry().right())
                    refs.append(ClickThing(r1, rx, rx.capturedTexts()))
                    r2.setLeft(self.viewport().geometry().left())
                    refs.append(ClickThing(r2, rx, rx.capturedTexts()))
                    # We check for middle lines
                    cursor.setPosition(rx.pos())
                    cursor.movePosition(cursor.Down)
                    while self.cursorRect(cursor).top() != r2.top():
                        r3 = self.cursorRect(cursor)
                        r3.setLeft(self.viewport().geometry().left())
                        r3.setRight(self.viewport().geometry().right())
                        refs.append(ClickThing(r3, rx, rx.capturedTexts()))
                        if not cursor.movePosition(cursor.Down):
                            # Super-rare failure. Leaving log message for future investigation.
                            LOGGER.debug("Failed to move cursor down while calculating clickables. Aborting.")
                            break

        self.clickRects = refs

    def mouseMoveEvent(self, event):
        """
        When mouse moves, we show tooltip when appropriate.
        """
        self.beginTooltipMoveEvent()
        textEditView.mouseMoveEvent(self, event)
        self.endTooltipMoveEvent()

        onRect = [r for r in self.clickRects if r.rect.contains(event.pos())]

        if not onRect:
            qApp.restoreOverrideCursor()
            self.hideTooltip()
            return

        ct = onRect[0]
        if not qApp.overrideCursor():
            qApp.setOverrideCursor(Qt.PointingHandCursor)

        if ct.regex == self.automaticLinkRegex:
            tooltip = ct.texts[2] or ct.texts[4]

        elif ct.regex == self.imageRegex:
            tt = ("<p><b>" + ct.texts[1] + "</b></p>"
                  +"<p><img src='data:image/png;base64,{}'></p>")
            tooltip = None
            pos = event.pos() + QPoint(0, ct.rect.height())
            ImageTooltip.fromUrl(ct.texts[2], pos, self)

        elif ct.regex == self.inlineLinkRegex:
            tooltip = ct.texts[1] or ct.texts[2]

        if tooltip:
            tooltip = self.tr("{} (CTRL+Click to open)").format(tooltip)
            self.showTooltip(self.mapToGlobal(event.pos()), tooltip)

    def mouseReleaseEvent(self, event):
        textEditView.mouseReleaseEvent(self, event)
        onRect = [r for r in self.clickRects if r.rect.contains(event.pos())]
        if onRect and event.modifiers() & Qt.ControlModifier:
            ct = onRect[0]

            if ct.regex == self.automaticLinkRegex:
                url = ct.texts[2] or ct.texts[4]
            elif ct.regex == self.imageRegex:
                url = ct.texts[2]
            elif ct.regex == self.inlineLinkRegex:
                url = ct.texts[2]

            F.openURL(url)
            qApp.restoreOverrideCursor()

    # def paintEvent(self, event):
    #     """
    #     Only useful for debugging: shows which rects are detected for
    #     clickable things.
    #     """
    #     textEditView.paintEvent(self, event)
    #
    #     # Debug: paint rects
    #     from PyQt5.QtGui import QPainter
    #     painter = QPainter(self.viewport())
    #     painter.setPen(Qt.gray)
    #     for r in self.clickRects:
    #         painter.drawRect(r.rect)

    def doTooltip(self, pos, message):
        QToolTip.showText(self.mapToGlobal(pos), message)

class ClickThing:
    """
    A simple class to remember QRect associated with clickable stuff.
    """
    def __init__(self, rect, regex, texts):
        self.rect = rect
        self.regex = regex
        self.texts = texts

from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager, QNetworkReply
from PyQt5.QtCore import QIODevice, QUrl, QBuffer
from PyQt5.QtGui import QPixmap

class ImageTooltip:
    """
    This class handles the retrieving and caching of images in order to display these in tooltips.
    """

    cache = {}
    manager = QNetworkAccessManager()
    processing = {}

    supportedSchemes = ("", "file", "http", "https")

    def fromUrl(url, pos, editor):
        """
        Shows the image tooltip for the given url if available, or requests it for future use.
        """
        ImageTooltip.editor = editor

        if ImageTooltip.showTooltip(url, pos):
            return # the url already exists in the cache

        try:
            ImageTooltip.manager.finished.connect(ImageTooltip.finished, F.AUC)
        except:
            pass # already connected

        qurl = QUrl.fromUserInput(url)
        if (qurl == QUrl()):
            ImageTooltip.cache[url] = (False, ImageTooltip.manager.tr("The image path or URL is incomplete or malformed."))
            ImageTooltip.showTooltip(url, pos)
            return # empty QUrl means it failed completely
        elif (qurl.scheme() not in ImageTooltip.supportedSchemes):
            # QUrl.fromUserInput() can occasionally deduce an incorrect scheme,
            # which produces an error message regarding an unknown scheme. (Yay!)
            # But it also breaks all possible methods to try and associate the
            # reply with the original request in finished(), since reply.request()
            # is completely and utterly butchered for all tracking needs. :'(
            # (The QNetworkRequest, .url() and .originatingObject() can all change.)

            # Test case (Linux): ![image](C:\test_root.jpg)
            ImageTooltip.cache[url] = (False, ImageTooltip.manager.tr("The protocol \"{}\" is not supported.").format(qurl.scheme()))
            ImageTooltip.showTooltip(url, pos)
            return # no more request/reply chaos, please!
        elif (qurl in ImageTooltip.processing):
            return # one download is more than enough

        # Request the image for later processing.
        request = QNetworkRequest(qurl)
        ImageTooltip.processing[qurl] = (pos, url)
        reply = ImageTooltip.manager.get(request)

        # On Linux the finished() signal is not triggered when the url resembles
        # 'file://X:/...'. But because it completes instantly, we can manually
        # trigger the code to keep our processing dictionary neat & clean.
        if reply.error() == 302:  # QNetworkReply.ProtocolInvalidOperationError
            ImageTooltip.finished(reply)

    def finished(reply):
        """
        After retrieving an image, we add it to the cache.
        """
        cache = ImageTooltip.cache
        url_key = reply.request().url()
        pos, url = None, None

        if url_key in ImageTooltip.processing:
            # Obtain the information associated with this request.
            pos, url = ImageTooltip.processing[url_key]
            del ImageTooltip.processing[url_key]
        elif len(ImageTooltip.processing) == 0:
            # We are not processing anything. Maybe it is a spurious signal,
            # or maybe the 'reply.error() == 302' workaround in fromUrl() has
            # been fixed in Qt. Whatever the reason, we can assume this request
            # has already been handled, and needs no more work from us.
            return
        else:
            # Somehow we lost track. Log what we can to hopefully figure it out.
            LOGGER.warning("Unable to match fetched data for tooltip to original request.")
            LOGGER.warning("- Completed request: %s", url_key)
            LOGGER.warning("- Status upon finishing: %s, %s", reply.error(), reply.errorString())
            LOGGER.warning("- Currently processing: %s", ImageTooltip.processing)
            return

        # Update cache with retrieved data.
        if reply.error() != QNetworkReply.NoError:
            cache[url] = (False, reply.errorString())
        else:
            px = QPixmap()
            px.loadFromData(reply.readAll())
            px = px.scaled(800, 600, Qt.KeepAspectRatio)
            cache[url] = (True, px)

        ImageTooltip.showTooltip(url, pos)

    def showTooltip(url, pos):
        """
        Show a tooltip for the given url based on cached information.
        """
        cache = ImageTooltip.cache

        if url in cache:
            if not cache[url][0]:  # error, image was not found
                ImageTooltip.tooltipError(cache[url][1], pos)
            else:
                ImageTooltip.tooltip(cache[url][1], pos)
            return True
        return False

    def tooltipError(message, pos):
        """
        Display a tooltip with an error message at the given position.
        """
        ImageTooltip.editor.doTooltip(pos, message)

    def tooltip(image, pos):
        """
        Display a tooltip with an image at the given position.
        """
        px = image
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        px.save(buffer, "PNG", quality=100)
        image = bytes(buffer.data().toBase64()).decode()
        tt = "<p><img src='data:image/png;base64,{}'></p>".format(image)
        ImageTooltip.editor.doTooltip(pos, tt)
