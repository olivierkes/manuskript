# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manuskript/ui/editors/tabSplitter_ui.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_tabSplitter(object):
    def setupUi(self, tabSplitter):
        tabSplitter.setObjectName("tabSplitter")
        tabSplitter.resize(400, 300)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(tabSplitter.sizePolicy().hasHeightForWidth())
        tabSplitter.setSizePolicy(sizePolicy)
        tabSplitter.setWindowTitle("tabSPlitter")
        self.verticalLayout = QtWidgets.QVBoxLayout(tabSplitter)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter = QtWidgets.QSplitter(tabSplitter)
        self.splitter.setMinimumSize(QtCore.QSize(30, 30))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.tab = QtWidgets.QTabWidget(self.splitter)
        self.tab.setTabsClosable(True)
        self.tab.setMovable(True)
        self.tab.setObjectName("tab")
        self.verticalLayout.addWidget(self.splitter)

        self.retranslateUi(tabSplitter)
        QtCore.QMetaObject.connectSlotsByName(tabSplitter)

    def retranslateUi(self, tabSplitter):
        pass

