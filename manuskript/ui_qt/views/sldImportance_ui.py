# -*- coding: utf-8 -*-

# Form implementation generated from reading ui_qt file 'manuskript/ui_qt/views/sldImportance_ui.ui_qt'
#
# Created: Thu Mar  3 18:52:22 2016
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_sldImportance(object):
    def setupUi(self, sldImportance):
        sldImportance.setObjectName("sldImportance")
        sldImportance.resize(452, 354)
        self.horizontalLayout = QtWidgets.QHBoxLayout(sldImportance)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.sld = QtWidgets.QSlider(sldImportance)
        self.sld.setMinimum(0)
        self.sld.setMaximum(2)
        self.sld.setPageStep(1)
        self.sld.setProperty("value", 0)
        self.sld.setOrientation(QtCore.Qt.Horizontal)
        self.sld.setObjectName("sld")
        self.horizontalLayout.addWidget(self.sld)
        self.lbl = QtWidgets.QLabel(sldImportance)
        self.lbl.setObjectName("lbl")
        self.horizontalLayout.addWidget(self.lbl)

        self.retranslateUi(sldImportance)
        QtCore.QMetaObject.connectSlotsByName(sldImportance)

    def retranslateUi(self, sldImportance):
        _translate = QtCore.QCoreApplication.translate
        sldImportance.setWindowTitle(_translate("sldImportance", "Form"))
        self.lbl.setText(_translate("sldImportance", "TextLabel"))

