# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manuskript/ui/tools/todo_ui.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TodoList(object):
    def setupUi(self, TodoList):
        TodoList.setObjectName("TodoList")
        TodoList.resize(733, 453)
        self.verticalLayout = QtWidgets.QVBoxLayout(TodoList)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.help_label = QtWidgets.QLabel(TodoList)
        self.help_label.setObjectName("help_label")
        self.horizontalLayout.addWidget(self.help_label)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnFindTodos = QtWidgets.QPushButton(TodoList)
        self.btnFindTodos.setObjectName("btnFindTodos")
        self.horizontalLayout.addWidget(self.btnFindTodos)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tblTodos = QtWidgets.QTableView(TodoList)
        self.tblTodos.setSortingEnabled(True)
        self.tblTodos.setObjectName("tblTodos")
        self.verticalLayout.addWidget(self.tblTodos)

        self.retranslateUi(TodoList)
        QtCore.QMetaObject.connectSlotsByName(TodoList)

    def retranslateUi(self, TodoList):
        _translate = QtCore.QCoreApplication.translate
        TodoList.setWindowTitle(_translate("TodoList", "Todos"))
        self.help_label.setText(_translate("TodoList", "Surround text with %t % to mark a todo."))
        self.btnFindTodos.setText(_translate("TodoList", "Find Todos"))

