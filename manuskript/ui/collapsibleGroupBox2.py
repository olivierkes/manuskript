#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QFrame, QPushButton, QVBoxLayout, QSizePolicy, qApp

from manuskript.functions import lightBlue


class collapsibleGroupBox2(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.frame = QFrame(self)
        self.button = QPushButton("Toggle", self)
        self.button.setCheckable(True)
        self.button.setChecked(True)
        self.switched = False
        self.vPolicy = None
        # self.button.setStyleSheet("background-color: lightBlue;")

        s1 = """
        QPushButton{
            background-color: #BBB;
            border: none;
            padding: 2px;
        }
        QPushButton:checked, QPushButton:hover{
            font-style:italic;
            background-color:lightBlue;
        }"""

        # p = qApp.palette()
        # c = p.color(p.Window)

        s2 = """
        QPushButton{
            background-color: transparent;
            border: none;
            border-top: 1px solid darkgray;
            padding: 4px 0px;
            font-weight: bold;
        }
        QPushButton:hover{
            background-color:#cccccc;
        }
        """

        self.button.setStyleSheet(s2)

    def resizeEvent(self, event):
        if not self.switched:
            self.switchLayout()
        return QWidget.resizeEvent(self, event)

    def switchLayout(self):
        self.frame.setLayout(self.layout())
        self.wLayout = QVBoxLayout(self)
        self.wLayout.setContentsMargins(0, 0, 0, 0)
        self.wLayout.setSpacing(0)
        self.wLayout.addWidget(self.button)
        self.wLayout.addWidget(self.frame)
        self.button.toggled.connect(self.setExpanded)
        self.frame.layout().setContentsMargins(0, 0, 0, 4)
        self.frame.layout().setSpacing(0)
        self.switched = True

        self.vPolicy = self.sizePolicy().verticalPolicy()
        self.parent().layout().setAlignment(Qt.AlignTop)

        self.setExpanded(self.button.isChecked())

    def setFlat(self, val):
        if val:
            self.frame.setFrameShape(QFrame.NoFrame)

    def setCheckable(self, val):
        pass

    def setTitle(self, title):
        self.button.setText(title)

    def setExpanded(self, val):
        self.frame.setVisible(val)
        if val:
            self.setSizePolicy(QSizePolicy.Preferred, self.vPolicy)
        else:
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

    def saveState(self):
        return self.button.isChecked()

    def restoreState(self, val):
        self.button.setChecked(val)
