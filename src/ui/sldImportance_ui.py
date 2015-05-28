# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/ui/sldImportance_ui.ui'
#
# Created: Thu May 28 03:24:08 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_sldImportance(object):
    def setupUi(self, sldImportance):
        sldImportance.setObjectName(_fromUtf8("sldImportance"))
        sldImportance.resize(452, 354)
        self.horizontalLayout = QtGui.QHBoxLayout(sldImportance)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.sld = QtGui.QSlider(sldImportance)
        self.sld.setMinimum(0)
        self.sld.setMaximum(2)
        self.sld.setPageStep(1)
        self.sld.setProperty("value", 0)
        self.sld.setOrientation(QtCore.Qt.Horizontal)
        self.sld.setObjectName(_fromUtf8("sld"))
        self.horizontalLayout.addWidget(self.sld)
        self.lbl = QtGui.QLabel(sldImportance)
        self.lbl.setObjectName(_fromUtf8("lbl"))
        self.horizontalLayout.addWidget(self.lbl)

        self.retranslateUi(sldImportance)
        QtCore.QMetaObject.connectSlotsByName(sldImportance)

    def retranslateUi(self, sldImportance):
        sldImportance.setWindowTitle(_translate("sldImportance", "Form", None))
        self.lbl.setText(_translate("sldImportance", "TextLabel", None))

