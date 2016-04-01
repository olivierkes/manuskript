# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manuskript/ui/exporters/exporter_ui.ui'
#
# Created by: PyQt5 UI code generator 5.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_exporter(object):
    def setupUi(self, exporter):
        exporter.setObjectName("exporter")
        exporter.resize(792, 502)
        self.verticalLayout = QtWidgets.QVBoxLayout(exporter)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(exporter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.cmbExporters = QtWidgets.QComboBox(exporter)
        self.cmbExporters.setObjectName("cmbExporters")
        self.horizontalLayout.addWidget(self.cmbExporters)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.btnManageExporters = QtWidgets.QPushButton(exporter)
        self.btnManageExporters.setObjectName("btnManageExporters")
        self.horizontalLayout.addWidget(self.btnManageExporters)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.splitter = QtWidgets.QSplitter(exporter)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.grpSettings = QtWidgets.QGroupBox(self.splitter)
        self.grpSettings.setObjectName("grpSettings")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.grpSettings)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.settings = QtWidgets.QWidget(self.grpSettings)
        self.settings.setObjectName("settings")
        self.verticalLayout_3.addWidget(self.settings)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton = QtWidgets.QPushButton(self.grpSettings)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.grpPreviewBefore = QtWidgets.QGroupBox(self.splitter)
        self.grpPreviewBefore.setObjectName("grpPreviewBefore")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.grpPreviewBefore)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.previewBefore = QtWidgets.QWidget(self.grpPreviewBefore)
        self.previewBefore.setObjectName("previewBefore")
        self.verticalLayout_2.addWidget(self.previewBefore)
        self.grpPreviewAfter = QtWidgets.QGroupBox(self.splitter)
        self.grpPreviewAfter.setObjectName("grpPreviewAfter")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.grpPreviewAfter)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.previewAfter = QtWidgets.QWidget(self.grpPreviewAfter)
        self.previewAfter.setObjectName("previewAfter")
        self.verticalLayout_4.addWidget(self.previewAfter)
        self.verticalLayout.addWidget(self.splitter)

        self.retranslateUi(exporter)
        QtCore.QMetaObject.connectSlotsByName(exporter)

    def retranslateUi(self, exporter):
        _translate = QtCore.QCoreApplication.translate
        exporter.setWindowTitle(_translate("exporter", "Export"))
        self.label.setText(_translate("exporter", "Export to:"))
        self.btnManageExporters.setText(_translate("exporter", "Manage exporters"))
        self.grpSettings.setTitle(_translate("exporter", "Settings"))
        self.pushButton.setText(_translate("exporter", "Show Intermediate Preview"))
        self.grpPreviewBefore.setTitle(_translate("exporter", "Preview"))
        self.grpPreviewAfter.setTitle(_translate("exporter", "Preview"))

