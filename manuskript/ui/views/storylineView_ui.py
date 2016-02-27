# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manuskript/ui/views/storylineView_ui.ui'
#
# Created by: PyQt5 UI code generator 5.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_storylineView(object):
    def setupUi(self, storylineView):
        storylineView.setObjectName("storylineView")
        storylineView.resize(1040, 130)
        self.horizontalLayout = QtWidgets.QHBoxLayout(storylineView)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.btnZoomIn = QtWidgets.QPushButton(storylineView)
        self.btnZoomIn.setMaximumSize(QtCore.QSize(32, 32))
        self.btnZoomIn.setFlat(True)
        self.btnZoomIn.setObjectName("btnZoomIn")
        self.verticalLayout.addWidget(self.btnZoomIn)
        self.btnZoomOut = QtWidgets.QPushButton(storylineView)
        self.btnZoomOut.setMaximumSize(QtCore.QSize(32, 32))
        self.btnZoomOut.setFlat(True)
        self.btnZoomOut.setObjectName("btnZoomOut")
        self.verticalLayout.addWidget(self.btnZoomOut)
        self.btnRefresh = QtWidgets.QPushButton(storylineView)
        self.btnRefresh.setMaximumSize(QtCore.QSize(32, 32))
        self.btnRefresh.setText("")
        icon = QtGui.QIcon.fromTheme("view-refresh")
        self.btnRefresh.setIcon(icon)
        self.btnRefresh.setFlat(True)
        self.btnRefresh.setObjectName("btnRefresh")
        self.verticalLayout.addWidget(self.btnRefresh)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.btnSettings = QtWidgets.QPushButton(storylineView)
        self.btnSettings.setMaximumSize(QtCore.QSize(32, 32))
        self.btnSettings.setText("")
        icon = QtGui.QIcon.fromTheme("preferences-system")
        self.btnSettings.setIcon(icon)
        self.btnSettings.setFlat(True)
        self.btnSettings.setObjectName("btnSettings")
        self.verticalLayout.addWidget(self.btnSettings)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.view = QtWidgets.QGraphicsView(storylineView)
        self.view.setObjectName("view")
        self.horizontalLayout.addWidget(self.view)

        self.retranslateUi(storylineView)
        QtCore.QMetaObject.connectSlotsByName(storylineView)

    def retranslateUi(self, storylineView):
        _translate = QtCore.QCoreApplication.translate
        storylineView.setWindowTitle(_translate("storylineView", "Form"))
        self.btnZoomIn.setText(_translate("storylineView", "+"))
        self.btnZoomOut.setText(_translate("storylineView", "-"))

