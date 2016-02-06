# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manuskript/ui/compileDialog_ui.ui'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets

class Ui_compileDialog(object):
    def setupUi(self, compileDialog):
        compileDialog.setObjectName("compileDialog")
        compileDialog.resize(627, 343)
        compileDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(compileDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(compileDialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.cmbTargets = QtWidgets.QComboBox(compileDialog)
        self.cmbTargets.setObjectName("cmbTargets")
        self.horizontalLayout.addWidget(self.cmbTargets)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.wPath = QtWidgets.QWidget(compileDialog)
        self.wPath.setObjectName("wPath")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.wPath)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.wPath)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.txtPath = QtWidgets.QLineEdit(self.wPath)
        self.txtPath.setObjectName("txtPath")
        self.horizontalLayout_3.addWidget(self.txtPath)
        self.btnPath = QtWidgets.QPushButton(self.wPath)
        self.btnPath.setObjectName("btnPath")
        self.horizontalLayout_3.addWidget(self.btnPath)
        self.verticalLayout.addWidget(self.wPath)
        self.wFilename = QtWidgets.QWidget(compileDialog)
        self.wFilename.setObjectName("wFilename")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.wFilename)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_3 = QtWidgets.QLabel(self.wFilename)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)
        self.txtFilename = QtWidgets.QLineEdit(self.wFilename)
        self.txtFilename.setObjectName("txtFilename")
        self.horizontalLayout_4.addWidget(self.txtFilename)
        self.btnFilename = QtWidgets.QPushButton(self.wFilename)
        self.btnFilename.setObjectName("btnFilename")
        self.horizontalLayout_4.addWidget(self.btnFilename)
        self.verticalLayout.addWidget(self.wFilename)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.btnCompile = QtWidgets.QPushButton(compileDialog)
        self.btnCompile.setObjectName("btnCompile")
        self.horizontalLayout_2.addWidget(self.btnCompile)
        self.btnCancel = QtWidgets.QPushButton(compileDialog)
        self.btnCancel.setObjectName("btnCancel")
        self.horizontalLayout_2.addWidget(self.btnCancel)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(compileDialog)
        QtCore.QMetaObject.connectSlotsByName(compileDialog)

    def retranslateUi(self, compileDialog):
        _translate = QtCore.QCoreApplication.translate
        compileDialog.setWindowTitle(_translate("compileDialog", "Dialog"))
        self.label.setText(_translate("compileDialog", "Compile as:"))
        self.label_2.setText(_translate("compileDialog", "Folder:"))
        self.btnPath.setText(_translate("compileDialog", "..."))
        self.label_3.setText(_translate("compileDialog", "File name:"))
        self.btnFilename.setText(_translate("compileDialog", "..."))
        self.btnCompile.setText(_translate("compileDialog", "Compile"))
        self.btnCancel.setText(_translate("compileDialog", "Cancel"))

