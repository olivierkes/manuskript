# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manuskript/ui/search_ui.ui'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_search(object):
    def setupUi(self, search):
        search.setObjectName("search")
        search.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(search)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.text = QtWidgets.QLineEdit(search)
        self.text.setProperty("clearButtonEnabled", True)
        self.text.setObjectName("text")
        self.horizontalLayout.addWidget(self.text)
        self.btnOptions = QtWidgets.QPushButton(search)
        self.btnOptions.setText("")
        icon = QtGui.QIcon.fromTheme("edit-find")
        self.btnOptions.setIcon(icon)
        self.btnOptions.setCheckable(True)
        self.btnOptions.setObjectName("btnOptions")
        self.horizontalLayout.addWidget(self.btnOptions)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.result = QtWidgets.QListWidget(search)
        self.result.setObjectName("result")
        self.verticalLayout.addWidget(self.result)

        self.retranslateUi(search)
        QtCore.QMetaObject.connectSlotsByName(search)

    def retranslateUi(self, search):
        _translate = QtCore.QCoreApplication.translate
        search.setWindowTitle(_translate("search", "Form"))

