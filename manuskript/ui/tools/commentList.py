#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import QVariant, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QHeaderView

from manuskript import settings
from manuskript.ui.tools.comment_ui import Ui_CommentList
import re

class commentList(QWidget, Ui_CommentList):
    def __init__(self, mainWindow):
        QWidget.__init__(self)
        self.setupUi(self)
        self.mw = mainWindow

        self.btnFindComments.clicked.connect(self.findComments)

        self.tblComments.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        #Populate the list as soon as you enter the screen
        self.findComments()


    def findComments(self):
        root = self.mw.mdlOutline.rootItem

        def shorten(note):
            maxLen = 75

            note = note.strip()
            if len(note) > maxLen:
                note = note[:maxLen] + "..."
            return note

        def findInText(item, breadcrumbs):
            txt = item.text()

            #I don't like having root in the breadcrumbs
            if item != root:
                breadcrumbs.append(item.title())

            #Find all comment blocks. Using a capture block so the tokens aren't in the find
            lst = re.findall(r"<!--(.*?)-->", txt)

            #Trim off the tokens
            lst = [(shorten(t), breadcrumbs) for t in lst]

            #Recursive search through the children
            for c in item.children():
                lst += findInText(c, breadcrumbs[:])

            return lst

        lst = findInText(root, [])

        mdl = QStandardItemModel()
        mdl.setHorizontalHeaderLabels([self.tr("Comment"), self.tr("File")])

        for t in lst:
            mdl.appendRow([QStandardItem(t[0]), QStandardItem("/".join(t[1]))])

        self.tblComments.setModel(mdl)


    def updateSettings(self):
        pass