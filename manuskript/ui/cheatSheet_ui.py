# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manuskript/ui/cheatSheet_ui.ui'
#
# Created: Fri Apr  8 14:27:04 2016
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_cheatSheet(object):
    def setupUi(self, cheatSheet):
        cheatSheet.setObjectName("cheatSheet")
        cheatSheet.resize(400, 344)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(cheatSheet)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.txtFilter = QtWidgets.QLineEdit(cheatSheet)
        self.txtFilter.setStyleSheet("")
        self.txtFilter.setFrame(False)
        self.txtFilter.setClearButtonEnabled(True)
        self.txtFilter.setObjectName("txtFilter")
        self.horizontalLayout.addWidget(self.txtFilter)
        self.btnShowList = QtWidgets.QPushButton(cheatSheet)
        self.btnShowList.setText("")
        icon = QtGui.QIcon.fromTheme("go-bottom")
        self.btnShowList.setIcon(icon)
        self.btnShowList.setCheckable(True)
        self.btnShowList.setFlat(True)
        self.btnShowList.setObjectName("btnShowList")
        self.horizontalLayout.addWidget(self.btnShowList)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.line = QtWidgets.QFrame(cheatSheet)
        self.line.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line.setLineWidth(0)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_2.addWidget(self.line)
        self.splitter = QtWidgets.QSplitter(cheatSheet)
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
        self.scrollArea.setLineWidth(0)
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
        self.view.setLineWidth(0)
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
        self.txtFilter.setPlaceholderText(_translate("cheatSheet", "Filter (type the name of anything in your project)"))

