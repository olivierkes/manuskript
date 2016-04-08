# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manuskript/ui/editors/textFormat_ui.ui'
#
# Created: Fri Apr  8 18:15:49 2016
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_textFormat(object):
    def setupUi(self, textFormat):
        textFormat.setObjectName("textFormat")
        textFormat.resize(507, 34)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(textFormat)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.format = QtWidgets.QWidget(textFormat)
        self.format.setObjectName("format")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.format)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnBold = QtWidgets.QToolButton(self.format)
        self.btnBold.setText("")
        self.btnBold.setObjectName("btnBold")
        self.horizontalLayout.addWidget(self.btnBold)
        self.btnItalic = QtWidgets.QToolButton(self.format)
        self.btnItalic.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnItalic.setIcon(icon)
        self.btnItalic.setObjectName("btnItalic")
        self.horizontalLayout.addWidget(self.btnItalic)
        self.btnUnderlined = QtWidgets.QToolButton(self.format)
        self.btnUnderlined.setText("")
        self.btnUnderlined.setIcon(icon)
        self.btnUnderlined.setObjectName("btnUnderlined")
        self.horizontalLayout.addWidget(self.btnUnderlined)
        self.btnClear = QtWidgets.QToolButton(self.format)
        self.btnClear.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("../"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnClear.setIcon(icon1)
        self.btnClear.setObjectName("btnClear")
        self.horizontalLayout.addWidget(self.btnClear)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.horizontalLayout_3.addWidget(self.format)
        self.align = QtWidgets.QWidget(textFormat)
        self.align.setObjectName("align")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.align)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.btnLeft = QtWidgets.QToolButton(self.align)
        self.btnLeft.setText("")
        self.btnLeft.setIcon(icon)
        self.btnLeft.setObjectName("btnLeft")
        self.horizontalLayout_2.addWidget(self.btnLeft)
        self.btnCenter = QtWidgets.QToolButton(self.align)
        self.btnCenter.setText("")
        self.btnCenter.setIcon(icon)
        self.btnCenter.setObjectName("btnCenter")
        self.horizontalLayout_2.addWidget(self.btnCenter)
        self.btnRight = QtWidgets.QToolButton(self.align)
        self.btnRight.setText("")
        self.btnRight.setIcon(icon)
        self.btnRight.setObjectName("btnRight")
        self.horizontalLayout_2.addWidget(self.btnRight)
        self.btnJustify = QtWidgets.QToolButton(self.align)
        self.btnJustify.setText("")
        self.btnJustify.setIcon(icon)
        self.btnJustify.setObjectName("btnJustify")
        self.horizontalLayout_2.addWidget(self.btnJustify)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.horizontalLayout_3.addWidget(self.align)

        self.retranslateUi(textFormat)
        QtCore.QMetaObject.connectSlotsByName(textFormat)

    def retranslateUi(self, textFormat):
        _translate = QtCore.QCoreApplication.translate
        textFormat.setWindowTitle(_translate("textFormat", "Form"))

