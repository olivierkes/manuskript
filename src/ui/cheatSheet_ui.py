# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/ui/cheatSheet_ui.ui'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_cheatSheet(object):
    def setupUi(self, cheatSheet):
        cheatSheet.setObjectName("cheatSheet")
        cheatSheet.resize(400, 344)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(cheatSheet)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.txtFilter = QtWidgets.QLineEdit(cheatSheet)
        self.txtFilter.setProperty("clearButtonEnabled", True)
        self.txtFilter.setObjectName("txtFilter")
        self.verticalLayout_2.addWidget(self.txtFilter)
        self.splitter = QtWidgets.QSplitter(cheatSheet)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.list = QtWidgets.QListWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list.sizePolicy().hasHeightForWidth())
        self.list.setSizePolicy(sizePolicy)
        self.list.setObjectName("list")
        self.scrollArea = QtWidgets.QScrollArea(self.splitter)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 396, 119))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.view = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.view.sizePolicy().hasHeightForWidth())
        self.view.setSizePolicy(sizePolicy)
        self.view.setText("")
        self.view.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.view.setWordWrap(True)
        self.view.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.view.setObjectName("view")
        self.verticalLayout.addWidget(self.view)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_2.addWidget(self.splitter)

        self.retranslateUi(cheatSheet)
        QtCore.QMetaObject.connectSlotsByName(cheatSheet)

    def retranslateUi(self, cheatSheet):
        _translate = QtCore.QCoreApplication.translate
        cheatSheet.setWindowTitle(_translate("cheatSheet", "Form"))
        self.txtFilter.setPlaceholderText(_translate("cheatSheet", "Filter"))

