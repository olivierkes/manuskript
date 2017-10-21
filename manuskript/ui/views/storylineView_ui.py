# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manuskript/ui/views/storylineView_ui.ui'
#
# Created: Mon Oct 16 10:05:35 2017
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_storylineView(object):
    def setupUi(self, storylineView):
        storylineView.setObjectName("storylineView")
        storylineView.resize(1040, 130)
        self.horizontalLayout = QtWidgets.QHBoxLayout(storylineView)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.btnRefresh = QtWidgets.QPushButton(storylineView)
        self.btnRefresh.setMaximumSize(QtCore.QSize(32, 32))
        self.btnRefresh.setText("")
        icon = QtGui.QIcon.fromTheme("view-refresh")
        self.btnRefresh.setIcon(icon)
        self.btnRefresh.setFlat(True)
        self.btnRefresh.setObjectName("btnRefresh")
        self.verticalLayout.addWidget(self.btnRefresh)
        self.sldTxtSize = QtWidgets.QSlider(storylineView)
        self.sldTxtSize.setMinimum(1)
        self.sldTxtSize.setMaximum(100)
        self.sldTxtSize.setProperty("value", 20)
        self.sldTxtSize.setOrientation(QtCore.Qt.Vertical)
        self.sldTxtSize.setObjectName("sldTxtSize")
        self.verticalLayout.addWidget(self.sldTxtSize)
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

