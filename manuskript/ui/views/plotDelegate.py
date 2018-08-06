#!/usr/bin/env python
# --!-- coding: utf8 --!--

import collections

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QStyledItemDelegate, QLineEdit, QMenu, QAction


class plotDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)

    def sizeHint(self, option, index):
        s = QStyledItemDelegate.sizeHint(self, option, index)
        if s.width() < 200:
            s.setWidth(200)
        return s

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setFrame(False)
        editor.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return editor

    def setEditorData(self, editor, index):
        editor.setText(index.model().data(index))

        self.txt = editor
        self.menu = QMenu(editor)

        plotsTypes = collections.OrderedDict({
            self.tr("General"): [
                self.tr("Promise"),
                self.tr("Problem"),
                self.tr("Progress"),
                self.tr("Resolution")
            ],
            self.tr("Try / Fail"): [
                self.tr("No and"),
                self.tr("Yes but"),
            ],
            self.tr("Freytag's pyramid"): [
                self.tr("Exposition"),
                self.tr("Rising action"),
                self.tr("Climax"),
                self.tr("Falling action"),
                self.tr("Resolution"),
            ],
            self.tr("Three acts"): [
                self.tr("1. Setup"),
                self.tr("1. Inciting event"),
                self.tr("1. Turning point"),
                "---",
                self.tr("2. Choice"),
                self.tr("2. Reversal"),
                self.tr("2. Disaster"),
                "---",
                self.tr("3. Stand up"),
                self.tr("3. Climax"),
                self.tr("3. Ending"),
            ],

            self.tr("Hero's journey"): [
                self.tr("Ordinary world"),
                self.tr("Call to adventure"),
                self.tr("Refusal of the call"),
                self.tr("Meeting with mentor"),
                self.tr("Crossing the Threshold"),
                self.tr("Tests"),
                self.tr("Approach"),
                self.tr("Abyss"),
                self.tr("Reward / Revelation"),
                self.tr("Transformation"),
                self.tr("Atonement"),
                self.tr("Return"),
            ],
        })

        for name in plotsTypes:
            m = QMenu(name, self.menu)

            for sub in plotsTypes[name]:
                if sub == "---":
                    m.addSeparator()
                else:
                    a = QAction(sub, m)
                    a.triggered.connect(self.submit)
                    m.addAction(a)

            self.menu.addMenu(m)

        editor.addAction(QIcon.fromTheme("list-add"), QLineEdit.LeadingPosition).triggered.connect(self.popupMenu)

    def setModelData(self, editor, model, index):
        val = editor.text()
        model.setData(index, val)

    def popupMenu(self):
        act = self.sender()
        self.menu.popup(self.txt.parent().mapToGlobal(self.txt.geometry().bottomLeft()))

    def submit(self):
        act = self.sender()
        self.txt.setText(act.text())
