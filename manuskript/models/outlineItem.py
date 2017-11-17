#!/usr/bin/env python
# --!-- coding: utf8 --!--

from PyQt5.QtCore import Qt
from manuskript.models.abstractItem import abstractItem
from manuskript import enums
from manuskript.functions import mainWindow, toInt
from manuskript import settings
import time


class outlineItem(abstractItem):

    enum = enums.Outline

    # Used for XML export
    name = "outlineItem"

    def __init__(self, model=None, title="", _type="folder", xml=None, parent=None, ID=None):
        abstractItem.__init__(self, model, title, _type, xml, parent, ID)

        self.defaultTextType = None
        self._data[self.enum.compile] = Qt.Checked

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
        if self._data[self.enum.compile] in ["0", 0]:
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

    #######################################################################
    # Wordcount
    #######################################################################

    def insertChild(self, row, child):
        abstractItem.insertChild(self, row, child)
        self.updateWordCount()

    def removeChild(self, row):
        r = abstractItem.removeChild(self, row)
        # Might be causing segfault when updateWordCount emits dataChanged
        self.updateWordCount(emit=False)
        return r

    def updateWordCount(self, emit=True):
        """Update word count for item and parents.
        If emit is False, no signal is emitted (sometimes cause segfault)"""
        if not self.isFolder():
            setGoal = toInt(self.data(self.enum.setGoal))
            goal = toInt(self.data(self.enum.goal))

            if goal != setGoal:
                self._data[self.enum.goal] = setGoal
            if setGoal:
                wc = toInt(self.data(self.enum.wordCount))
                self.setData(self.enum.goalPercentage, wc / float(setGoal))

        else:
            wc = 0
            for c in self.children():
                wc += toInt(c.data(self.enum.wordCount))
            self._data[self.enum.wordCount] = wc

            setGoal = toInt(self.data(self.enum.setGoal))
            goal = toInt(self.data(self.enum.goal))

            if setGoal:
                if goal != setGoal:
                    self._data[self.enum.goal] = setGoal
                    goal = setGoal
            else:
                goal = 0
                for c in self.children():
                    goal += toInt(c.data(self.enum.goal))
                self._data[self.enum.goal] = goal

            if goal:
                self.setData(self.enum.goalPercentage, wc / float(goal))
            else:
                self.setData(self.enum.goalPercentage, "")

        if emit:
            self.emitDataChanged([self.enum.goal, self.enum.setGoal,
                                  self.enum.wordCount, self.enum.goalPercentage])

        if self.parent():
            self.parent().updateWordCount(emit)

    def stats(self):
        wc = self.data(Outline.wordCount)
        goal = self.data(Outline.goal)
        progress = self.data(Outline.goalPercentage)
        if not wc:
            wc = 0
        if goal:
            return qApp.translate("outlineItem", "{} words / {} ({})").format(
                    locale.format("%d", wc, grouping=True),
                    locale.format("%d", goal, grouping=True),
                    "{}%".format(str(int(progress * 100))))
        else:
            return qApp.translate("outlineItem", "{} words").format(
                    locale.format("%d", wc, grouping=True))

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

    def findItemsContaining(self, text, columns, mainWindow=mainWindow(), caseSensitive=False, recursive=True):
        """Returns a list if IDs of all subitems
        containing ``text`` in columns ``columns``
        (being a list of int).
        """
        lst = self.itemContains(text, columns, mainWindow, caseSensitive)

        if recursive:
            for c in self.children():
                lst.extend(c.findItemsContaining(text, columns, mainWindow, caseSensitive))

        return lst

    def itemContains(self, text, columns, mainWindow=mainWindow(), caseSensitive=False):
        lst = []
        text = text.lower() if not caseSensitive else text
        for c in columns:

            if c == self.enum.POV and self.POV():
                c = mainWindow.mdlCharacter.getCharacterByID(self.POV())
                if c:
                    searchIn = c.name()
                else:
                    searchIn = ""
                    print("Character POV not found:", self.POV())

            elif c == self.enum.status:
                searchIn = mainWindow.mdlStatus.item(toInt(self.status()), 0).text()

            elif c == self.enum.label:
                searchIn = mainWindow.mdlLabels.item(toInt(self.label()), 0).text()

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
                self._data[self.enum.text])

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





