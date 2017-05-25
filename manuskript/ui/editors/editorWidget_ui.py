# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manuskript/ui/editors/editorWidget_ui.ui'
#
# Created: Fri Apr  8 20:03:08 2016
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_editorWidget_ui(object):
    def setupUi(self, editorWidget_ui):
        editorWidget_ui.setObjectName("editorWidget_ui")
        editorWidget_ui.resize(400, 300)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(editorWidget_ui)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.stack = QtWidgets.QStackedWidget(editorWidget_ui)
        self.stack.setObjectName("stack")
        self.text = QtWidgets.QWidget()
        self.text.setObjectName("text")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.text)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.txtRedacText = textEditView(self.text)
        self.txtRedacText.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.txtRedacText.setObjectName("txtRedacText")
        self.horizontalLayout_2.addWidget(self.txtRedacText)
        self.stack.addWidget(self.text)
        self.folder = QtWidgets.QWidget()
        self.folder.setObjectName("folder")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.folder)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scroll = QtWidgets.QScrollArea(self.folder)
        self.scroll.setAutoFillBackground(True)
        self.scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll.setWidgetResizable(True)
        self.scroll.setObjectName("scroll")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 400, 300))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scroll.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scroll)
        self.stack.addWidget(self.folder)
        self.cork = QtWidgets.QWidget()
        self.cork.setObjectName("cork")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.cork)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.corkView = corkView(self.cork)
        self.corkView.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.corkView.setObjectName("corkView")
        self.horizontalLayout_3.addWidget(self.corkView)
        self.stack.addWidget(self.cork)
        self.outline = QtWidgets.QWidget()
        self.outline.setObjectName("outline")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.outline)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.outlineView = outlineView(self.outline)
        self.outlineView.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.outlineView.setObjectName("outlineView")
        self.verticalLayout_3.addWidget(self.outlineView)
        self.stack.addWidget(self.outline)
        self.verticalLayout_2.addWidget(self.stack)

        self.retranslateUi(editorWidget_ui)
        self.stack.setCurrentIndex(3)
        QtCore.QMetaObject.connectSlotsByName(editorWidget_ui)

    def retranslateUi(self, editorWidget_ui):
        _translate = QtCore.QCoreApplication.translate
        editorWidget_ui.setWindowTitle(_translate("editorWidget_ui", "Form"))

from manuskript.ui.views.outlineView import outlineView
from manuskript.ui.views.textEditView import textEditView
from manuskript.ui.views.corkView import corkView
