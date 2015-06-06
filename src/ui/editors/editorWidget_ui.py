# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/ui/editors/editorWidget_ui.ui'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_editorWidget_ui(object):
    def setupUi(self, editorWidget_ui):
        editorWidget_ui.setObjectName("editorWidget_ui")
        editorWidget_ui.resize(400, 300)
        self.horizontalLayout = QtWidgets.QHBoxLayout(editorWidget_ui)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.stack = QtWidgets.QStackedWidget(editorWidget_ui)
        self.stack.setObjectName("stack")
        self.scene = QtWidgets.QWidget()
        self.scene.setObjectName("scene")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.scene)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.txtRedacText = customTextEdit(self.scene)
        self.txtRedacText.setObjectName("txtRedacText")
        self.horizontalLayout_2.addWidget(self.txtRedacText)
        self.stack.addWidget(self.scene)
        self.folder = QtWidgets.QWidget()
        self.folder.setObjectName("folder")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.folder)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scroll = QtWidgets.QScrollArea(self.folder)
        self.scroll.setAutoFillBackground(True)
        self.scroll.setWidgetResizable(True)
        self.scroll.setObjectName("scroll")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 396, 296))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scroll.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scroll)
        self.stack.addWidget(self.folder)
        self.horizontalLayout.addWidget(self.stack)

        self.retranslateUi(editorWidget_ui)
        self.stack.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(editorWidget_ui)

    def retranslateUi(self, editorWidget_ui):
        _translate = QtCore.QCoreApplication.translate
        editorWidget_ui.setWindowTitle(_translate("editorWidget_ui", "Form"))

from ui.editors.customTextEdit import customTextEdit
