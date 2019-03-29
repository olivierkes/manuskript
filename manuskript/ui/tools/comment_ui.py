# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manuskript/ui/tools/comment_ui.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CommentList(object):
    def setupUi(self, CommentList):
        CommentList.setObjectName("CommentList")
        CommentList.resize(733, 453)
        self.verticalLayout = QtWidgets.QVBoxLayout(CommentList)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnFindComments = QtWidgets.QPushButton(CommentList)
        self.btnFindComments.setObjectName("btnFindComments")
        self.horizontalLayout.addWidget(self.btnFindComments)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tblComments = QtWidgets.QTableView(CommentList)
        self.tblComments.setSortingEnabled(True)
        self.tblComments.setObjectName("tblComments")
        self.verticalLayout.addWidget(self.tblComments)

        self.retranslateUi(CommentList)
        QtCore.QMetaObject.connectSlotsByName(CommentList)

    def retranslateUi(self, CommentList):
        _translate = QtCore.QCoreApplication.translate
        CommentList.setWindowTitle(_translate("CommentList", "Comment List"))
        self.btnFindComments.setText(_translate("CommentList", "Find Comments"))

