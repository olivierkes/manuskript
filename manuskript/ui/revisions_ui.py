# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manuskript/ui/revisions_ui.ui'
#
# Created: Mon Oct 16 10:36:02 2017
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_revisions(object):
    def setupUi(self, revisions):
        revisions.setObjectName("revisions")
        revisions.resize(400, 344)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(revisions)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QtWidgets.QSplitter(revisions)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.list = QtWidgets.QListWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list.sizePolicy().hasHeightForWidth())
        self.list.setSizePolicy(sizePolicy)
        self.list.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.list.setObjectName("list")
        self.scrollArea = QtWidgets.QScrollArea(self.splitter)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 400, 68))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
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
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btnOptions = QtWidgets.QPushButton(self.layoutWidget)
        icon = QtGui.QIcon.fromTheme("preferences-system-symbolic")
        self.btnOptions.setIcon(icon)
        self.btnOptions.setFlat(True)
        self.btnOptions.setObjectName("btnOptions")
        self.horizontalLayout_2.addWidget(self.btnOptions)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.btnRestore = QtWidgets.QPushButton(self.layoutWidget)
        icon = QtGui.QIcon.fromTheme("edit-redo")
        self.btnRestore.setIcon(icon)
        self.btnRestore.setFlat(True)
        self.btnRestore.setObjectName("btnRestore")
        self.horizontalLayout_2.addWidget(self.btnRestore)
        self.btnDelete = QtWidgets.QPushButton(self.layoutWidget)
        icon = QtGui.QIcon.fromTheme("edit-delete")
        self.btnDelete.setIcon(icon)
        self.btnDelete.setFlat(True)
        self.btnDelete.setObjectName("btnDelete")
        self.horizontalLayout_2.addWidget(self.btnDelete)
        self.verticalLayout_2.addWidget(self.splitter)

        self.retranslateUi(revisions)
        QtCore.QMetaObject.connectSlotsByName(revisions)

    def retranslateUi(self, revisions):
        _translate = QtCore.QCoreApplication.translate
        revisions.setWindowTitle(_translate("revisions", "Form"))
        self.btnOptions.setText(_translate("revisions", "Options"))
        self.btnRestore.setText(_translate("revisions", "Restore"))
        self.btnDelete.setText(_translate("revisions", "Delete"))

