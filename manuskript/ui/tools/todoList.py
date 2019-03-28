#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import QVariant, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QHeaderView

from manuskript import settings
from manuskript.ui.tools.todo_ui import Ui_TodoList
import re

class todoList(QWidget, Ui_TodoList):
    def __init__(self, mainWindow):
        QWidget.__init__(self)
        self.setupUi(self)
        self.mw = mainWindow

        self.btnFindTodos.clicked.connect(self.findTodos)

        self.tblTodos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)


    def findTodos(self):
        root = self.mw.mdlOutline.rootItem

        def findInText(item, breadcrumbs):
            txt = item.text()

            #I don't like having root in the breadcrumbs
            if item.title() != root.title():
                breadcrumbs.append(item.title())

            #Find all Todo blocks
            lst = re.findall(r"%t [^%]+%", txt)

            #Trim off the metadata
            lst = [(t[2:-1].strip(), breadcrumbs) for t in lst] 

            #Recursive search through the children
            for c in item.children():
                lst += findInText(c, breadcrumbs[:])

            return lst

        lst = findInText(root, [])

        mdl = QStandardItemModel()
        mdl.setHorizontalHeaderLabels([self.tr("Todo"), self.tr("File")])

        for t in lst:
            mdl.appendRow([QStandardItem(t[0]), QStandardItem("/".join(t[1]))])

        self.tblTodos.setModel(mdl)


    def updateSettings(self):
        pass