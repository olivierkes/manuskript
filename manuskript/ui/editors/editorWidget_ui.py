# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manuskript/ui/editors/editorWidget_ui.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
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
        self.textLayout = QtWidgets.QVBoxLayout(self.text)
        self.textLayout.setContentsMargins(0, 0, 0, 0)
        self.textLayout.setSpacing(0)
        self.textLayout.setObjectName("textLayout")
        # Reload banner (hidden by default)
        self.reloadBanner = QtWidgets.QFrame(self.text)
        self.reloadBanner.setObjectName("reloadBanner")
        self.reloadBanner.setStyleSheet(
            "QFrame#reloadBanner {"
            "  background: #e65100; border-bottom: 2px solid #bf360c;"
            "  color: white; font-weight: bold; font-size: 13px;"
            "}"
            "QFrame#reloadBanner QPushButton {"
            "  background: white; color: black; border: none;"
            "  border-radius: 3px; padding: 4px 12px;"
            "}"
            "QFrame#reloadBanner QPushButton:hover { background: #fff3e0; }"
        )
        self.reloadBanner.setFixedHeight(44)
        self.reloadBanner.hide()
        self.reloadBannerLayout = QtWidgets.QHBoxLayout(self.reloadBanner)
        self.reloadBannerLayout.setContentsMargins(16, 6, 16, 6)
        self.reloadBannerLabel = QtWidgets.QLabel(self.reloadBanner)
        self.reloadBannerLabel.setText("")
        self.reloadBannerLayout.addWidget(self.reloadBannerLabel)
        self.reloadBannerLayout.addStretch()
        self.reloadBannerBtn = QtWidgets.QPushButton("", self.reloadBanner)
        self.reloadBannerBtn.setFixedWidth(110)
        self.reloadBannerLayout.addWidget(self.reloadBannerBtn)
        self.reloadBannerDismiss = QtWidgets.QPushButton("", self.reloadBanner)
        self.reloadBannerDismiss.setFixedWidth(80)
        self.reloadBannerLayout.addWidget(self.reloadBannerDismiss)
        self.textLayout.addWidget(self.reloadBanner)
        # Editor
        self.txtRedacText = MDEditView(self.text)
        self.txtRedacText.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.txtRedacText.setObjectName("txtRedacText")
        self.textLayout.addWidget(self.txtRedacText)
        self.stack.addWidget(self.text)
        self.folder = QtWidgets.QWidget()
        self.folder.setObjectName("folder")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.folder)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
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
        self.reloadBannerLabel.setText(_translate("editorWidget_ui", "This file has been modified outside Manuskript."))
        self.reloadBannerBtn.setText(_translate("editorWidget_ui", "Reload"))
        self.reloadBannerDismiss.setText(_translate("editorWidget_ui", "Dismiss"))

from manuskript.ui.views.MDEditView import MDEditView
from manuskript.ui.views.corkView import corkView
from manuskript.ui.views.outlineView import outlineView
