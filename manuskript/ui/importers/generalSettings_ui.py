# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manuskript/ui/importers/generalSettings_ui.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_generalSettings(object):
    def setupUi(self, generalSettings):
        generalSettings.setObjectName("generalSettings")
        generalSettings.resize(267, 401)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(generalSettings)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.toolBox = QtWidgets.QToolBox(generalSettings)
        self.toolBox.setStyleSheet("QToolBox::tab{\n"
"    background-color: #BBB;\n"
"    padding: 2px;\n"
"    border: none;\n"
"}\n"
"\n"
"QToolBox::tab:selected, QToolBox::tab:hover{\n"
"    background-color:skyblue;\n"
"}")
        self.toolBox.setObjectName("toolBox")
        self.general = QtWidgets.QWidget()
        self.general.setGeometry(QtCore.QRect(0, 0, 267, 378))
        self.general.setObjectName("general")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.general)
        self.verticalLayout_5.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.formLayout_4 = QtWidgets.QFormLayout()
        self.formLayout_4.setRowWrapPolicy(QtWidgets.QFormLayout.WrapLongRows)
        self.formLayout_4.setObjectName("formLayout_4")
        self.chkGeneralSplitScenes = QtWidgets.QCheckBox(self.general)
        self.chkGeneralSplitScenes.setEnabled(False)
        self.chkGeneralSplitScenes.setObjectName("chkGeneralSplitScenes")
        self.formLayout_4.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.chkGeneralSplitScenes)
        self.txtGeneralSplitScenes = QtWidgets.QLineEdit(self.general)
        self.txtGeneralSplitScenes.setEnabled(False)
        self.txtGeneralSplitScenes.setObjectName("txtGeneralSplitScenes")
        self.formLayout_4.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.txtGeneralSplitScenes)
        self.chkGeneralTrimTitles = QtWidgets.QCheckBox(self.general)
        self.chkGeneralTrimTitles.setObjectName("chkGeneralTrimTitles")
        self.formLayout_4.setWidget(3, QtWidgets.QFormLayout.SpanningRole, self.chkGeneralTrimTitles)
        self.treeGeneralParent = QtWidgets.QTreeView(self.general)
        self.treeGeneralParent.setHeaderHidden(True)
        self.treeGeneralParent.setObjectName("treeGeneralParent")
        self.formLayout_4.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.treeGeneralParent)
        self.chkGeneralParent = QtWidgets.QCheckBox(self.general)
        self.chkGeneralParent.setObjectName("chkGeneralParent")
        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.chkGeneralParent)
        self.verticalLayout_5.addLayout(self.formLayout_4)
        self.toolBox.addItem(self.general, "")
        self.verticalLayout_2.addWidget(self.toolBox)

        self.retranslateUi(generalSettings)
        self.toolBox.setCurrentIndex(0)
        self.toolBox.layout().setSpacing(0)
        QtCore.QMetaObject.connectSlotsByName(generalSettings)

    def retranslateUi(self, generalSettings):
        _translate = QtCore.QCoreApplication.translate
        generalSettings.setWindowTitle(_translate("generalSettings", "Form"))
        self.chkGeneralSplitScenes.setText(_translate("generalSettings", "Split scenes at:"))
        self.chkGeneralTrimTitles.setText(_translate("generalSettings", "Trim long titles (> 32 chars)"))
        self.chkGeneralParent.setText(_translate("generalSettings", "Import under:"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.general), _translate("generalSettings", "General"))

