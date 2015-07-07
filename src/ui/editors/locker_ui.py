# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/ui/editors/locker_ui.ui'
#
# Created: Tue Jul  7 17:57:16 2015
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_locker(object):
    def setupUi(self, locker):
        locker.setObjectName("locker")
        locker.resize(157, 155)
        self.verticalLayout = QtWidgets.QVBoxLayout(locker)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(locker)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.rbtnWordTarget = QtWidgets.QRadioButton(locker)
        self.rbtnWordTarget.setObjectName("rbtnWordTarget")
        self.verticalLayout.addWidget(self.rbtnWordTarget)
        self.rbtnTimeTarget = QtWidgets.QRadioButton(locker)
        self.rbtnTimeTarget.setObjectName("rbtnTimeTarget")
        self.verticalLayout.addWidget(self.rbtnTimeTarget)
        self.spnWordTarget = QtWidgets.QSpinBox(locker)
        self.spnWordTarget.setMinimum(1)
        self.spnWordTarget.setMaximum(99999)
        self.spnWordTarget.setProperty("value", 500)
        self.spnWordTarget.setObjectName("spnWordTarget")
        self.verticalLayout.addWidget(self.spnWordTarget)
        self.spnTimeTarget = QtWidgets.QSpinBox(locker)
        self.spnTimeTarget.setMinimum(1)
        self.spnTimeTarget.setMaximum(9999)
        self.spnTimeTarget.setProperty("value", 5)
        self.spnTimeTarget.setObjectName("spnTimeTarget")
        self.verticalLayout.addWidget(self.spnTimeTarget)
        self.btnLock = QtWidgets.QPushButton(locker)
        self.btnLock.setObjectName("btnLock")
        self.verticalLayout.addWidget(self.btnLock)

        self.retranslateUi(locker)
        QtCore.QMetaObject.connectSlotsByName(locker)

    def retranslateUi(self, locker):
        _translate = QtCore.QCoreApplication.translate
        locker.setWindowTitle(_translate("locker", "Form"))
        self.label.setText(_translate("locker", "Lock screen:"))
        self.rbtnWordTarget.setText(_translate("locker", "Word target"))
        self.rbtnTimeTarget.setText(_translate("locker", "Time target"))
        self.spnWordTarget.setSuffix(_translate("locker", " words"))
        self.spnTimeTarget.setSuffix(_translate("locker", " minutes"))
        self.btnLock.setText(_translate("locker", "Lock !"))

