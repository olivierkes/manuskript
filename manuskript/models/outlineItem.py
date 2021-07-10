#!/usr/bin/env python
# --!-- coding: utf8 --!--

import time
import locale
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import qApp
from lxml import etree as ET
from manuskript.models.abstractItem import abstractItem
from manuskript.models.searchableItem import searchableItem
from manuskript import enums
from manuskript import functions as F
from manuskript import settings
from manuskript.converters import HTML2PlainText
from manuskript.searchLabels import OutlineSearchLabels
from manuskript.enums import Outline, Model

try:
    locale.setlocale(locale.LC_ALL, '')
except:
    # Invalid locale, but not really a big deal because it's used only for
    # number formatting
    pass

import logging
LOGGER = logging.getLogger(__name__)

class outlineItem(abstractItem, searchableItem):

    enum = enums.Outline

    # Used for XML export
    name = "outlineItem"

    def __init__(self, model=None, title="", _type="folder", xml=None, parent=None, ID=None):
        abstractItem.__init__(self, model, title, _type, xml, parent, ID)
        searchableItem.__init__(self, OutlineSearchLabels)

        self.defaultTextType = None
        if not self._data.get(self.enum.compile):
            self._data[self.enum.compile] = 2

    #######################################################################
    # Properties
    #######################################################################

    def isFolder(self):
        return self._data[self.enum.type] == "folder"

    def isText(self):
        return self._data[self.enum.type] == "md"

    def isMD(self):
        return self._data[self.enum.type] == "md"

    def isMMD(self):
        return self._data[self.enum.type] == "md"

    def text(self):
        return self.data(self.enum.text)

    def compile(self):
        if self._data.get(self.enum.compile, 1) in ["0", 0]:
            return False
        elif self.parent():
            return self.parent().compile()
        else:
            return True  # rootItem always compile

    def POV(self):
        return self.data(self.enum.POV)

    def status(self):
        return self.data(self.enum.status)

    def label(self):
        return self.data(self.enum.label)

    def customIcon(self):
        return self.data(self.enum.customIcon)

    def setCustomIcon(self, customIcon):
        self.setData(self.enum.customIcon, customIcon)

    def wordCount(self):
        return self._data.get(self.enum.wordCount, 0)

    def charCount(self):
        return self._data.get(self.enum.charCount, 0)

    def __str__(self):
        return "{id}: {folder}{title}{children}".format(
            id=self.ID(),
            folder="*" if self.isFolder() else "",
            title=self.data(self.enum.title),
            children="" if self.isText() else "({})".format(self.childCount())
            )

    __repr__ = __str__

    def charCount(self):
        return self._data.get(self.enum.charCount, 0)

    #######################################################################
    # Data
    #######################################################################

    def data(self, column, role=Qt.DisplayRole):

        data = abstractItem.data(self, column, role)
        E = self.enum

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if data == "" and column == E.revisions:
                return []

            else:
                # Used to verify nbsp characters not getting clobbered.
                #if column == E.text:
                #    print("GET", str(role), "-->", str([hex(ord(x)) for x in data]))
                return data

        elif role == Qt.DecorationRole and column == E.title:
            if self.customIcon():
                return QIcon.fromTheme(self.data(E.customIcon))
            if self.isFolder():
                return QIcon.fromTheme("folder")
            elif self.isText():
                return QIcon.fromTheme("text-x-generic")

        elif role == Qt.CheckStateRole and column == E.compile:
            return Qt.Checked if self.compile() else Qt.Unchecked

        elif role == Qt.FontRole:
            f = QFont()
            if (column == E.wordCount or column == E.charCount) and self.isFolder():
                f.setItalic(True)
            elif column == E.goal and self.isFolder() and not self.data(E.setGoal):
                f.setItalic(True)
            if self.isFolder():
                f.setBold(True)
            return f

    def setData(self, column, data, role=Qt.DisplayRole):

        E = self.enum

        if column == E.text and self.isFolder():
            # Folder have no text
            return

        if column == E.goal:
            self._data[E.setGoal] = F.toInt(data) if F.toInt(data) > 0 else ""

        # Checking if we will have to recount words
        updateWordCount = False
        if column in [E.wordCount, E.charCount, E.goal, E.setGoal]:
            updateWordCount = not column in self._data or self._data[column] != data

        # Stuff to do before
        if column == E.text:
            self.addRevision()
            # Used to verify nbsp characters not getting clobbered.
            #print("SET", str(role), "-->", str([hex(ord(x)) for x in data]))

        # Calling base class implementation
        abstractItem.setData(self, column, data, role)

        # Stuff to do afterwards
        if column == E.text:
            wc = F.wordCount(data)
            cc = F.charCount(data, settings.countSpaces)
            self.setData(E.wordCount, wc)
            self.setData(E.charCount, cc)

        if column == E.compile:
            # Title changes when compile changes
            self.emitDataChanged(cols=[E.title, E.compile],
                                 recursive=True)

        if column == E.customIcon:
            # If custom icon changed, we tell views to update title (so that
            # icons will be updated as well)
            self.emitDataChanged(cols=[E.title])

        if updateWordCount:
            self.updateWordCount()

    #######################################################################
    # Wordcount
    #######################################################################

    def insertChild(self, row, child):
        abstractItem.insertChild(self, row, child)
        self.updateWordCount()

    def removeChild(self, row):
        r = abstractItem.removeChild(self, row)
        self.updateWordCount()
        return r

    def updateWordCount(self):
        """Update word count for item and parents."""
        if not self.isFolder():
            setGoal = F.toInt(self.data(self.enum.setGoal))
            goal = F.toInt(self.data(self.enum.goal))

            if goal != setGoal:
                self._data[self.enum.goal] = setGoal
            if setGoal:
                wc = F.toInt(self.data(self.enum.wordCount))
                self.setData(self.enum.goalPercentage, wc / float(setGoal))

        else:
            wc = 0
            cc = 0
            for c in self.children():
                wc += F.toInt(c.data(self.enum.wordCount))
                cc += F.toInt(c.data(self.enum.charCount))
            self._data[self.enum.wordCount] = wc
            self._data[self.enum.charCount] = cc

            setGoal = F.toInt(self.data(self.enum.setGoal))
            goal = F.toInt(self.data(self.enum.goal))

            if setGoal:
                if goal != setGoal:
                    self._data[self.enum.goal] = setGoal
                    goal = setGoal
            else:
                goal = 0
                for c in self.children():
                    goal += F.toInt(c.data(self.enum.goal))
                self._data[self.enum.goal] = goal

            if goal:
                self.setData(self.enum.goalPercentage, wc / float(goal))
            else:
                self.setData(self.enum.goalPercentage, "")

        self.emitDataChanged([self.enum.goal, self.enum.setGoal,
                              self.enum.wordCount, self.enum.charCount,
                              self.enum.goalPercentage])

        if self.parent():
            self.parent().updateWordCount()

    def stats(self):
        wc = self.data(enums.Outline.wordCount)
        goal = self.data(enums.Outline.goal)
        progress = self.data(enums.Outline.goalPercentage)
        if not wc:
            wc = 0
        if goal:
            return qApp.translate("outlineItem", "{} words / {} ({})").format(
                    locale.format_string("%d", wc, grouping=True),
                    locale.format_string("%d", goal, grouping=True),
                    "{}%".format(str(int(progress * 100))))
        else:
            return qApp.translate("outlineItem", "{} words").format(
                    locale.format_string("%d", wc, grouping=True))

    #######################################################################
    # Tools: split and merge
    #######################################################################

    def split(self, splitMark, recursive=True):
        """
        Split scene at splitMark. If multiple splitMark, multiple splits.

        If called on a folder and recursive is True, then it is recursively
        applied to every children.
        """
        if self.isFolder() and recursive:
            for c in self.children():
                c.split(splitMark)

        else:
            txt = self.text().split(splitMark)

            if len(txt) == 1:
                # Mark not found
                return False

            else:

                # Stores the new text
                self.setData(self.enum.text, txt[0])

                k = 1
                for subTxt in txt[1:]:
                    # Create a copy
                    item = self.copy()

                    # Change title adding _k
                    item.setData(self.enum.title,
                                 "{}_{}".format(item.title(), k+1))

                    # Set text
                    item.setData(self.enum.text, subTxt)

                    # Inserting item
                    #self.parent().insertChild(self.row()+k, item)
                    self._model.insertItem(item, self.row()+k, self.parent().index())
                    k += 1

    def splitAt(self, position, length=0):
        """
        Splits note at position p.

        If length is bigger than 0, it describes the length of the title, made
        from the character following position.
        """

        txt = self.text()

        # Stores the new text
        self.setData(self.enum.text, txt[:position])

        # Create a copy
        item = self.copy()

        # Update title
        if length > 0:
            title = txt[position:position+length].replace("\n", "")
        else:
            title = "{}_{}".format(item.title(), 2)
        item.setData(self.enum.title, title)

        # Set text
        item.setData(self.enum.text, txt[position+length:])

        # Inserting item using the model to signal views
        self._model.insertItem(item, self.row()+1, self.parent().index())

    def mergeWith(self, items, sep="\n\n"):
        """
        Merges item with several other items. Merge is basic, it merges only
        the text.

        @param items: list of `outlineItem`s.
        @param sep: a text added between each item's text.
        """

        # Merges the texts
        text = [self.text()]
        text.extend([i.text() for i in items])
        self.setData(self.enum.text, sep.join(text))

        # Removes other items
        self._model.removeIndexes([i.index() for i in items])

    #######################################################################
    # Search
    #######################################################################

    def findItemsByPOV(self, POV):
        "Returns a list of IDs of all subitems whose POV is ``POV``."
        lst = []
        if self.POV() == POV:
            lst.append(self.ID())

        for c in self.children():
            lst.extend(c.findItemsByPOV(POV))

        return lst

    def findItemsContaining(self, text, columns, mainWindow=F.mainWindow(), caseSensitive=False, recursive=True):
        """Returns a list if IDs of all subitems
        containing ``text`` in columns ``columns``
        (being a list of int).
        """
        lst = self.itemContains(text, columns, mainWindow, caseSensitive)

        if recursive:
            for c in self.children():
                lst.extend(c.findItemsContaining(text, columns, mainWindow, caseSensitive))

        return lst

    def itemContains(self, text, columns, mainWindow=F.mainWindow(), caseSensitive=False):
        lst = []
        text = text.lower() if not caseSensitive else text
        for c in columns:
            if c == self.enum.POV and self.POV():
                character = mainWindow.mdlCharacter.getCharacterByID(self.POV())
                if character:
                    searchIn = character.name()
                else:
                    searchIn = ""
                    LOGGER.error("Character POV not found: %s", self.POV())

            elif c == self.enum.status:
                searchIn = mainWindow.mdlStatus.item(F.toInt(self.status()), 0).text()

            elif c == self.enum.label:
                searchIn = mainWindow.mdlLabels.item(F.toInt(self.label()), 0).text()

            else:
                searchIn = self.data(c)

            searchIn = searchIn.lower() if not caseSensitive else searchIn
            if text in searchIn:
                if not self.ID() in lst:
                    lst.append(self.ID())

        return lst

    ###############################################################################
    # REVISIONS
    ###############################################################################

    def revisions(self):
        return self.data(self.enum.revisions)

    def appendRevision(self, ts, text):
        if not self.enum.revisions in self._data:
            self._data[self.enum.revisions] = []

        self._data[self.enum.revisions].append((
            int(ts),
            text))

    def addRevision(self):
        if not settings.revisions["keep"]:
            return

        if not self.enum.text in self._data:
            return

        self.appendRevision(
                time.time(),
                self.text())

        if settings.revisions["smartremove"]:
            self.cleanRevisions()

        self.emitDataChanged([self.enum.revisions])

    def deleteRevision(self, ts):
        self._data[self.enum.revisions] = [r for r in self._data[self.enum.revisions] if r[0] != ts]
        self.emitDataChanged([self.enum.revisions])

    def clearAllRevisions(self):
        self._data[self.enum.revisions] = []
        self.emitDataChanged([self.enum.revisions])

    def cleanRevisions(self):
        "Keep only one some the revisions."
        rev = self.revisions()
        rev2 = []
        now = time.time()

        rule = settings.revisions["rules"]

        revs = {}
        for i in rule:
            revs[i] = []

        for r in rev:
            # Have to put the lambda key otherwise cannot order when one element is None
            for span in sorted(rule, key=lambda x: x if x else 60 * 60 * 24 * 30 * 365):
                if not span or now - r[0] < span:
                    revs[span].append(r)
                    break

        for span in revs:
            sortedRev = sorted(revs[span], key=lambda x: x[0])
            last = None
            for r in sortedRev:
                if not last:
                    rev2.append(r)
                    last = r[0]
                elif r[0] - last >= rule[span]:
                    rev2.append(r)
                    last = r[0]

        if rev2 != rev:
            self._data[self.enum.revisions] = rev2
            self.emitDataChanged([self.enum.revisions])

    #######################################################################
    # XML
    #######################################################################

    # We don't want to write some datas (computed)
    XMLExclude = [enums.Outline.wordCount,
                  enums.Outline.charCount,
                  enums.Outline.goal,
                  enums.Outline.goalPercentage,
                  enums.Outline.revisions]
    # We want to force some data even if they're empty
    XMLForce = [enums.Outline.compile]

    def toXMLProcessItem(self, item):

        # Saving revisions
        rev = self.revisions()
        for r in rev:
            revItem = ET.Element("revision")
            revItem.set("timestamp", str(r[0]))
            revItem.set("text", self.cleanTextForXML(r[1]))
            item.append(revItem)

        return item


    def setFromXMLProcessMore(self, root):

        # If loading from an old file format, convert to md and
        # remove html markup
        if self.type() in ["txt", "t2t"]:
            self.setData(Outline.type, "md")

        elif self.type() == "html":
            self.setData(Outline.type, "md")
            self.setData(Outline.text, HTML2PlainText(self.data(Outline.text)))
            self.setData(Outline.notes, HTML2PlainText(self.data(Outline.notes)))

        # Revisions
        for child in root:
            if child.tag == "revision":
                self.appendRevision(child.attrib["timestamp"], child.attrib["text"])

    #######################################################################
    # Search
    #######################################################################
    def searchModel(self):
        return Model.Outline

    def searchID(self):
        return self.data(Outline.ID)

    def searchTitle(self, column):
        return self.title()

    def searchPath(self, column):
        return [self.translate("Outline")] + self.path().split(' > ') + [self.translate(self.searchColumnLabel(column))]

    def searchData(self, column):
        mainWindow = F.mainWindow()

        searchData = None

        if column == self.enum.POV and self.POV():
            character = mainWindow.mdlCharacter.getCharacterByID(self.POV())
            if character:
                searchData = character.name()

        elif column == self.enum.status:
            searchData = mainWindow.mdlStatus.item(F.toInt(self.status()), 0).text()

        elif column == self.enum.label:
            searchData = mainWindow.mdlLabels.item(F.toInt(self.label()), 0).text()

        else:
            searchData = self.data(column)

        return searchData
