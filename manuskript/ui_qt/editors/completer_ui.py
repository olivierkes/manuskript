# -*- coding: utf-8 -*-

# Form implementation generated from reading ui_qt file 'manuskript/ui_qt/editors/completer_ui.ui_qt'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets

class Ui_completer(object):
    def setupUi(self, completer):
        completer.setObjectName("completer")
        completer.resize(163, 143)
        self.verticalLayout = QtWidgets.QVBoxLayout(completer)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.text = QtWidgets.QLineEdit(completer)
        self.text.setObjectName("text")
        self.verticalLayout.addWidget(self.text)
        self.list = QtWidgets.QListWidget(completer)
        self.list.setObjectName("list")
        self.verticalLayout.addWidget(self.list)

        self.retranslateUi(completer)
        QtCore.QMetaObject.connectSlotsByName(completer)

    def retranslateUi(self, completer):
        _translate = QtCore.QCoreApplication.translate
        completer.setWindowTitle(_translate("completer", "Form"))

