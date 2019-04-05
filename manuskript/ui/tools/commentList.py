#!/usr/bin/env python
# --!-- coding: utf8 --!--

from PyQt5.QtCore import QVariant, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QHeaderView

from manuskript import settings
from manuskript.ui.tools.comment_ui import Ui_CommentList
from manuskript.models import references as Ref

import re

class commentList(QWidget, Ui_CommentList):
    def __init__(self, mainWindow):
        QWidget.__init__(self)
        self.setupUi(self)
        self.mw = mainWindow

        self.btnFindComments.clicked.connect(self.findComments)
        self.tblComments.clicked.connect(self.jumpToComment)

        self.tblComments.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        #Populate the list as soon as you enter the screen
        self.findComments()

    def jumpToComment(self, idx):
        item = self.mdl.itemFromIndex(idx)
        match = self.itemToMatch[id(item)]

        index = self.mw.mdlOutline.indexFromItem(match.container)

        if index.isValid():
            self.mw.tabMain.setCurrentIndex(self.mw.TabRedac)
            self.mw.mainEditor.setCurrentModelIndex(index, newTab=True)
            return True
        else:
            print("Ref not found")
            return False

    def _findInText(item, breadcrumbs, isRoot=False):
        txt = item.text()

        #I don't like having root in the breadcrumbs
        if not isRoot:
            breadcrumbs.append(item.title())

        #Find all comment blocks
        matchIter = re.finditer(r"<!--(.*?)-->", txt)

        lst = []
        for m in matchIter:
            match = commentList._shorten(m.group(0))
            paraCount = commentList._countParagraphs(txt, m.start(0))

            lst.append(_CommentMatch(item, match, breadcrumbs, paraCount))

        #Recursive search through the children
        for c in item.children():
            lst += commentList._findInText(c, breadcrumbs[:])

        return lst

    def _countParagraphs(text, end):
        #Humans typically index from 1
        return text[:end].count("\n") + 1

    def _shorten(note):
        maxLen = 75

        note = note[4:-3].strip()
        if len(note) > maxLen:
            note = note[:maxLen] + "..."
        return note


    def findComments(self):
        root = self.mw.mdlOutline.rootItem

        lst = commentList._findInText(root, [], True)

        self.mdl = QStandardItemModel()
        self.mdl.setHorizontalHeaderLabels([self.tr("Comment"), self.tr("File"), self.tr("Paragraph")])

        self.itemToMatch = {}

        for t in lst:
            textItem = QStandardItem(t.text)
            breadcrumbItem = QStandardItem("/".join(t.breadcrumbs))
            paragraphItem = QStandardItem(str(t.paragraph))

            self.itemToMatch[id(textItem)] = t
            self.itemToMatch[id(breadcrumbItem)] = t
            self.itemToMatch[id(paragraphItem)] = t

            self.mdl.appendRow([textItem, breadcrumbItem, paragraphItem])

        self.tblComments.setModel(self.mdl)


    def updateSettings(self):
        pass

class _CommentMatch():
    def __init__(self, container, text, breadcrumbs, paragraph):
        self.container = container
        self.text = text
        self.breadcrumbs = breadcrumbs
        self.paragraph = paragraph